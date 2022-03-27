# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: rts/scripts/client/RTSSpawnKeyPointAvatar.py
import typing
import BigWorld
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui.battle_control import event_dispatcher
from shared_utils import nextTick
from AvatarInputHandler.control_modes import ArcadeControlMode
from functools import partial
if typing.TYPE_CHECKING:
    from typing import List, Dict, Union

class RTSSpawnKeyPointAvatar(BigWorld.DynamicScriptComponent):

    def receiveAvailableSpawnKeyPointsWithVehicleTypes(self, points):
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.updateAvailablePoints(points)

    def receiveTeamSpawnKeyPoints(self, chosenPoints, unsuitablePoints):
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.updatePoints(chosenPoints, unsuitablePoints)

    def setClientFilters(self, val):
        playerVehicleID = getattr(self, 'playerVehicleID', None)
        if playerVehicleID is None:
            return
        else:
            vehicle = BigWorld.entity(playerVehicleID)
            if vehicle is not None and vehicle.filter is not None:
                vehicle.filter.enableClientFilters = val
            return

    def closeChooseSpawnKeyPointsWindow(self):
        self.setClientFilters(False)
        LOG_WARNING('closeChooseSpawnKeyPointsWindow')
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.closeSpawnPoints()
        if self.entity.getVehicleAttached() is not None:
            controlMode = self.entity.inputHandler.ctrl
            if isinstance(controlMode, ArcadeControlMode):
                camera = self.entity.inputHandler.ctrl.camera
                nextTick(camera.setToVehicleDirection)()
        BigWorld.callback(15, partial(self.setClientFilters, True))
        return
