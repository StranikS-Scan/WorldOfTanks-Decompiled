# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/SpawnKeyPointAvatar.py
import BigWorld
from debug_utils import LOG_WARNING
from shared_utils import nextTick
from AvatarInputHandler.control_modes import ArcadeControlMode

class SpawnKeyPointAvatar(BigWorld.DynamicScriptComponent):

    def receiveAvailableSpawnKeyPoints(self, points):
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.showSpawnPoints(points)

    def receiveTeamSpawnKeyPoints(self, pointsByVehicle):
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.updateTeamSpawnKeyPoints(pointsByVehicle)

    def receiveSpawnKeyPointsCloseTime(self, serverTime):
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.setupCloseTime(serverTime)

    def closeChooseSpawnKeyPointsWindow(self):
        LOG_WARNING('closeChooseSpawnKeyPointsWindow')
        spawnCtrl = self.entity.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.closeSpawnPoints()
        if self.entity.getVehicleAttached() is not None:
            controlMode = self.entity.inputHandler.ctrl
            if isinstance(controlMode, ArcadeControlMode):
                camera = self.entity.inputHandler.ctrl.camera
                nextTick(camera.setToVehicleDirection)()
        return
