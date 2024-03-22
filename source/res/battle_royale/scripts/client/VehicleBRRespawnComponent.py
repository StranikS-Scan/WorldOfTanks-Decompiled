# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleBRRespawnComponent.py
import logging
import BigWorld
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class VehicleBRRespawnComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        if not self.checkCurrentVehicel():
            return
        else:
            self.componentChanged()
            prevLives = self.lives if self.resurrectTime or self.teammateResurrectTime else None
            self.__updateLives(self.lives, prevLives)
            self.__updateResurectTime(self.resurrectTime)
            self.__updateTeammateResurectTime(self.teammateResurrectTime)
            self.__updateTimeBlockToRessurect()
            return

    def set_resurrectTime(self, prev):
        if self.checkCurrentVehicel():
            self.__updateResurectTime(self.resurrectTime)

    def componentChanged(self):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        spawnCtrl.componentChanged()

    def __updateResurectTime(self, resurrectTime):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        respawnTime = int(resurrectTime - BigWorld.serverTime()) if resurrectTime else 0
        spawnCtrl.updateRespawnTimer(respawnTime)

    def __updateTeammateResurectTime(self, teammateResurrectTime):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        respawnTime = int(teammateResurrectTime - BigWorld.serverTime()) if teammateResurrectTime else 0
        spawnCtrl.updateTeammateRespawnTime(respawnTime)

    def __updateTimeBlockToRessurect(self):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        blockTime = int(self.timeBlockToRessurect - BigWorld.serverTime()) if self.timeBlockToRessurect else 0
        spawnCtrl.updateBlockToRessurecTimer(blockTime)

    def checkCurrentVehicel(self):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        isObserver = 'observer' in vehicle.typeDescriptor.type.tags if vehicle else False
        return self.entity.id == BigWorld.player().playerVehicleID or isObserver

    def set_teammateResurrectTime(self, prev):
        if self.checkCurrentVehicel():
            self.__updateTeammateResurectTime(self.teammateResurrectTime)
            _logger.info('set_teammateResurrectTime %s', self.teammateResurrectTime)

    def set_timeBlockToRessurect(self, prev):
        if self.checkCurrentVehicel():
            self.__updateTimeBlockToRessurect()
            _logger.info('set_timeBlockToRessurect %s', self.timeBlockToRessurect)

    def set_lives(self, prev):
        self.__updateLives(self.lives, prev)
        _logger.info('set_lives %s, %s', self.lives, prev)

    def __updateLives(self, lives, prev):
        ctrl = self.sessionProvider.dynamic.vehicleCount
        if ctrl:
            ctrl.updateLives(lives)
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.updateLives(lives, prev)
