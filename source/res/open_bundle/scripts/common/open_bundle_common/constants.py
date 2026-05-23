# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/common/open_bundle_common/constants.py
from __future__ import absolute_import
from datetime import timedelta
OPEN_BUNDLE_GAME_PARAMS_KEY = 'open_bundle_config'
OPEN_BUNDLE_PDATA_KEY = 'openBundle'
MIN_X_COORDINATE = 0
MIN_Y_COORDINATE = 0
MAX_X_COORDINATE = 12
MAX_Y_COORDINATE = 5
OPEN_BUNDLE_MAX_CELLS = (MAX_X_COORDINATE - MIN_X_COORDINATE) * (MAX_Y_COORDINATE - MIN_Y_COORDINATE)
OPEN_BUNDLE_CELL_TAGS = ('rare', 'uniqueNotification')
OPEN_BUNDLE_TEMPLATES = ('S1', 'S2', 'S3', 'S4', 'M1', 'M2', 'L1')
OPEN_BUNDLE_DATA_LIFETIME = timedelta(days=60).total_seconds()
OPEN_BUNDLE_FIXED_REWARD_LOGGING_OFFSET = 1000
