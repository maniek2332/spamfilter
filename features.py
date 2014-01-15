#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn_pandas import DataFrameMapper, DataWrapper
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from mail_parser import parse_mails
from datasets import TRAIN_ALL


class FeaturesExtractor(DataFrameMapper):
    def __init__(self, subject_words=300, text_words=2000):
        self.subject_vectorizer = CountVectorizer()
        self.text_vectorizer = TfidfVectorizer()
        self.stub_extractor = StubExtractor()

        self.subject_words = subject_words
        self.text_words = text_words

        self.mapping = (
            ('plain_body', self.text_vectorizer),
            ('h_subject', self.subject_vectorizer),
            (['tags_count', 'errors_count', 'body_length',
              'rel_tags_count', 'rel_errors_count',
              'cov_b', 'cov_i', 'cov_font', 'cov_center',
              'rel_cov_b', 'rel_cov_i', 'rel_cov_font', 'rel_cov_center',
              'http_links', 'http_raw_links', 'mail_links',
              'rel_http_links', 'rel_http_raw_links', 'rel_mail_links',
              'attached_images', 'charset_errors'], self.stub_extractor),
        )

        super(FeaturesExtractor, self).__init__(self.mapping)

    @property
    def subject_words(self):
        return self.subject_vectorizer.max_features

    @subject_words.setter
    def subject_words(self, value):
        self.subject_vectorizer.max_features = value

    @property
    def text_words(self):
        return self.text_vectorizer.max_features

    @text_words.setter
    def text_words(self, value):
        self.text_vectorizer.max_features = value

    # XXX bugfix of converting string columns
    def _get_col_subset(self, X, cols):
        if isinstance(cols, basestring):
            cols = [cols]

        if isinstance(X, list):
            X = [x[cols] for x in X]
            X = pd.DataFrame(X)

        elif isinstance(X, DataWrapper):
            X = X.df

        if len(cols) == 1:
            t = X[cols[0]]
        else:
            t = X.as_matrix(cols)

        if np.all(X.dtypes[cols] == 'object'):
            t = np.array(t, dtype='|U')  # '|U' instead of '|S'

        return t


class StubExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X):
        pass

    def transform(self, X):
        return X


if __name__ == '__main__':
    mails_data = parse_mails(TRAIN_ALL['filename'])
    fext = FeaturesExtractor()
    #print len(fext.extract())
    #fext.extract()
