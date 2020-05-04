# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_destroy_timers_panel.py
import SoundGroups
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.meta.EventDestroyTimersPanelMeta import EventDestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_DESTROY_TIMER_STATES import BATTLE_DESTROY_TIMER_STATES as _TIMER_STATES
import BigWorld

class EventDestroyTimersPanel(EventDestroyTimersPanelMeta):
    _DEATHZONE_ENTER_SOUND = 'ev_2020_secret_event_gameplay_death_sector_timer_start'
    _DEATHZONE_EXIT_SOUND = 'ev_2020_secret_event_gameplay_death_sector_timer_stop'

    def __init__(self, mapping=None):
        super(EventDestroyTimersPanel, self).__init__(mapping)
        self.__deathzoneWarningCounter = 0
        self.__deathzoneStrikeTime = 0
        self.__activePersonalDeathZones = {}
        self.__personalZoneLastTimeToStrike = 0

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.EVENT_DEATHZONE:
            self.__updateDeathZoneWarningNotification(*value)
        elif state == VEHICLE_VIEW_STATE.PERSONAL_DEATHZONE:
            self.__updatePersonalDeathZoneWarningNotification(*value)
        else:
            self.as_setWarningTextS('', False)
            super(EventDestroyTimersPanel, self)._onVehicleStateUpdated(state, value)

    def __updateDeathZoneWarningNotification(self, visible, time, updateTimeOnly):
        self.as_setWarningTextS(backport.text(R.strings.event.notification.deathzone()), visible)
        if not updateTimeOnly or not visible:
            self.__deathzoneWarningCounter += 1 if visible else -1
        if self.__deathzoneWarningCounter > 0:
            self.__deathzoneStrikeTime = time
        self.__updateDeathZoneTimer(updateTimeOnly)

    def __updateDeathZoneTimer(self, updateOnly=True):
        if self.__deathzoneWarningCounter > 0:
            self._showTimer(_TIMER_STATES.EVENT_DEATH_ZONE, self.__deathzoneStrikeTime - BigWorld.serverTime(), 'critical', None)
            if not updateOnly:
                SoundGroups.g_instance.playSound2D(self._DEATHZONE_ENTER_SOUND)
        else:
            self._hideTimer(_TIMER_STATES.EVENT_DEATH_ZONE)
            SoundGroups.g_instance.playSound2D(self._DEATHZONE_EXIT_SOUND)
            self.__updatePersonalDeathZoneTimer(max(self.__personalZoneLastTimeToStrike - BigWorld.serverTime(), 0))
        return

    def __updatePersonalDeathZoneWarningNotification(self, zoneId, enable, endTime):
        if enable:
            self.__activePersonalDeathZones[zoneId] = endTime
        elif zoneId in self.__activePersonalDeathZones:
            self.__activePersonalDeathZones.pop(zoneId)
        self.as_setWarningTextS(backport.text(R.strings.event.notification.deathzone()), bool(self.__activePersonalDeathZones) and self.__isPlayerAlive())
        if self.__activePersonalDeathZones:
            minStrikeTime = min([ value for value in self.__activePersonalDeathZones.itervalues() ])
            timeToStrike = max(minStrikeTime - BigWorld.serverTime(), 0)
            if self.__personalZoneLastTimeToStrike != minStrikeTime or timeToStrike == 0:
                self.__updatePersonalDeathZoneTimer(timeToStrike)
            self.__personalZoneLastTimeToStrike = minStrikeTime
        else:
            self._hideTimer(_TIMER_STATES.EVENT_DEATH_ZONE)
            self.__personalZoneLastTimeToStrike = 0
            self.__updateDeathZoneTimer()

    def __updatePersonalDeathZoneTimer(self, timeToStrike):
        if not self.__activePersonalDeathZones:
            return
        else:
            if self.__isPlayerAlive():
                state = 'critical' if timeToStrike > 0 else 'warning'
                self._showTimer(_TIMER_STATES.EVENT_DEATH_ZONE, timeToStrike, state, None)
            return

    def __isPlayerAlive(self):
        vehicle = BigWorld.player().vehicle
        return vehicle and vehicle.isAlive()
