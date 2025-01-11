# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/timers_panel.py
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel, _TIMERS_PRIORITY
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, TIMER_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
_FREEZING_ZONE_UI_TIMER = 'freezingZone'
_FLARE_MARK_UI_TIMER = 'flareMark'

class GrinchTimersPanel(TimersPanel):

    def __init__(self, mapping=None):
        super(GrinchTimersPanel, self).__init__(mapping)
        _TIMERS_PRIORITY[_FREEZING_ZONE_UI_TIMER, _TIMER_STATES.WARNING_VIEW] = 1
        _TIMERS_PRIORITY[_FLARE_MARK_UI_TIMER, _TIMER_STATES.CRITICAL_VIEW] = 9

    def _generateMainTimersData(self):
        tData = super(GrinchTimersPanel, self)._generateMainTimersData()
        linkage = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI
        replaced = {_TIMER_STATES.WARNING_ZONE: self._getNotificationTimerData(_TIMER_STATES.WARNING_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.GRINCH_WARNING_ICON, linkage=linkage, color=BATTLE_NOTIFICATIONS_TIMER_COLORS.LIGHT_BLUE, text=backport.text(R.strings.ingame_gui.grinchBattle.warning_zone.indicator())),
         _TIMER_STATES.DANGER_ZONE: self._getNotificationTimerData(_TIMER_STATES.DANGER_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.GRINCH_DANGER_ICON, linkage=linkage, color=BATTLE_NOTIFICATIONS_TIMER_COLORS.LIGHT_BLUE, iconOffsetY=-10),
         _FREEZING_ZONE_UI_TIMER: self._getNotificationTimerData(_FREEZING_ZONE_UI_TIMER, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.GRINCH_DANGER_ICON, linkage=linkage, color=BATTLE_NOTIFICATIONS_TIMER_COLORS.LIGHT_BLUE, text=backport.text(R.strings.ingame_gui.grinchBattle.death_zone.indicator())),
         _FLARE_MARK_UI_TIMER: self._getNotificationTimerData(_FLARE_MARK_UI_TIMER, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.GRINCH_FLARE_MARK_ICON, linkage=linkage, color=BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, text=backport.text(R.strings.ingame_gui.grinchBattle.flare_mark.indicator()), iconOffsetY=-10)}
        for i, tdV in enumerate(tData):
            typeID = tdV['typeId']
            if typeID in replaced:
                tData[i] = replaced[typeID]
                del replaced[typeID]

        for v in replaced.itervalues():
            tData.append(v)

        return tData

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.MAP_DEATH_ZONE:
            if value.needToCloseTimer():
                self._hideTimer(_FREEZING_ZONE_UI_TIMER)
            else:
                self._showTimer(_FREEZING_ZONE_UI_TIMER, 0.0, TIMER_VIEW_STATE.WARNING, 0.0)
        elif state == VEHICLE_VIEW_STATE.STEALTH_RADAR:
            if value.needToCloseTimer():
                self._hideTimer(_FLARE_MARK_UI_TIMER)
            else:
                self._showTimer(_FLARE_MARK_UI_TIMER, value.totalTime, value.level, value.totalTime + value.startTime)
        else:
            super(GrinchTimersPanel, self)._onVehicleStateUpdated(state, value)
