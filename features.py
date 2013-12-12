#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from mail_parser import parse_mails
from utils import memory
from datasets import TRAIN_ALL


class FeaturesExtractor(object):
    def __init__(self):
        self._parse_mails = memory.cache(self._parse_mails,
                                         ignore=('self',))
        self._extract_features = memory.cache(self._extract_features,
                                              ignore=('self',))

        self.text_vectorizer = None
        self.subject_vectorizer = None

    def vectorize_text(self, mails, fit=False):
        if fit:
            self.text_vectorizer = TfidfVectorizer(max_features=1000)
            self.text_vectorizer.fit(mails['plain_body'])
        features = pd.DataFrame(
            index=mails.index,
            data=self.text_vectorizer.transform(mails['plain_body']).todense()
        )
        return features

    def _extract(self, mails_data, fit):
        features = self._vectorize_text(mails_data, fit)
        return features

    def extract(self, mails_data):
        assert self.text_vectorizer is not None
        return self._extract(mails_data, False)

    def fit_extract(self, mails_data):
        return self._extract(mails_data, True)


if __name__ == '__main__':
    mails_data = parse_mails(TRAIN_ALL['filename'])
    fext = FeaturesExtractor(mails_data)
    #print len(fext.extract())
    fext.extract()
