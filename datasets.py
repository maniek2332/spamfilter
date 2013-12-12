#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd


TRAIN_SPAM_FILE = 'mail_db/train_spam.txt'
TRAIN_HAM_FILE = 'mail_db/train_ham.txt'
TEST_SPAM_FILE = 'mail_db/test_spam.txt'
TEST_HAM_FILE = 'mail_db/test_ham.txt'

def create_mails_frame(list_file, label=None):
    with open(list_file, 'rb') as fh:
        mails_list = [line.strip() for line in fh]
    mails_frame = pd.DataFrame(index=mails_list,
                               data=mails_list, columns=['filename'])
    if label is not None:
        label_series = pd.Series(index=mails_list, data=label, name='label')
        mails_frame = mails_frame.join(label_series)
    return mails_frame

TRAIN_SPAM = create_mails_frame(TRAIN_SPAM_FILE, 1)
TRAIN_HAM = create_mails_frame(TRAIN_HAM_FILE, 0)
TRAIN_ALL = pd.concat([TRAIN_SPAM, TRAIN_HAM])
