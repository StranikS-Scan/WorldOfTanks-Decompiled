# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_destroy_timers_panel.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.EventDestroyTimersPanelMeta import EventDestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, SoulCollectorDestroyTimerState
from gui.battle_control.event_dispatcher import onCollectorProgress, onCollectorProgressStop
from gui.impl import backport
from gui.impl.gen import R

class EventDestroyTimersPanel(EventDestroyTimersPanelMeta):
    _TEMPLATES_PATH = 'html_templates:eventHW21/destroyTimer'

    def __init__(self, mapping=None):
        super(EventDestroyTimersPanel, self).__init__(mapping=mapping)
        self.__isVehOnFire = False
        self.__isVehOnAuraFire = False
        self.__isVehLoseSouls = False
        self.__isVehCanBeDamaged = True
        self.__isRibbonsPanelOverlay = False
        self.__isBuffsPanelOverlay = False
        self.__currentCollectorState = SoulCollectorDestroyTimerState.NO_TIMER
        self.__currentTimer = None
        self._timers.onCurrentTimerChange += self.__onCurrentTimerChange
        return

    def _dispose(self):
        self._timers.onCurrentTimerChange -= self.__onCurrentTimerChange
        super(EventDestroyTimersPanel, self)._dispose()

    def _generateMainTimersData(self):
        data = super(EventDestroyTimersPanel, self)._generateMainTimersData()
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.EVENTWARNING_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI))
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.EVENT_DEATH_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.EVENT_PERSONAL_DEATH_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI, iconOffsetY=-8))
        return data

    def _getStaticDeathZoneIcon(self):
        return BATTLE_NOTIFICATIONS_TIMER_LINKAGES.EVENT_STATIC_DEATH_ZONE

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
            return
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isVehOnFire = False
            self.__isVehOnAuraFire = False
            self.__isVehLoseSouls = False
            self.__isVehCanBeDamaged = True
            return
        if state == VEHICLE_VIEW_STATE.COLLECTOR_STATUS:
            self.__updateCollectorStatus(value)
        super(EventDestroyTimersPanel, self)._onVehicleStateUpdated(state, value)

    def __setAuraFireInVehicle(self, value=None):
        if value is not None:
            self.__isVehOnAuraFire = value
        isInFire = self.__isVehOnAuraFire and self.__isVehCanBeDamaged
        self.__setFireInVehicle(isInFire)
        return

    def __setVehicleLoseSoulsInAura(self, value=None):
        if value is not None:
            self.__isVehLoseSouls = value
        isInFire = self.__isVehLoseSouls and self.__isVehCanBeDamaged
        if isInFire:
            self._timers.addTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA, BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW, 0, None)
        else:
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA)
        return

    def __setFireInVehicle(self, isInFire):
        if (self.__isVehOnFire or self.__isVehOnAuraFire) and self.__isVehCanBeDamaged:
            isInFire = self.__isVehOnFire or self.__isVehOnAuraFire
        if isInFire:
            self._timers.addTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW, 0, None)
        else:
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE)
        return

    def __updateCollectorStatus(self, data):
        if data['state'] == SoulCollectorDestroyTimerState.WAIT_ALLIES:
            self.as_setWaitForAlliesS(True)
        elif data['state'] == SoulCollectorDestroyTimerState.COLLECTOR_PROGRESS:
            self.as_setFillingInProgressS(data['soulsCollected'], data['collectorCapacity'], data['isActive'], True)
        elif data['state'] == SoulCollectorDestroyTimerState.ALARM_TIMER:
            self.as_setGotoPointTimerS(data['timeLeft'], data['alarmTime'], '' if not data['showMessage'] else backport.text(R.strings.event.notification.gotoToTeleport()), True)
        else:
            self.as_hideAllNotificationsS()
        self.__currentCollectorState = data['state']
        self.__updateOverlays()

    def setComponentsOverlay(self, isRibbonsPanelOverlay, isBuffsPanelOverlay):
        self.__isRibbonsPanelOverlay = isRibbonsPanelOverlay
        self.__isBuffsPanelOverlay = isBuffsPanelOverlay
        self.__updateOverlays()

    def __onCurrentTimerChange(self):
        timerId = self._timers.getCurrentTimerId()
        if timerId == BATTLE_NOTIFICATIONS_TIMER_TYPES.EVENT_DEATH_ZONE:
            self.as_setWarningTextS(makeHtmlString(self._TEMPLATES_PATH, 'personalDeathZone', {'value': backport.text(R.strings.event.battle.leaveDeathZone())}))
        elif timerId == BATTLE_NOTIFICATIONS_TIMER_TYPES.LOSE_SOULS_IN_AURA:
            self.as_setWarningTextS(backport.text(R.strings.event.bossAura.leaveDamageAreaWarningSouls()))
        elif timerId == BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE and self.__isVehOnAuraFire:
            self.as_setWarningTextS(backport.text(R.strings.event.bossAura.leaveDamageAreaWarningHealth()))
        elif timerId in (BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED):
            self.as_setWarningTextS(backport.text(R.strings.event.destroyTimer.halfOverturned()))
        elif timerId == BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE:
            self.as_setWarningTextS(backport.text(R.strings.event.destroyTimer.deathZone()))
        else:
            self.as_setWarningTextS('')
        self.__currentTimer = timerId
        self.__updateOverlays()

    def __updateOverlays(self):
        if self.__currentCollectorState != SoulCollectorDestroyTimerState.NO_TIMER or self.__currentTimer:
            onCollectorProgress({'isRibbonsPanelOverlay': self.__isRibbonsPanelOverlay,
             'isBuffsPanelOverlay': self.__isBuffsPanelOverlay})
        else:
            onCollectorProgressStop()
