# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/shared/timers_panel.py
from __future__ import absolute_import
from fort_rush.gui.battle_control.fort_rush_battle_constants import FR_VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel, _TIMERS_PRIORITY
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
_INVULNERABLE = 'invulnerable'
_INVULNERABLE_PRIORITY = (_INVULNERABLE, _TIMER_STATES.WARNING_VIEW)

class FortRushTimersPanel(TimersPanel):

    def __init__(self, mapping=None):
        super(FortRushTimersPanel, self).__init__(mapping)
        stunPriority = _TIMERS_PRIORITY.get((_TIMER_STATES.STUN, _TIMER_STATES.WARNING_VIEW), 10)
        _TIMERS_PRIORITY[_INVULNERABLE_PRIORITY] = stunPriority + 1

    def _dispose(self):
        _TIMERS_PRIORITY.pop(_INVULNERABLE_PRIORITY, None)
        super(FortRushTimersPanel, self)._dispose()
        return

    def _generateMainTimersData(self):
        mtd = super(FortRushTimersPanel, self)._generateMainTimersData()
        mtd.append(self._getNotificationTimerData(_INVULNERABLE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SHIELD_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI, color=BATTLE_NOTIFICATIONS_TIMER_COLORS.LIGHT_BLUE, text=backport.text(R.strings.fort_rush.timersPanel.invulnerable()), iconOffsetY=-10))
        return mtd

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            if self._timers and self._timers.hasActiveTimer(_INVULNERABLE):
                return
        if state == FR_VEHICLE_VIEW_STATE.INVULNERABLE:
            if value.needToCloseTimer():
                self._hideTimer(_INVULNERABLE)
            else:
                self._showTimer(_INVULNERABLE, value.totalTime, value.level, value.totalTime + value.startTime)
        else:
            super(FortRushTimersPanel, self)._onVehicleStateUpdated(state, value)
