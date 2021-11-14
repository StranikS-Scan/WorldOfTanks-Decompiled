# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_destroy_timers_panel.py
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.meta.EventDestroyTimersPanelMeta import EventDestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES

class EventDestroyTimersPanel(EventDestroyTimersPanelMeta):

    def __init__(self, mapping=None):
        super(EventDestroyTimersPanel, self).__init__()
        self.__isVehOnFire = False
        self._vehicleInFireMessage = None
        return

    def _generateMainTimersData(self):
        data = super(EventDestroyTimersPanel, self)._generateMainTimersData()
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.EVENT_WARNING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.EVENTWARNING_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI))
        return data

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.FIRE:
            self.__isVehOnFire = value
            self.__setFireInVehicle(value)
            if self.__isVehOnFire and self._vehicleInFireMessage:
                self.setWarningText(self._vehicleInFireMessage, self.__isVehOnFire)
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isVehOnFire = False
        else:
            super(EventDestroyTimersPanel, self)._onVehicleStateUpdated(state, value)

    def __setFireInVehicle(self, isInFire):
        if self.__isVehOnFire:
            self._timers.addTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW, 0, None)
        else:
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE)
        return

    def setVehicleInFireMessage(self, msg):
        self._vehicleInFireMessage = msg

    def setWarningText(self, warningText, isInFire):
        self.as_setWarningTextS(warningText, isInFire)
