# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleBRRespawnComponent.py
import logging
import BigWorld
import Math
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class VehicleBRRespawnComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        if self.entity.id != BigWorld.player().playerVehicleID:
            return
        else:
            prevLives = self.lives if self.resurrectTime or self.teammateResurrectTime else None
            self.__updateLives(self.lives, prevLives)
            self.__updateResurectTime(self.resurrectTime or self.teammateResurrectTime)
            self.__updatePosition()
            return

    def set_resurrectTime(self, prev):
        if self.entity.id == BigWorld.player().playerVehicleID:
            self.__updateResurectTime(self.resurrectTime)

    def __updateResurectTime(self, resurrectTime):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        respawnTime = int(resurrectTime - BigWorld.serverTime()) if resurrectTime else 0
        spawnCtrl.updateRespawnTimer(respawnTime)

    def __updateTimeBlockToRessurect(self):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        blockTime = int(self.timeBlockToRessurect - BigWorld.serverTime()) if self.timeBlockToRessurect else 0
        spawnCtrl.updateBlockToRessurecTimer(blockTime)

    def set_position(self, prev):
        if self.entity.id == BigWorld.player().playerVehicleID:
            self.__updatePosition()

    def __updatePosition(self):
        if self.resurrectTime and self.position != Math.Vector2(0, 0):
            self.showRespawnPoints()

    def showRespawnPoints(self):
        pass

    def set_teammateResurrectTime(self, prev):
        if self.entity.id == BigWorld.player().playerVehicleID:
            self.__updateResurectTime(self.teammateResurrectTime)
            _logger.debug('set_teammateResurrectTime %s', self.teammateResurrectTime)

    def set_timeBlockToRessurect(self, prev):
        if self.entity.id == BigWorld.player().playerVehicleID:
            self.__updateTimeBlockToRessurect()
            _logger.debug('set_timeBlockToRessurect %s', self.timeBlockToRessurect)

    def set_lives(self, prev):
        self.__updateLives(self.lives, prev)
        _logger.debug('set_lives %s, %s', self.lives, prev)

    def __updateLives(self, lives, prev):
        ctrl = self.sessionProvider.dynamic.vehicleCount
        if ctrl:
            ctrl.updateLives(lives)
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.updateLives(lives, prev)
