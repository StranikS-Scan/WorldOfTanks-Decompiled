# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/common/fun_random_common/fun_constants.py
from constants import IS_DEVELOPMENT
DEFAULT_ASSETS_PACK = 'undefined'
DEFAULT_SETTINGS_KEY = 'undefined'
DEFAULT_PRIORITY = 0
FUN_EVENT_ID_KEY = 'funEventID'
UNKNOWN_EVENT_ID = 0
UNKNOWN_EVENT_NAME = 'unknown_event'
UNKNOWN_WWISE_REMAPPING = 'unknownRemapping'

class FunSubModeImpl(object):
    DEV_TEST = 0
    DEFAULT = 1
    NEW_YEAR = 2
    ALL = (DEFAULT, NEW_YEAR) + ((DEV_TEST,) if IS_DEVELOPMENT else ())


class FunProgressionCondition(object):
    BATTLES = 'battles'
    TOP = 'top'
    WIN = 'win'
    ALL = (BATTLES, TOP, WIN)
