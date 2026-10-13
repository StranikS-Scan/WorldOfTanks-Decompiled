# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleStatusNotificationComponent.py
from __future__ import absolute_import
import BigWorld
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class HWVehicleStatusNotificationComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWVehicleStatusNotificationComponent, self).__init__()
        player = BigWorld.player()
        self._isPlayerVehicle = player.vehicle and player.vehicle.id == self.entity.id
        if self._isPlayerVehicle:
            self._state = getattr(VEHICLE_VIEW_STATE, self.vehicleViewState, None)
            if self._state:
                self.guiSessionProvider.invalidateVehicleState(self._state, *self.initArgs)
        return

    def onDestroy(self):
        if self._isPlayerVehicle:
            self.guiSessionProvider.invalidateVehicleState(self._state, *self.finiArgs)
