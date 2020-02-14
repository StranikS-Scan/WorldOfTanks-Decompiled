# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prime_time_servers_data_provider.py
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider

class PrimeTimesServersDataProvider(ServersDataProvider):

    def __init__(self, primeTimesForDay):
        super(PrimeTimesServersDataProvider, self).__init__()
        self.primeTimes = None
        self.__maxPeriodLen = 0
        self.updatePrimeTimes(primeTimesForDay)
        return

    def updatePrimeTimes(self, primeTimesForDay):
        self.primeTimes = primeTimesForDay
        self.__maxPeriodLen = self.__getMaxPrimeTimes()

    def getDefaultSelectedServer(self, serversList):
        periodStartMin = None
        chosenServer = None
        getByPing = False
        for server in serversList:
            serverPeriods = self.primeTimes[server['shortname']]
            for periodStart, _ in serverPeriods:
                if periodStartMin is None:
                    chosenServer = server['id']
                    periodStartMin = periodStart
                if periodStart < periodStartMin:
                    chosenServer = server['id']
                    periodStartMin = periodStart
                if periodStart == periodStartMin:
                    chosenServer = None
                    getByPing = True

        if not getByPing or not serversList:
            return chosenServer
        elif getByPing:
            minPingServer = serversList[0]
            for server in serversList:
                if server['pingValue'] < minPingServer['pingValue']:
                    minPingServer = server

            return minPingServer['id']
        else:
            return

    def _makeVO(self, index, item):
        vo = super(PrimeTimesServersDataProvider, self)._makeVO(index, item)
        serverName = item.get('shortname')
        serverPeriods = []
        for scheduleServerNames in self.primeTimes.keys():
            if serverName in scheduleServerNames:
                serverPeriods = self.primeTimes[scheduleServerNames]

        periodsStr = []
        frmt = backport.getShortTimeFormat
        if serverPeriods:
            for periodStart, periodEnd in serverPeriods:
                periodsStr.append(backport.text(R.strings.ranked_battles.calendarDay.time(), start=frmt(periodStart), end=frmt(periodEnd)))

        else:
            periodsStr = backport.text(R.strings.common.common.dash())
        vo['shortname'] = item['shortname']
        vo['schedules'] = '\n'.join(periodsStr)
        vo['selected'] = False
        vo['maxPrimeTimes'] = self.__maxPeriodLen
        return vo

    def __getMaxPrimeTimes(self):
        if self.primeTimes:
            return max([ len(serverPeriods) for serverPeriods in self.primeTimes.values() ])
