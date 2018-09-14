# Embedded file name: scripts/client/gui/shared/fortifications/fort_hours_ctrlr.py
from ConnectionManager import connectionManager
import Event
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.LobbyContext import g_lobbyContext
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import time_utils

def isSortiesAvailableNow():
    serverStngs = g_lobbyContext.getServerSettings()
    return not isHourInForbiddenList(serverStngs.getForbiddenSortieHours())


def isHourInForbiddenList(hours, currUtcTimeHour = None):
    if currUtcTimeHour is not None:
        cTime = currUtcTimeHour
    else:
        cTime = time_utils.getTimeStructInUTC(None).tm_hour
    return cTime in hours


def getForbiddenPeriods(hours, formatter = None):
    guiData = []

    def _getEndHour(hour):
        hour = hour + 1
        if hour < time_utils.HOURS_IN_DAY:
            return hour
        return 0

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
            elif h - currRange[1] > 1:
                guiData.append(_formatPeriod(currRange[0], _getEndHour(currRange[1])))
                currRange = [h, h]
            else:
                currRange[1] = h

        guiData.append(_formatPeriod(currRange[0], _getEndHour(currRange[1])))
    return guiData


def getUpdatePeriods(forbiddenUTCHours, localTimestamp = None):

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
            elif i != time_utils.HOURS_IN_DAY:
                hoursTillUpdate += 1
            else:
                outcomePeriods.append((hoursTillUpdate + 1 + hoursTillFirstUpdate) * time_utils.ONE_HOUR)

        secondsLeft = time_utils.ONE_HOUR - (utc.tm_min * time_utils.ONE_MINUTE + utc.tm_sec)
        firstPeriod = hoursTillFirstUpdate * time_utils.ONE_HOUR + secondsLeft
    return (firstPeriod, outcomePeriods)


class FortHoursController:

    def start(self):
        g_clientUpdateManager.addCallbacks({'serverSettings': self._onChanged})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _onChanged(self, diff = None):
        pass


class SortiesCurfewController(FortHoursController, Notifiable):

    def __init__(self, notifierClass = None):
        Notifiable.__init__(self)
        self.__sortiesAvailable = None
        self.__currServerAvailable = None
        self.onStatusChanged = Event.Event()
        notifier = notifierClass or SimpleNotifier
        self.addNotificator(notifier(self.__getClosestUpdatePeriod, self.__notificatorUpdated))
        self.__currentPeriod = 0
        self.__periods = None
        return

    def getStatus(self):
        if self.__sortiesAvailable is None:
            self.__calcStatus()
        return (self.__sortiesAvailable, self.__currServerAvailable)

    def start(self):
        super(SortiesCurfewController, self).start()
        self.__update()
        LOG_DEBUG('Sorties controller started')

    def stop(self):
        self.onStatusChanged.clear()
        self.__periods = None
        super(SortiesCurfewController, self).stop()
        LOG_DEBUG('Sorties controller has been successfully stopped')
        return

    def _onChanged(self, diff = None):
        if diff and ('forbiddenSortieHours' in diff or 'forbiddenSortiePeripheryIDs' in diff):
            self.__update(diff.get('forbiddenSortieHours', None), diff.get('forbiddenSortiePeripheryIDs', None))
            LOG_DEBUG('Sorties settings changed:', diff)
        return

    def _getPeriodsInfo(self):
        return (self.__currentPeriod, self.__periods[:] if self.__periods else None)

    def _getForbiddenHours(self):
        servSettings = self.__getServerSettings()
        if servSettings:
            return servSettings.getForbiddenSortieHours()
        return []

    def _getTimeStamp(self):
        return None

    def __getClosestUpdatePeriod(self):
        return self.__currentPeriod

    def __update(self, forbHours = None, forbPeripheries = None):
        hours = forbHours
        if hours is None:
            hours = self._getForbiddenHours()
        self.__calcStatus(hours, forbPeripheries)
        if not self.__currServerAvailable:
            self.__currentPeriod, self.__periods = (0, 0)
            self.stopNotification()
        else:
            self.__currentPeriod, self.__periods = getUpdatePeriods(hours, self._getTimeStamp())
            self.startNotification()
        self.onStatusChanged()
        return

    def __notificatorUpdated(self):
        if self.__periods:
            self.__currentPeriod = self.__periods.pop(0)
            self.__periods.append(self.__currentPeriod)
        else:
            self.__currentPeriod = 0
        self.__calcStatus()
        self.startNotification()
        self.onStatusChanged()

    def __calcStatus(self, hours = None, servers = None):
        servSettings = self.__getServerSettings()
        if servers is None:
            servers = servSettings.getForbiddenSortiePeripheryIDs() if servSettings else []
        hours = hours or self._getForbiddenHours()
        utcHour = time_utils.getTimeStructInUTC(self._getTimeStamp()).tm_hour
        self.__sortiesAvailable = not isHourInForbiddenList(hours, utcHour)
        self.__currServerAvailable = connectionManager.peripheryID not in servers
        LOG_DEBUG('Sorties availability:', 'At current hour:', self.__sortiesAvailable, 'At current periphery:', self.__currServerAvailable)
        return

    def __getServerSettings(self):
        return g_lobbyContext.getServerSettings()

    def __str__(self):
        return 'SortiesController (%s)' % ('Sorties availability: At current hour: ' + str(self.__sortiesAvailable) + ', At current periphery: ' + str(self.__currServerAvailable) + '. Next update after: ' + str(self.__currentPeriod) + ' sec. All periods: ' + str(self.__periods))
