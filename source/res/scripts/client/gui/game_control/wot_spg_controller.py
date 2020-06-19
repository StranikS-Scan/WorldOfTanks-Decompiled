# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_spg_controller.py
from collections import defaultdict
import typing
import Event
from gui.periodic_battles.models import PrimeTime
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from shared_utils import collapseIntervals, findFirst
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IWOTSPGController
from CurrentVehicle import g_currentVehicle

class WOTSPGEventController(IWOTSPGController, Notifiable):
    _eventsCache = dependency.descriptor(IEventsCache)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(WOTSPGEventController, self).__init__()
        self.__isVehSwitching = False
        self.__isEventEnabled = None
        self.__isEventModeOn = None
        self.onEventModeChanged = Event.Event()
        self.onEventTriggerChanged = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onUpdated = Event.Event()
        return

    def fini(self):
        self.onEventModeChanged.clear()
        self.onEventTriggerChanged.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.onUpdated.clear()
        self.clearNotification()
        super(WOTSPGEventController, self).fini()

    def init(self):
        super(WOTSPGEventController, self).init()
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerUpdate, (time_utils.ONE_MINUTE,)))

    def isEnabled(self):
        return bool(self._eventsCache.getEventBattles().enabled)

    def onLobbyInited(self, ctx):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self._eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        g_currentVehicle.onChangeStarted += self.__onCurrentVehicleChangeStarted
        self.startNotification()

    def isEventModeOn(self):
        return self.isEnabled() and self.__getEventModeOn()

    def isEventVehicle(self):
        return self.__getEventModeOn()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def getPrimeTimes(self):
        primeTimes = self._eventsCache.getEventPrimeTimes()
        primeTimesPeriods = defaultdict(lambda : defaultdict(list))
        for primeTime in primeTimes:
            period = (primeTime.start, primeTime.end)
            weekdays = primeTime.weekdays
            for pID in primeTime.peripheryIDs:
                periphery = primeTimesPeriods[pID]
                for wDay in weekdays:
                    periphery[wDay].append(period)

        return {pID:PrimeTime(pID, {wDay:collapseIntervals(periods) for wDay, periods in pPeriods.iteritems()}) for pID, pPeriods in primeTimesPeriods.iteritems()}

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        primeTimes = self.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        serversPeriodsMapping = {}
        hostsList = self.__getHostList()
        for _, _, serverShortName, _, peripheryID in hostsList:
            if peripheryID not in primeTimes:
                continue
            dayPeriods = primeTimes[peripheryID].getPeriodsBetween(dayStart, dayEnd)
            if groupIdentical and dayPeriods in serversPeriodsMapping.values():
                for name, period in serversPeriodsMapping.iteritems():
                    serverInMapping = name if period == dayPeriods else None
                    if serverInMapping:
                        newName = '{0}, {1}'.format(serverInMapping, serverShortName)
                        serversPeriodsMapping[newName] = serversPeriodsMapping.pop(serverInMapping)
                        break

            serversPeriodsMapping[serverShortName] = dayPeriods

        return serversPeriodsMapping

    def getPrimeTimeStatus(self, peripheryID=None):
        if peripheryID is None:
            peripheryID = self._connectionMgr.peripheryID
        primeTime = self.getPrimeTimes().get(peripheryID)
        if primeTime is None:
            return (PrimeTimeStatus.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PrimeTimeStatus.FROZEN, 0, False)
        else:
            isNow, timeTillUpdate = self.__getAvailability(primeTime)
            return (PrimeTimeStatus.AVAILABLE, timeTillUpdate, True) if isNow else (PrimeTimeStatus.NOT_AVAILABLE, timeTillUpdate, False)

    def getTimer(self):
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus()
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE and not self._connectionMgr.isStandalone():
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
            for peripheryID in allPeripheryIDs:
                peripheryStatus, peripheryTime, _ = self.getPrimeTimeStatus(peripheryID)
                if peripheryStatus == PrimeTimeStatus.NOT_AVAILABLE and peripheryTime < timeLeft:
                    timeLeft = peripheryTime

        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def hasConfiguredPrimeTimeServers(self):
        return self.__hasPrimeStatusServer((PrimeTimeStatus.AVAILABLE, PrimeTimeStatus.NOT_AVAILABLE))

    def hasAvailablePrimeTimeServers(self):
        return self.__hasPrimeStatusServer((PrimeTimeStatus.AVAILABLE,))

    def __initData(self):
        self.__onEventsCacheSyncCompleted()

    def __clear(self):
        self.__isVehSwitching = False
        self.__isEventModeOn = None
        self.__isEventEnabled = None
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_currentVehicle.onChangeStarted -= self.__onCurrentVehicleChangeStarted
        self._eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.stopNotification()
        return

    def __updateEventModeState(self):
        if g_currentVehicle.isPresent():
            isEventModeOn = self.isEventModeOn()
            if isEventModeOn != self.__isEventModeOn:
                self.__isEventModeOn = isEventModeOn
                self.onEventModeChanged(self.__isEventModeOn)

    def __getEventModeOn(self):
        return g_currentVehicle.item.isOnlyForEventBattles if g_currentVehicle.isPresent() else False

    def __onCurrentVehicleChanged(self):
        if self.__isVehSwitching:
            self.__updateEventModeState()
        self.__isVehSwitching = False

    def __onCurrentVehicleChangeStarted(self):
        self.__isVehSwitching = True

    def __onEventsCacheSyncCompleted(self, *_):
        isEventEnabled = self.isEnabled()
        if isEventEnabled != self.__isEventEnabled:
            self.__isEventEnabled = isEventEnabled
            self.onEventTriggerChanged(isEventEnabled)
            self.__updateEventModeState()
            self.__resetTimer()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __getHostList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self._connectionMgr.isStandalone():
            hostsList.insert(0, (self._connectionMgr.url,
             self._connectionMgr.serverUserName,
             self._connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        return hostsList

    def __getAvailability(self, primeTime):
        now = time_utils.getServerUTCTime()
        periods = primeTime.getPeriodsActiveForTime(now, True)
        currentPeriod = findFirst(lambda (start, end): start <= now < end, periods)
        isNow = currentPeriod is not None
        if isNow:
            timeTillUpdate = currentPeriod[1] - now
        else:
            nextPeriod = self.__getNextPeriodStart(primeTime)
            timeTillUpdate = nextPeriod[0] - now
        return (isNow, timeTillUpdate)

    def __getNextPeriodStart(self, primeTime):
        if not primeTime.hasAnyPeriods():
            return None
        else:
            now = time_utils.getServerUTCTime()
            allPeriods = primeTime.getPeriods()
            startDateTime = time_utils.getDateTimeInUTC(now)
            startTimeDayStart, _ = time_utils.getDayTimeBoundsForUTC(now)
            weekDay = startDateTime.isoweekday()
            oneHour = time_utils.ONE_HOUR
            oneMinute = time_utils.ONE_MINUTE
            while True:
                if weekDay in allPeriods:
                    for (startHour, startMinute), (endHour, endMinute) in allPeriods[weekDay]:
                        periodStartTime = startTimeDayStart + startHour * oneHour + startMinute * oneMinute
                        periodEndTime = startTimeDayStart + endHour * oneHour + endMinute * oneMinute
                        if now < periodEndTime:
                            period = (max(now, periodStartTime), periodEndTime)
                            return period

                if weekDay == time_utils.WEEK_END:
                    weekDay = time_utils.WEEK_START
                else:
                    weekDay += 1
                startTimeDayStart += time_utils.ONE_DAY

            return None

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)
        self.onUpdated()

    def __hasPrimeStatusServer(self, states):
        if self._connectionMgr.isStandalone():
            allPeripheryIDs = {self._connectionMgr.peripheryID}
        else:
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
        for peripheryID in allPeripheryIDs:
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus in states:
                return True

        return False
