# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/hints/battle/newbie.py
import logging
LOGGER_NAME = 'NewbieBattleHints'

def getLogger(*names):
    return logging.getLogger('{}'.format(':'.join((LOGGER_NAME,) + names)))
