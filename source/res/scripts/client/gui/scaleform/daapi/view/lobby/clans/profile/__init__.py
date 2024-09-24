# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/__init__.py
from gui.shared.utils.functions import getArenaGeometryName
from gui.impl import backport
from gui.impl.gen import R
MAX_MEMBERS_IN_CLAN = 100

def getI18ArenaById(arenaId):
    mapName = getArenaGeometryName(arenaId)
    dynAccessor = R.strings.arenas.dyn('c_{}'.format(mapName))
    return backport.text(dynAccessor.name()) if dynAccessor.isValid() else mapName
