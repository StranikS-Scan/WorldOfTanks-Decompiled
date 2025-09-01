# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMVehicleRespawnComponent.py
import BigWorld
from VehicleRespawnComponent import VehicleRespawnComponent
from aih_constants import CTRL_MODE_NAME

class SMVehicleRespawnComponent(VehicleRespawnComponent):

    def _onVehicleAppeared(self):
        super(SMVehicleRespawnComponent, self)._onVehicleAppeared()
        avatar = BigWorld.player()
        inputHandler = avatar.inputHandler
        if avatar.playerVehicleID == self.entity.id and inputHandler is not None and inputHandler.ctrlModeName != CTRL_MODE_NAME.ARCADE:
            inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE)
        return

    def _explodeVehicleBeforeRespawn(self):
        if self.explodeVehicle:
            super(SMVehicleRespawnComponent, self)._explodeVehicleBeforeRespawn()
