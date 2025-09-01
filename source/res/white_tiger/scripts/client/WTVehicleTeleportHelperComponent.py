# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleTeleportHelperComponent.py
import typing
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
if typing.TYPE_CHECKING:
    from typing import Any
    from Avatar import Avatar

class WTVehicleTeleportHelperComponent(DynamicScriptComponent):

    def onTeleported(self, *args, **kwargs):
        BigWorld.callback(0.1, self.updateCameraDirection)

    def updateCameraDirection(self):
        player = BigWorld.player()
        arcadeCameraManager = player.inputHandler.ctrls['arcade']
        if arcadeCameraManager:
            arcadeCameraManager.camera.setToVehicleDirection()
