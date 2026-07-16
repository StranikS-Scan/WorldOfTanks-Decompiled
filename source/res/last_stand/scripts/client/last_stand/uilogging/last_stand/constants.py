# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/uilogging/last_stand/constants.py
from __future__ import absolute_import
from enum import Enum
FEATURE = 'ls_narration'
START_MARKER_KEY = 'start'
END_MARKER_KEY = 'end'
NARRATION_PREFIX = '#ev_last_stand_quantum'

class NarrationLogAction(Enum):
    START = 'start'
    END = 'end'
