# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/performance/hangar/constants.py
from enum import Enum

class Features(str, Enum):
    METRICS = 'hangar_metrics'


class Groups(str, Enum):
    SPACE = 'space'
    VIEWS = 'views'


class LogActions(str, Enum):
    SPACE_DISPOSED = 'space_disposed'
