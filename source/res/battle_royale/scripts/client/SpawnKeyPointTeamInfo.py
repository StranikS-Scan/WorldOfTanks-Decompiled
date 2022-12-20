# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/SpawnKeyPointTeamInfo.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from shared_utils import nextTick
from AvatarInputHandler.control_modes import ArcadeControlMode
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from battle_royale_client_common.SpawnKeyPointTeamInfoBase import SpawnKeyPointTeamInfoBase

class SpawnKeyPointTeamInfo(SpawnKeyPointTeamInfoBase, DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        if self.placed:
            return
        self.onReceiveTeamSpawnKeyPoints += self.__onReceiveTeamSpawnKeyPoints
        self.onCloseChooseSpawnKeyPointsWindow += self.__onCloseChooseSpawnKeyPointsWindow
        spawnCtrl = self.guiSessionProvider.dynamic.spawn
        spawnCtrl.showSpawnPoints(self.availableSpawnKeyPoints)
        if self.spawnKeyPointsCloseTime:
            spawnCtrl.setupCloseTime(self.spawnKeyPointsCloseTime)
        self.__onReceiveTeamSpawnKeyPoints(self.teamSpawnKeyPoints)

    def set_spawnKeyPointsCloseTime(self, prev):
        spawnCtrl = self.guiSessionProvider.dynamic.spawn
        spawnCtrl.setupCloseTime(self.spawnKeyPointsCloseTime)

    def __onReceiveTeamSpawnKeyPoints(self, points):
        if not self._isAvatarReady:
            return
        self.guiSessionProvider.dynamic.spawn.updateTeamSpawnKeyPoints(points)

    def __onCloseChooseSpawnKeyPointsWindow(self):
        if not self._isAvatarReady:
            return
        else:
            spawnCtrl = self.guiSessionProvider.dynamic.spawn
            spawnCtrl.closeSpawnPoints()
            self.onReceiveTeamSpawnKeyPoints -= self.__onReceiveTeamSpawnKeyPoints
            self.onCloseChooseSpawnKeyPointsWindow -= self.__onCloseChooseSpawnKeyPointsWindow
            avatar = BigWorld.player()
            if avatar.getVehicleAttached() is not None:
                controlMode = avatar.inputHandler.ctrl
                if isinstance(controlMode, ArcadeControlMode):
                    camera = avatar.inputHandler.ctrl.camera
                    nextTick(camera.setToVehicleDirection)()
            return

    def _avatar(self):
        return BigWorld.player()
