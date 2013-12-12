#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from joblib import Memory


JOBLIB_CACHE_DIR = './cache/'
memory = Memory(cachedir=JOBLIB_CACHE_DIR, verbose=True)

LOG = logging.getLogger('antispam')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.WARNING)
