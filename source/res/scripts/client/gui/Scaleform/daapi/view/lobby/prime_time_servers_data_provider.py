# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prime_time_servers_data_provider.py
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider

class PrimeTimesServersDataProvider(ServersDataProvider):

    def __init__(self, primeTimesForDay):
        super(PrimeTimesServersDataProvider, self).__init__()
        self.primeTimes = primeTimesForDay
        self.__maxPeriodLen = self.__getMaxPrimeTimes()

    def getDefaultSelectedServer(self, serversList):
        if not serversList:
            return
        else:
            import random
            return random.choice(serversList)['id']

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
