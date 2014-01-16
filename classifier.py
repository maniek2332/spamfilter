#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
#from sklearn.grid_search import GridSearchCV
from sklearn.metrics import f1_score, roc_curve, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn_pandas import cross_val_score, GridSearchCV
from matplotlib import pyplot as plt

from features import FeaturesExtractor
from mail_parser import parse_mails, parse_mail_string
from datasets import TRAIN_ALL, TEST_ALL, COMPLETE_ALL
from utils import linestyles_gen


class Score(object):
    def __init__(self, thresholds, fpr, tpr, auc):
        self.thresholds = thresholds
        self.fpr = fpr
        self.tpr = tpr
        self.auc = auc

    def interpolate(self, target_thresholds):
        return Score(
            target_thresholds,
            np.interp(target_thresholds, self.thresholds, self.fpr),
            np.interp(target_thresholds, self.thresholds, self.tpr),
            self.auc)

    def plot(self, label=None, lc='black', ls='-', fill_alpha=0.1):
        plt.plot(self.fpr, self.tpr, color=lc, label=label,
                 ls=ls, lw=1.8, alpha=0.6)
        plt.fill_between(self.fpr, self.tpr, alpha=fill_alpha)


def scores_mean(scores):
    thresholds = scores[0].thresholds
    assert all([thresholds == s.thresholds for s in scores[2:]])

    m_fpr = np.vstack([s.fpr for s in scores]).mean(0)
    m_tpr = np.vstack([s.tpr for s in scores]).mean(0)
    m_auc = np.vstack([s.auc for s in scores]).mean(0)

    return Score(thresholds, m_fpr, m_tpr, m_auc)


class ROCScorer(object):
    def __init__(self, params_names):
        self.params_names = params_names
        self.scores = defaultdict(list)
        self.interp_thresholds = set()

    @property
    def interp_scores(self):
        i_scores = {}
        interp_thresholds = sorted(self.interp_thresholds)
        for params, scores in self.scores.items():
            full_params_name = self._get_full_params_name(params)
            scores = [s.interpolate(interp_thresholds) for s in scores]
            i_scores[full_params_name] = scores_mean(scores)
        return i_scores

    def _get_full_params_name(self, params):
        full_params_list = ["%s=%r" % (n.split('__')[-1], v)
                            for n, v in zip(self.params_names, params)]
        return ", ".join(full_params_list)

    def _get_estimator_params(self, estimator):
        all_params = estimator.get_params()
        return tuple(all_params[p] for p in self.params_names)

    def __call__(self, estimator, X, y):
        proba = estimator.predict_proba(X)[:, 1]
        fpr, tpr, thresholds = roc_curve(y, proba)
        fpr, tpr, thresholds = fpr[::-1], tpr[::-1], thresholds[::-1]
        self.interp_thresholds |= set(thresholds.tolist())
        auc = roc_auc_score(y, proba)

        score = Score(thresholds, fpr, tpr, auc)
        params = self._get_estimator_params(estimator)
        self.scores[params].append(score)

        return auc


class AntispamModel(object):
    def __init__(self, classifier):
        self.classifier = classifier
        self.features_extractor = FeaturesExtractor()

        self.spam_filter = Pipeline([
            ('features', self.features_extractor),
            ('minmax', MinMaxScaler()),
            ('classifier', self.classifier),
        ])

    def train(self, train_data, labels):
        self.spam_filter.fit(train_data, labels)

    def accuracy(self, test_data, real_labels):
        return self.spam_filter.score(test_data, real_labels)

    def test(self, test_data, real_labels):
        y_pred = self.spam_filter.predict(test_data)
        y_true = real_labels
        return f1_score(y_true, y_pred)

    def cv_score(self, train_data, labels):
        return cross_val_score(self.spam_filter, train_data, labels,
                               score_func=f1_score)

    def predict_single(self, mail_content):
        data = parse_mail_string(mail_content)
        return self.spam_filter.predict(data)[0]

    def plot_roc_curve(self, test_data, real_labels):
        proba = self.spam_filter.predict_proba(test_data)[:, 1]
        fpr, tpr, thresholds = roc_curve(real_labels, proba)
        plt.plot(fpr, tpr, c='black', lw=3.0)
        plt.fill_between(fpr, tpr, alpha=0.1)
        plt.plot((0, 1), (0, 1), '--', c='black')
        plt.xlim(0, 1.0)
        plt.ylim(0, 1.0)
        plt.show()


def print_scores_table(grid_scores):
    grid_scores.sort(key=lambda s: s.mean_validation_score)
    for s in grid_scores:
        params_str = ", ".join(
            ["%s=%g" % (k.split('__')[-1], v)
             for k, v in s.parameters.items()]
        )
        mean = s.cv_validation_scores.mean()
        std = s.cv_validation_scores.std()

        print "%-35s %-20.5f %-22.5f" % (params_str, mean, std)


def logistic_regression():
    train_mails = parse_mails(TRAIN_ALL['filename'])
    clf = LogisticRegression()
    model = AntispamModel(clf)
    model.train(train_mails, TRAIN_ALL['label'])
    test_mails = parse_mails(TEST_ALL['filename'])
    model.plot_roc_curve(test_mails, TEST_ALL['label'])


def grid_test(clf, params, n_folds=5, filepath=None,
              extra_params={}):
    train_mails = parse_mails(COMPLETE_ALL['filename'])
    train_labels = COMPLETE_ALL['label']
    model = AntispamModel(clf)
    model.spam_filter.set_params(**extra_params)
    scorer = ROCScorer(params.keys())
    cv = StratifiedKFold(train_labels, n_folds)
    grid_search = GridSearchCV(
        model.spam_filter, params, scoring=scorer,
        n_jobs=1, cv=cv, refit=False, verbose=2
    )
    grid_search.fit(train_mails, train_labels)

    print_scores_table(grid_search.grid_scores_)

    plt.figure(figsize=(8, 12))
    interp_scores = scorer.interp_scores.items()
    interp_scores.sort(key=lambda x: x[1].auc)
    scores_count = len(interp_scores)

    for (params, score), (ls, lc) in zip(interp_scores, linestyles_gen()):
        label = "%s (AUC: %.5f)" % (params, score.auc)
        plt.subplot(2, 1, 1)
        score.plot(label=label, lc=lc, ls=ls, fill_alpha=0.5 / scores_count)
        plt.subplot(2, 1, 2)
        score.plot(label=label, lc=lc, ls=ls, fill_alpha=0.5 / scores_count)
    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.legend(loc='lower right', fontsize='medium')
    plt.gca().add_patch(
        plt.Rectangle((0, 0.8), 0.2, 0.2, ls='dashed', fc='none')
    )
    plt.xlim(-0.05, 1)
    plt.ylim(0, 1.05)
    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.xlim(0, 0.2)
    plt.ylim(0.8, 1)
    if filepath:
        plt.savefig(filepath)
    plt.show()
    return grid_search


def text_vectorizer_grid():
    clf = LogisticRegression()
    params = {
        'features__subject_words': [10, 100, 300],
        'features__text_words': [500, 1000, 2000, 3000],
    }
    return grid_test(clf, params,
                     filepath='doc/charts/ROC_TextVectorizer.png')


def logistic_regression_grid():
    clf = LogisticRegression()
    params = {'classifier__C': [0.1, 0.5, 1.0, 1.5, 3.5, 5.0, 7.5]}
    return grid_test(clf, params,
                     filepath='doc/charts/ROC_LogisticRegression.png')


def naive_bayes_grid():
    clf = MultinomialNB()
    params = {'classifier__alpha': [0.001, 0.01, 0.1, 0.5, 1.0]}
    return grid_test(clf, params,
                     filepath='doc/charts/ROC_NaiveBayes.png')


def svm_grid():
    clf = SVC(probability=True, kernel='rbf')
    params = {
        'classifier__C': [0.1, 0.5, 1.0, 1.5, 3.5],
        'classifier__gamma': [0.1, 0.01],
    }
    return grid_test(clf, params, 3,
                     filepath='doc/charts/ROC_SVM-rbf.png',
                     extra_params={
                         'features__subject_words': 50,
                         'features__text_words': 500
                     })


def linear_svm_grid():
    clf = SVC(probability=True, kernel='linear')
    params = {'classifier__C': [0.1, 0.5, 1.0, 1.5, 3.5]}
    return grid_test(clf, params, 3,
                     filepath='doc/charts/ROC_SVM-linear.png',
                     extra_params={
                         'features__subject_words': 50,
                         'features__text_words': 500
                     })


def forest_grid():
    clf = RandomForestClassifier()
    params = {'classifier__n_estimators': [10, 30, 50, 75, 100]}
    return grid_test(clf, params, 5,
                     filepath='doc/charts/ROC_RandomForest.png')


def classifiers_comparison():
    classifiers = [
        (LogisticRegression(C=5.0), "Regresja logistyczna"),
        (MultinomialNB(alpha=0.1), "Naiwny klas. bayesowski"),
        (SVC(kernel='linear', probability=True,
             C=3.5, gamma=0.1), "SVM (liniowy)"),
        (SVC(kernel='rbf', probability=True, C=0.5), "SVM (RBF)"),
        (RandomForestClassifier(n_estimators=100), "Las drzew losowych"),
    ]

    clf_count = len(classifiers)

    train_mails = parse_mails(COMPLETE_ALL['filename'])
    train_labels = COMPLETE_ALL['label']
    plt.figure(figsize=(8, 12))
    for (clf, clf_name), (ls, lc) in zip(classifiers, linestyles_gen()):
        model = AntispamModel(clf)
        cv = StratifiedKFold(train_labels, 3)
        scorer = ROCScorer(model.spam_filter.get_params().keys())
        cross_val_score(model.spam_filter, train_mails, train_labels,
                        cv=cv, scoring=scorer, verbose=2)
        score = scorer.interp_scores.values()[0]
        label = clf_name
        plt.subplot(2, 1, 1)
        score.plot(label=label, lc=lc, ls=ls, fill_alpha=0.5 / clf_count)
        plt.subplot(2, 1, 2)
        score.plot(label=label, lc=lc, ls=ls, fill_alpha=0.5 / clf_count)
    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.legend(loc='lower right', fontsize='medium')
    plt.gca().add_patch(
        plt.Rectangle((0, 0.8), 0.2, 0.2, ls='dashed', fc='none')
    )
    plt.xlim(-0.05, 1)
    plt.ylim(0, 1.05)
    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.xlim(0, 0.2)
    plt.ylim(0.8, 1)
    plt.savefig('doc/charts/ROC_ALL.png')
    plt.show()



def roc_model_score(model, train_data, train_labels,
                    test_data, test_labels):
    model.train(train_data, train_labels)
    estimator_name = model.classifier.__class__.__name__
    print "Estimator: %s" % estimator_name
    proba = model.spam_filter.predict_proba(test_data)[:, 1]
    fpr, tpr, thresholds = roc_curve(test_labels, proba)
    auc = roc_auc_score(test_labels, proba)
    print "Accuracy: %.4f" % model.accuracy(test_data, test_labels)
    print "AUC: %.4f" % auc

    plt.fill_between(fpr, tpr, alpha=0.3)
    plt.title(estimator_name)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.savefig('doc/charts/ROC_%s.png' % estimator_name)
    plt.show()
    return estimator_name, tpr, fpr


def roc_model_score_all():
    classifiers = (
        LogisticRegression(),
        SVC(probability=True, verbose=2),
        MultinomialNB(),
        RandomForestClassifier(),
    )
    colors = ('blue', 'red', 'green', 'black')
    plot_data = []

    train_mails = parse_mails(TRAIN_ALL['filename'])
    train_labels = TRAIN_ALL['label']
    test_mails = parse_mails(TEST_ALL['filename'])
    test_labels = TEST_ALL['label']
    for clf in classifiers:
        model = AntispamModel(clf)
        ret = roc_model_score(model, train_mails, train_labels,
                              test_mails, test_labels)
        plot_data.append(ret)

    for (estimator_name, tpr, fpr), color in zip(plot_data, colors):
        plt.plot(fpr, tpr, lw=2, color=color, label=estimator_name)
        plt.fill_between(fpr, tpr, alpha=0.1)
    plt.legend(loc='lower right')
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.savefig('doc/charts/ROC_ALL.png')
    plt.show()


def prepare_model():
    print "Preparing model..."
    clf = LogisticRegression()
    model = AntispamModel(clf)
    train_mails = parse_mails(TRAIN_ALL['filename'])
    train_labels = TRAIN_ALL['label']
    model.train(train_mails, train_labels)
    print "Model ready!"
    return model


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Argument required"
        sys.exit(1)
    elif sys.argv[1] == 'logistic_regression_grid':
        grid_search = logistic_regression_grid()
    elif sys.argv[1] == 'naive_bayes_grid':
        grid_search = naive_bayes_grid()
    elif sys.argv[1] == 'svm_grid':
        grid_search = svm_grid()
    elif sys.argv[1] == 'linear_svm_grid':
        grid_search = linear_svm_grid()
    elif sys.argv[1] == 'forest_grid':
        grid_search = forest_grid()
    elif sys.argv[1] == 'text_vectorizer_grid':
        grid_search = text_vectorizer_grid()
    elif sys.argv[1] == 'classifiers_comparison':
        classifiers_comparison()
    else:
        print >> sys.stderr, "Unknown option: %s" % sys.argv[1]
