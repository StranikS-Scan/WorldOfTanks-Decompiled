# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/shared/crosshair/plugins.py
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import VehicleStatePlugin
from last_stand.gui.battle_control.ls_battle_constants import VEHICLE_VIEW_STATE

class LSVehicleStatePlugin(VehicleStatePlugin):

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.LS_MAX_HEALTH:
            self._setMaxHealth(value)
        super(LSVehicleStatePlugin, self)._onVehicleStateUpdated(state, value)
