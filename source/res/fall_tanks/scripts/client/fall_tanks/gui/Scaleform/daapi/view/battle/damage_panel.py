# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/damage_panel.py
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class FallTanksDamagePanel(DamagePanel):

    def _onVehicleStateUpdated(self, state, value):
        if state not in {VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.HEALTH}:
            super(FallTanksDamagePanel, self)._onVehicleStateUpdated(state, value)
