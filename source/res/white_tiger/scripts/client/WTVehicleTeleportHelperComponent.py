# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleTeleportHelperComponent.py
from __future__ import absolute_import
import typing
import BigWorld
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Any
    from Avatar import Avatar

class WTVehicleTeleportHelperComponent(DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onTeleported(self, *args, **kwargs):
        BigWorld.callback(0.1, self.updateCameraDirection)
        self.__updateTeleportationProgress()

    def onTeleportInterrupted(self):
        self.__updateTeleportationProgress()

    def updateCameraDirection(self):
        player = BigWorld.player()
        arcadeCameraManager = player.inputHandler.ctrls['arcade']
        if arcadeCameraManager:
            arcadeCameraManager.camera.setToVehicleDirection()

    def __updateTeleportationProgress(self):
        from white_tiger.gui.white_tiger_gui_constants import BATTLE_CTRL_ID
        teleportCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
        if teleportCtrl is not None:
            teleportCtrl.updateTeleportationProgress()
        return
