# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBTacticalMine.py
from battleground.mines_object import loadMines
from BasicMine import BasicMine
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency

class HBTacticalMine(BasicMine):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def _loadGameObject(self):
        arenaType = self.__sessionProvider.arenaVisitor.getArenaGuiType()
        effDescr = self.__dynObjectsCache.getConfig(arenaType).getTacticalMinesEffect()
        return loadMines(self.ownerVehicleID, self._registerGameObject, effDescr=effDescr)
