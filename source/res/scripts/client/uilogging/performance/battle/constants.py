# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/performance/battle/constants.py
from enum import Enum

class Features(str, Enum):
    METRICS = 'battle_metrics'


class Groups(str, Enum):
    SESSION = 'session'
    SYSTEM = 'system'


class LogActions(str, Enum):
    SPACE_DONE = 'space_done'
