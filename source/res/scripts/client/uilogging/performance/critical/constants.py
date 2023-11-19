# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/performance/critical/constants.py
from enum import Enum

class Features(str, Enum):
    MEMORY_CRITICAL = 'memory_critical'


class Groups(str, Enum):
    EVENT = 'event'


class LogActions(str, Enum):
    MEMORY_CRITICAL_EVENT = 'memory_critical_event'
