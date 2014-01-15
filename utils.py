#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from itertools import product

from joblib import Memory


JOBLIB_CACHE_DIR = './cache/'
memory = Memory(cachedir=JOBLIB_CACHE_DIR, verbose=True)

LOG = logging.getLogger('antispam')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.WARNING)

LINESTYLES = ['-', '-.', '--', ':']
COLORS = ['red', 'blue', 'green', 'cyan', 'orange']


def linestyles_gen():
    return product(LINESTYLES, COLORS)
