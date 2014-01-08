#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from itertools import cycle

from joblib import Memory


JOBLIB_CACHE_DIR = './cache/'
memory = Memory(cachedir=JOBLIB_CACHE_DIR, verbose=True)

LOG = logging.getLogger('antispam')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.WARNING)

LINESTYLES = ['-', '-.', '--', ':']
COLORS = ['red', 'blue', 'green', 'purple']


def linestyles_gen():
    return cycle(LINESTYLES)

def colors_gen():
    return cycle(COLORS)
