# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_availability.py
import Event
from debug_utils import LOG_DEBUG
from helpers import dependency
from helpers import time_utils
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext

def isHourInForbiddenList(hours, currUtcTimeHour=None):
    if currUtcTimeHour is not None:
        cTime = currUtcTimeHour
    else:
        cTime = time_utils.getTimeStructInUTC(None).tm_hour
    return cTime in hours


def _getNextHour(hour):
    hour = hour + 1
    return hour if hour < time_utils.HOURS_IN_DAY else 0


def getForbiddenPeriods(hours, formatter=None):
    guiData = []

    def _formatPeriod(fromHour, endHour):
        if formatter:
            return formatter(fromHour, endHour)
        else:
            return (fromHour, endHour)

    if hours:
        currRange = None
        for h in hours:
            if currRange is None:
                currRange = [h, h]
            if h - currRange[1] > 1:
                guiData.append(_formatPeriod(currRange[0], _getNextHour(currRange[1])))
                currRange = [h, h]
            currRange[1] = h

        guiData.append(_formatPeriod(currRange[0], _getNextHour(currRange[1])))
    return guiData


def getUpdatePeriods(forbiddenUTCHours, localTimestamp=None):

    def __getHour(index):
        index += 1
        if index == time_utils.HOURS_IN_DAY:
            index = 0
        return index

    firstPeriod = 0
    outcomePeriods = []
    if forbiddenUTCHours and len(forbiddenUTCHours) < time_utils.HOURS_IN_DAY:
        utc = time_utils.getTimeStructInUTC(localTimestamp)
        utcCurrHour = utc.tm_hour
        forbiddenValue = utcCurrHour in forbiddenUTCHours
        hoursTillFirstUpdate = None
        hoursTillUpdate = 0
        hour = utcCurrHour
        for i in range(0, time_utils.HOURS_IN_DAY + 1):
            hour = __getHour(hour)
            currForbiddenValue = hour in forbiddenUTCHours
            if currForbiddenValue != forbiddenValue:
                forbiddenValue = currForbiddenValue
                if hoursTillFirstUpdate is None:
                    hoursTillFirstUpdate = hoursTillUpdate
                else:
                    outcomePeriods.append((hoursTillUpdate + 1) * time_utils.ONE_HOUR)
                hoursTillUpdate = 0
            if i != time_utils.HOURS_IN_DAY:
                hoursTillUpdate += 1
            outcomePeriods.append((hoursTillUpdate + 1 + hoursTillFirstUpdate) * time_utils.ONE_HOUR)

        secondsLeft = time_utils.ONE_HOUR - (utc.tm_min * time_utils.ONE_MINUTE + utc.tm_sec)
        firstPeriod = hoursTillFirstUpdate * time_utils.ONE_HOUR + secondsLeft
    return (firstPeriod, outcomePeriods)


class BattleAvailabilityController(Notifiable):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, notifierClass=None):
        super(BattleAvailabilityController, self).__init__(self)
        self._battlesAvailable = None
        self._currServerAvailable = None
        self.onStatusChanged = Event.Event()
        notifier = notifierClass or SimpleNotifier
        self.__currentPeriod = 0
        self.__periods = None
        self.addNotificator(notifier(self.__getClosestUpdatePeriod, self.__notificatorUpdated))
        return

    def start(self):
        g_clientUpdateManager.addCallbacks({'serverSettings': self._onChanged})
        self._update()

    def stop(self):
        self.clearNotification()
        self.onStatusChanged.clear()
        self.__periods = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def getStatus(self):
        if self._battlesAvailable is None:
            self._calcStatus()
        return (self._battlesAvailable, self._currServerAvailable)

    def getForbiddenHours(self):
        raise NotImplementedError()

    def isServerAvailable(self):
        raise NotImplementedError()

    def _onChanged(self, diff=None):
        raise NotImplementedError()

    def _getPeriodsInfo(self):
        return (self.__currentPeriod, self.__periods[:] if self.__periods else None)

    def _getTimeStamp(self):
        return None

    def _update(self, forbHours=None):
        hours = forbHours
        if hours is None:
            hours = self.getForbiddenHours()
        self._calcStatus(hours)
        if not self._currServerAvailable:
            self.__currentPeriod, self.__periods = (0, 0)
            self.stopNotification()
        else:
            self.__currentPeriod, self.__periods = getUpdatePeriods(hours, self._getTimeStamp())
            self.startNotification()
        self.onStatusChanged()
        return

    def _calcStatus(self, hours=None):
        hours = hours or self.getForbiddenHours()
        utcHour = time_utils.getTimeStructInUTC(self._getTimeStamp()).tm_hour
        self._battlesAvailable = not isHourInForbiddenList(hours, utcHour)
        self._currServerAvailable = self.isServerAvailable()

    def __getClosestUpdatePeriod(self):
        return self.__currentPeriod

    def __notificatorUpdated(self):
        if self.__periods:
            self.__currentPeriod = self.__periods.pop(0)
            self.__periods.append(self.__currentPeriod)
        else:
            self.__currentPeriod = 0
        self._calcStatus()
        self.startNotification()
        self.onStatusChanged()


class SortiesCurfewController(BattleAvailabilityController):

    def start(self):
        super(SortiesCurfewController, self).start()
        LOG_DEBUG('Sorties controller started')

    def stop(self):
        super(SortiesCurfewController, self).stop()
        LOG_DEBUG('Sorties controller has been successfully stopped')

    def getForbiddenHours(self):
        servSettings = self.lobbyContext.getServerSettings()
        return servSettings.getForbiddenSortieHours() if servSettings else []

    def isServerAvailable(self):
        servSettings = self.lobbyContext.getServerSettings()
        return False if servSettings and self.connectionMgr.peripheryID in servSettings.getForbiddenSortiePeripheryIDs() else True

    def _onChanged(self, diff=None):
        if diff and ('forbiddenSortieHours' in diff or 'forbiddenSortiePeripheryIDs' in diff):
            self._update(diff.get('forbiddenSortieHours'))
            LOG_DEBUG('Sorties settings changed:', diff)

    def _getTimeStamp(self):
        return time_utils.getCurrentLocalServerTimestamp()

    def _calcStatus(self, hours=None):
        super(SortiesCurfewController, self)._calcStatus(hours)
        LOG_DEBUG('Sortie availability:', 'At current hour:', self._battlesAvailable, 'At current periphery:', self._currServerAvailable)

    def __repr__(self):
        currentPeriod, periods = self._getPeriodsInfo()
        return 'SortiesCurfewController (Sorties availability: At current hour: {0}, ' + 'At current periphery: {1}. Next update after: {2} sec. All periods: {3}'.format(str(self._battlesAvailable), str(self._currServerAvailable), str(currentPeriod), str(periods))
