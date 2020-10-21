# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_destroy_timers_panel.py
from constants import VEHICLE_MISC_STATUS
from gui.Scaleform.daapi.view.meta.EventDestroyTimersPanelMeta import EventDestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, SoulCollectorDestroyTimerState
from gui.battle_control.event_dispatcher import onCollectorProgress, onCollectorProgressStop
from gui.impl import backport
from gui.impl.gen import R

class EventDestroyTimersPanel(EventDestroyTimersPanelMeta):

    def __init__(self, mapping=None):
        super(EventDestroyTimersPanel, self).__init__(mapping=mapping)
        self.__isVehOnFire = False
        self._vehicleInFireMessage = None
        self.__isVehOnAuraFire = False
        self.__isVehLoseSouls = False
        self.__isVehCanBeDamaged = True
        self._isRibbonsPanelOverlay = False
        self._isBuffsPanelOverlay = False
        return

    def _generateMainTimersData(self):
        data = super(EventDestroyTimersPanel, self)._generateMainTimersData()
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.EVENTWARNING_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI))
        return data

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.FIRE_WITH_MESSAGE:
            self.__setAuraFireInVehicle(value)
            return
        if state == VEHICLE_VIEW_STATE.LOSE_SOULS_IN_AURA:
            self.__setVehicleLoseSoulsInAura(value)
            return
        if state == VEHICLE_VIEW_STATE.CAN_BE_DAMAGED:
            self.__isVehCanBeDamaged = value
            if self.__isVehLoseSouls:
                self.__setVehicleLoseSoulsInAura()
            if self.__isVehOnAuraFire:
                self.__setAuraFireInVehicle()
            return
        if state == VEHICLE_VIEW_STATE.FIRE:
            self.__isVehOnFire = value
            self.__setFireInVehicle(value)
            if self.__isVehOnFire and self._vehicleInFireMessage:
                self.setWarningText(self._vehicleInFireMessage, self.__isVehOnFire)
            return
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isVehOnFire = False
            self.__isVehOnAuraFire = False
            self.__isVehLoseSouls = False
            self.__isVehCanBeDamaged = True
            return
        if state == VEHICLE_VIEW_STATE.DESTROY_TIMER:
            if value.code == VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED:
                self.as_setWarningTextS(backport.text(R.strings.event.destroyTimer.halfOverturned()), not value.needToCloseTimer())
        elif state == VEHICLE_VIEW_STATE.COLLECTOR_STATUS:
            self.__updateCollectorStatus(value)
        super(EventDestroyTimersPanel, self)._onVehicleStateUpdated(state, value)

    def __setAuraFireInVehicle(self, value=None):
        if value is not None:
            self.__isVehOnAuraFire = value
        isInFire = self.__isVehOnAuraFire and self.__isVehCanBeDamaged
        self.__setFireInVehicle(isInFire)
        self.as_setWarningTextS(backport.text(R.strings.event.bossAura.leaveDamageAreaWarningHealth()), isInFire)
        return

    def __setVehicleLoseSoulsInAura(self, value=None):
        if value is not None:
            self.__isVehLoseSouls = value
        isInFire = self.__isVehLoseSouls and self.__isVehCanBeDamaged
        self.as_setWarningTextS(backport.text(R.strings.event.bossAura.leaveDamageAreaWarningSouls()), isInFire)
        if isInFire:
            self._timers.addTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA, BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW, 0, None)
            onCollectorProgress({'isRibbonsPanelOverlay': self._isRibbonsPanelOverlay,
             'isBuffsPanelOverlay': self._isBuffsPanelOverlay})
        else:
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA)
            onCollectorProgressStop()
        return

    def __setFireInVehicle(self, isInFire):
        if (self.__isVehOnFire or self.__isVehOnAuraFire) and self.__isVehCanBeDamaged:
            isInFire = self.__isVehOnFire or self.__isVehOnAuraFire
        if isInFire:
            self._timers.addTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW, 0, None)
            onCollectorProgress({'isRibbonsPanelOverlay': self._isRibbonsPanelOverlay,
             'isBuffsPanelOverlay': self._isBuffsPanelOverlay})
        else:
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE)
            onCollectorProgressStop()
        return

    def __updateCollectorStatus(self, data):
        if data['state'] != SoulCollectorDestroyTimerState.NO_TIMER:
            onCollectorProgress({'isRibbonsPanelOverlay': self._isRibbonsPanelOverlay,
             'isBuffsPanelOverlay': self._isBuffsPanelOverlay})
        if data['state'] == SoulCollectorDestroyTimerState.WAIT_ALLIES:
            self.as_setWaitForAlliesS(True)
        elif data['state'] == SoulCollectorDestroyTimerState.COLLECTOR_PROGRESS:
            self.as_setFillingInProgressS(data['soulsCollected'], data['collectorCapacity'], data['isActive'], True)
        elif data['state'] == SoulCollectorDestroyTimerState.ALARM_TIMER:
            self.as_setGotoPointTimerS(data['timeLeft'], data['alarmTime'], '' if not data['showMessage'] else backport.text(R.strings.event.notification.gotoToTeleport()), True)
        else:
            self.as_hideAllNotificationsS()
            onCollectorProgressStop()

    def setVehicleInFireMessage(self, msg):
        self._vehicleInFireMessage = msg

    def setWarningText(self, warningText, isInFire):
        self.as_setWarningTextS(warningText, isInFire)

    def setComponentsOverlay(self, isRibbonsPanelOverlay, isBuffsPanelOverlay):
        self._isRibbonsPanelOverlay = isRibbonsPanelOverlay
        self._isBuffsPanelOverlay = isBuffsPanelOverlay
