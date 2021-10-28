# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/appearance_cache_ctrls/event_appearance_cache_ctrl.py
import logging
import BigWorld
from gui.battle_control.controllers.appearance_cache_ctrls.default_appearance_cache_ctrl import DefaultAppearanceCacheController
from helpers import uniprof
from items.vehicles import VehicleDescriptor
from vehicle_outfit.outfit import Outfit
from common_tank_appearance import CommonTankAppearance
from vehicle_systems.camouflages import getOutfitComponent
from vehicle_systems.tankStructure import ModelStates
_logger = logging.getLogger(__name__)

class EventAppearanceCacheController(DefaultAppearanceCacheController):
    DEFAULT_LOD_IDX = 2

    def __init__(self, setup):
        super(EventAppearanceCacheController, self).__init__(setup)
        self._spawnList = set()

    def startControl(self, battleCtx, arenaVisitor):
        super(EventAppearanceCacheController, self).startControl(battleCtx, arenaVisitor)
        self._spawnList = set()

    def stopControl(self):
        super(EventAppearanceCacheController, self).stopControl()
        self._spawnList = set()

    def _addListeners(self):
        avatar = BigWorld.player()
        if hasattr(avatar, 'onSpawnListUpdated'):
            avatar.onSpawnListUpdated += self.updateSpawnList

    def _removeListeners(self):
        avatar = BigWorld.player()
        if hasattr(avatar, 'onSpawnListUpdated'):
            avatar.onSpawnListUpdated -= self.updateSpawnList

    @uniprof.regionDecorator(label='EventAppearanceCacheController.updateSpawnList', scope='wrap')
    def updateSpawnList(self, spawnListData):
        toAdd = spawnListData.difference(self._spawnList)
        toRemove = self._spawnList.difference(spawnListData)
        for data in toAdd:
            vDesc = VehicleDescriptor(compactDescr=data.vehicleCD)
            outfit = Outfit(component=getOutfitComponent(data.outfitCD), vehicleCD=data.vehicleCD)
            prereqs = set(CommonTankAppearance.collectPrerequisitesForEventBattle(vDesc, outfit, BigWorld.player().spaceID, False, ModelStates.UNDAMAGED))
            self._appearanceCache.loadResources(data.vehicleCD, list(prereqs))

        for data in toRemove:
            self._appearanceCache.unloadResources(data.vehicleCD)

        self._spawnList = spawnListData
        _logger.debug('SpawnList cache updated=%s', spawnListData)
