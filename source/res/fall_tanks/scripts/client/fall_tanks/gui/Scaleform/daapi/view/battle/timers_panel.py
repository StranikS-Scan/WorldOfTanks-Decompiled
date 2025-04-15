# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/timers_panel.py
import typing
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel, _ReplayStackTimersCollection, _RegularStackTimersCollection
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINK
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_STATES
from gui.battle_control.battle_constants import TIMER_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from fall_tanks.gui.battle_control.fall_tanks_battle_constants import VEHICLE_VIEW_STATE
if typing.TYPE_CHECKING:
    from FallTanksController import EvacuationState
_EVACUATION_LINKAGE = 'EvacuationDestroyTimerUI'
_EVACUATION_ICON = 'destroyTimerRespawnUI'
_VEHICLE_EVACUATION_TIMER_TYPE = _TIMER_STATES.RECOVERY
_TIMERS_PRIORITY = {(_VEHICLE_EVACUATION_TIMER_TYPE, _TIMER_STATES.WARNING_VIEW): 1,
 (_TIMER_STATES.OVERTURNED, _TIMER_STATES.CRITICAL_VIEW): 2,
 (_TIMER_STATES.OVERTURNED, _TIMER_STATES.WARNING_VIEW): 3}

class _FallTanksReplayStackTimersCollection(_ReplayStackTimersCollection):
    _TIMERS_PRIORITY = _TIMERS_PRIORITY


class _FallTanksRegularStackTimersCollection(_RegularStackTimersCollection):
    _TIMERS_PRIORITY = _TIMERS_PRIORITY


class FallTanksTimersPanel(TimersPanel):
    _OFFSET = 0

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.VEHICLE_EVACUATION:
            self.__updateVehicleEvacuationNotification(value)
        elif state == VEHICLE_VIEW_STATE.DESTROY_TIMER:
            self._showDestroyTimer(value)

    def _generateMainTimersData(self):
        return [self._getNotificationTimerData(_VEHICLE_EVACUATION_TIMER_TYPE, _EVACUATION_ICON, _EVACUATION_LINKAGE, _COLORS.CUSTOM, text=backport.text(R.strings.fall_tanks.statusNotificationTimer.evacuation()), iconOffsetY=self._OFFSET), self._getNotificationTimerData(_TIMER_STATES.OVERTURNED, _LINK.OVERTURNED_GREEN_ICON, _LINK.DESTROY_TIMER_UI, _COLORS.GREEN, text=backport.text(R.strings.ingame_gui.destroyTimer.liftOver()), iconOffsetY=self._OFFSET)]

    def _generateSecondaryTimersData(self):
        return []

    @classmethod
    def _getTimersCollectionCls(cls):
        isReplayPlaying = cls.sessionProvider.isReplayPlaying
        return _FallTanksReplayStackTimersCollection if isReplayPlaying else _FallTanksRegularStackTimersCollection

    def __updateVehicleEvacuationNotification(self, evacuationState):
        if evacuationState.isActive:
            self._showTimer(_VEHICLE_EVACUATION_TIMER_TYPE, evacuationState.totalTime, TIMER_VIEW_STATE.WARNING, evacuationState.endTime)
        else:
            self._hideTimer(_VEHICLE_EVACUATION_TIMER_TYPE)
