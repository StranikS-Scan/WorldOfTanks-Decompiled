# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/shared/crosshair/plugins.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import VehicleStatePlugin
from halloween.gui.battle_control.halloween_battle_constants import VEHICLE_VIEW_STATE

class HWVehicleStatePlugin(VehicleStatePlugin):

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HW_MAX_HEALTH:
            self._setMaxHealth(value)
        super(HWVehicleStatePlugin, self)._onVehicleStateUpdated(state, value)
