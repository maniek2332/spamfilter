#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from datasets import TRAIN_ALL, TEST_ALL
from utils import linestyles_gen, colors_gen


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

    def plot(self, color='black', label=None, ls='-'):
        plt.plot(self.fpr, self.tpr, color=color, label=label, ls=ls, lw=1)
        plt.fill_between(self.fpr, self.tpr, alpha=0.1)


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


def logistic_regression():
    train_mails = parse_mails(TRAIN_ALL['filename'])
    clf = LogisticRegression()
    model = AntispamModel(clf)
    model.train(train_mails, TRAIN_ALL['label'])
    test_mails = parse_mails(TEST_ALL['filename'])
    model.plot_roc_curve(test_mails, TEST_ALL['label'])


def logistic_regression_grid():
    params = {'classifier__C': [0.1, 0.5, 1.0, 1.5, 3.5]}
    train_mails = parse_mails(TRAIN_ALL['filename'])
    train_labels = TRAIN_ALL['label']
    clf = LogisticRegression()
    model = AntispamModel(clf)
    scorer = ROCScorer(params.keys())
    cv = StratifiedKFold(train_labels, 5)
    grid_search = GridSearchCV(
        model.spam_filter, params, scoring='f1',
        n_jobs=1, cv=cv, refit=False, verbose=True
    )
    grid_search.fit(train_mails, train_labels)
    print grid_search.best_score_
    print grid_search.best_params_
    print grid_search.grid_scores_

    for (params, score), color in zip(scorer.interp_scores.items(),
                                      colors_gen()):
        label = "%s (AUC: %.4f)" % (params, score.auc)
        score.plot(label=params, color=color)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.legend(loc='best')
    plt.show()
    return grid_search


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
    plt.legend(loc='best')
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
    #roc_model_score_all()
    grid_search = logistic_regression_grid()
    #train_mails = parse_mails(TRAIN_ALL['filename'])
    ##clf = LogisticRegression()
    ##clf = RandomForestClassifier()
    #clf = SVC(probability=True)
    #model = AntispamModel(clf)
    #model.train(train_mails, TRAIN_ALL['label'])
    #test_mails = parse_mails(TEST_ALL['filename'])
    #model.plot_roc_curve(test_mails, TEST_ALL['label'])
    ##print model.test(test_mails, TEST_ALL['label'])
    ##print model.cv_score(train_mails, TRAIN_ALL['label'])

