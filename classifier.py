#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, roc_curve
#from sklearn.linear_model import LogisticRegression
#from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn_pandas import cross_val_score
from matplotlib import pyplot as plt

from features import FeaturesExtractor
from mail_parser import parse_mails
from datasets import TRAIN_ALL, TEST_ALL


class AntispamModel(object):
    def __init__(self, classifier):
        self.classifier = classifier
        self.features_extractor = FeaturesExtractor()

        self.spam_filter = Pipeline([
            ('features', self.features_extractor),
            ('classifier', self.classifier),
        ])

    def train(self, train_data, labels):
        self.spam_filter.fit(train_data, labels)

    def test(self, test_data, real_labels):
        y_pred = self.spam_filter.predict(test_data)
        y_true = real_labels
        return f1_score(y_true, y_pred)

    def cv_score(self, train_data, labels):
        return cross_val_score(self.spam_filter, train_data, labels,
                               score_func=f1_score)

    def plot_roc_curve(self, test_data, real_labels):
        proba = self.spam_filter.predict_proba(test_data)[:, 1]
        fpr, tpr, thresholds = roc_curve(real_labels, proba)
        plt.plot(fpr, tpr, c='black', lw=3.0)
        plt.plot((0, 1), (0, 1), '--', c='black')
        plt.xlim(0, 1.0)
        plt.ylim(0, 1.0)
        plt.show()


if __name__ == '__main__':
    train_mails = parse_mails(TRAIN_ALL['filename'])
    #clf = LogisticRegression()
    #clf = RandomForestClassifier()
    clf = SVC(probability=True)
    model = AntispamModel(clf)
    model.train(train_mails, TRAIN_ALL['label'])
    test_mails = parse_mails(TEST_ALL['filename'])
    model.plot_roc_curve(test_mails, TEST_ALL['label'])
    #print model.test(test_mails, TEST_ALL['label'])
    #print model.cv_score(train_mails, TRAIN_ALL['label'])

