#!/bin/bash

find mail_db/spam/* -name '*.*' | sort -R > mail_db/all_spam.txt
find mail_db/easy_ham/* mail_db/hard_ham/* -name '*.*' | sort -R > mail_db/all_ham.txt

SPAM_COUNT=`wc -l < mail_db/all_spam.txt`
HAM_COUNT=`wc -l < mail_db/all_ham.txt`

echo "SPAM_COUNT: $SPAM_COUNT"
echo "HAM_COUNT: $HAM_COUNT"

SPAM_TEST_COUNT=$[SPAM_COUNT * 20 / 100]
HAM_TEST_COUNT=$[HAM_COUNT * 20 / 100]

SPAM_TRAIN_COUNT=$[SPAM_COUNT - SPAM_TEST_COUNT]
HAM_TRAIN_COUNT=$[HAM_COUNT - HAM_TEST_COUNT]

head -n $SPAM_TEST_COUNT mail_db/all_spam.txt > mail_db/test_spam.txt
head -n $HAM_TEST_COUNT mail_db/all_ham.txt > mail_db/test_ham.txt

tail -n $SPAM_TRAIN_COUNT mail_db/all_spam.txt > mail_db/train_spam.txt
tail -n $HAM_TRAIN_COUNT mail_db/all_ham.txt > mail_db/train_ham.txt

wc -l mail_db/all_spam.txt mail_db/train_spam.txt mail_db/test_spam.txt \
      mail_db/all_ham.txt mail_db/train_ham.txt mail_db/test_ham.txt
