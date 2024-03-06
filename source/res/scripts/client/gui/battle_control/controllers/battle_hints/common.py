# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/common.py
import logging
from hints_common.battle.schemas.const import MAX_PRIORITY
DEFAULT_LOGGER_NAME = 'BattleHints'
HIGHEST_PRIORITY = MAX_PRIORITY + 1
HIDE_ANIMATION_TIMEOUT = 2.0
QUEUE_HINTS_MAX_SIZE = 200

def getLogger(*names):
    return logging.getLogger('{}'.format(':'.join((DEFAULT_LOGGER_NAME,) + names)))
