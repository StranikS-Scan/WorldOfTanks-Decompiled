# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/timers_panel.py
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class CommanderTimersPanel(TimersPanel):

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            return
        super(CommanderTimersPanel, self)._onVehicleStateUpdated(state, value)
