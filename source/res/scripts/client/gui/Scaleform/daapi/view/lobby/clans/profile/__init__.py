# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/__init__.py
MAX_MEMBERS_IN_CLAN = 100
from helpers.i18n import makeString as _ms

def getI18ArenaById(arenaName):
    return _ms('#arenas:%s/name' % arenaName)
