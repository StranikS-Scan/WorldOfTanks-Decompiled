# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/constants.py
from enum import Enum
DEFAULT_LOGGER_NAME = 'UI_LOG'

class LogLevels(object):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30


class CommonLogActions(str, Enum):
    CLICK = 'click'
    KEYDOWN = 'keydown'
