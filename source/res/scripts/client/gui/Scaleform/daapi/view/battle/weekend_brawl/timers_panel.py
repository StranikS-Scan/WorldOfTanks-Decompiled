# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/timers_panel.py
import weakref
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel
from gui.Scaleform.daapi.view.battle.weekend_brawl.timer_helpers import CapturingTimer, CapturedTimer, PointCooldownTimer, VehicleCooldownTimer, BlockedCapturingTimer
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_TYPES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
_MAX_DISPLAYED_SECONDARY_STATUS_TIMERS = 5

class _HelpersContainer(object):

    def __init__(self, itemClasses, view):
        self._items = [ itmClazz(view, idx) for idx, itmClazz in enumerate(itemClasses) ]

    def destroy(self):
        for item in self._items:
            item.destroy()

        self._items = None
        return

    def getItems(self):
        return self._items

    def getItem(self, idx):
        return self._items[idx]

    def update(self, value):
        for item in self._items:
            item.update(value)


class WeekendBrawlTimersPanel(TimersPanel):
    __slots__ = ('__timerHelpers',)
    _collection = [CapturingTimer,
     CapturedTimer,
     BlockedCapturingTimer,
     VehicleCooldownTimer,
     PointCooldownTimer]

    def __init__(self):
        super(WeekendBrawlTimersPanel, self).__init__()
        self._timers.setMaxDisplaySecondaryTimers(_MAX_DISPLAYED_SECONDARY_STATUS_TIMERS)
        self.__timerHelpers = None
        return

    def showTimer(self, timerIdx):
        timer = self.__timerHelpers.getItem(timerIdx)
        if timer is not None:
            self._showTimer(*timer.getData())
            timer.showText()
        return

    def removeTimer(self, timerIdx):
        timer = self.__timerHelpers.getItem(timerIdx)
        self._hideTimer(timer.getTimerTypeID())

    def _populate(self):
        super(WeekendBrawlTimersPanel, self)._populate()
        self.__timerHelpers = _HelpersContainer(self._collection, weakref.proxy(self))

    def _dispose(self):
        self.__timerHelpers.destroy()
        self.__timerHelpers = None
        super(WeekendBrawlTimersPanel, self)._dispose()
        return

    def _generateMainTimersData(self):
        data = super(WeekendBrawlTimersPanel, self)._generateMainTimersData()
        data.append(self._getNotificationTimerData(_TIMER_TYPES.INTEREST_POINT_CAPTURING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INTEREST_POINT_CAPTURING_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WEEKEND_BRAWL_GREEN_TIMER_UI, iconOffsetY=-10))
        data.append(self._getNotificationTimerData(_TIMER_TYPES.INTEREST_POINT_COOLDOWN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INTEREST_POINT_COOLDOWN_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WEEKEND_BRAWL_ORANGE_TIMER_UI, iconOffsetY=-10))
        return data

    def _generateSecondaryTimersData(self):
        data = super(WeekendBrawlTimersPanel, self)._generateSecondaryTimersData()
        data.append(self._getNotificationTimerData(_TIMER_TYPES.INTEREST_POINT_CAPTURED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INTEREST_POINT_CAPTURED_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WEEKEND_BRAWL_NOTIFICATION_UI))
        data.append(self._getNotificationTimerData(_TIMER_TYPES.INTEREST_POINT_BLOCKED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INTEREST_POINT_BLOCKED_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, True, False))
        return data

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.POINT_OF_INTEREST:
            self.__timerHelpers.update(value)
        else:
            super(WeekendBrawlTimersPanel, self)._onVehicleStateUpdated(state, value)
