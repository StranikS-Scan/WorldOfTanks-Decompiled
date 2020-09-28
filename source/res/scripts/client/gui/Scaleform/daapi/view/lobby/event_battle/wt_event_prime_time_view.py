# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_battle/wt_event_prime_time_view.py
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase
from gui.impl import backport
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IGameEventController

class WtEventServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IGameEventController)

    def _buildTooltip(self, peripheryID):
        rPrimeTime = R.strings.wt_event.primeTime
        if not self.getTimeLeft():
            tooltipStr = text_styles.expText(backport.text(rPrimeTime.endOfCycle(), server=self.getName()))
        else:
            timeStr = text_styles.neutral(backport.getTillTimeStringByRClass(self.getTimeLeft(), rPrimeTime.timeValue))
            if self._getIsAvailable():
                tooltipStr = text_styles.expText(backport.text(rPrimeTime.serverTooltip(), server=self.getName(), time=timeStr))
            else:
                tooltipStr = text_styles.expText(backport.text(rPrimeTime.server(), server=self.getName(), time=timeStr))
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}

    def isEnabled(self):
        return self.isActive()


class WtEventPrimeTimeView(PrimeTimeViewBase):
    __eventController = dependency.descriptor(IGameEventController)
    _serverPresenterClass = WtEventServerPresenter

    def _getController(self):
        return self.__eventController

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': text_styles.grandTitle(self.__getStatusText()),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo)),
         'showAlertBG': not self.__eventController.hasAvailablePrimeTimeServers()}

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.EVENT_BATTLE

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.EVENT_BATTLE

    def _getActualServers(self):
        activeServers = []
        currentServer = None
        for server in self._allServers.values():
            if server.isActive():
                if server.getPeripheryID() == self._connectionMgr.peripheryID:
                    currentServer = server
                else:
                    activeServers.append(server)

        if activeServers:
            return sorted(activeServers)
        else:
            return [currentServer] if currentServer else []

    def __getStatusText(self):
        rStatus = R.strings.wt_event.primeTime.status
        if not self.__eventController.hasAvailablePrimeTimeServers():
            return backport.text(rStatus.noPrimeTimesOnAllServers())
        else:
            currServerName = self._connectionMgr.serverUserName
            primeTime = self.__eventController.getPrimeTimes().get(self._connectionMgr.peripheryID)
            season = self.__eventController.getCurrentSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            timestamp = currTime + self.__eventController.getTimer()
            if season is not None and primeTime is not None:
                startTime = primeTime.getNextPeriodStart(currTime, timestamp)
                if startTime:
                    if startTime - currTime > time_utils.ONE_DAY:
                        startTimeStr = backport.getShortDateFormat(startTime)
                    else:
                        startTimeStr = backport.getShortTimeFormat(startTime)
                    return backport.text(rStatus.noPrimeTimeOnThisServer(), startTime=startTimeStr, server=currServerName)
            return backport.text(rStatus.disabledOnThisServer(), server=currServerName)

    def __getTimeText(self, serverInfo):
        rPrimeTime = R.strings.wt_event.primeTime
        if serverInfo:
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getName()
        else:
            _, timeLeft, isAvailable = self.__eventController.getPrimeTimeStatus()
            serverName = ''
        currentSeason = self.__eventController.getCurrentSeason()
        if currentSeason and not timeLeft:
            return backport.text(rPrimeTime.endOfCycle(), server=serverName)
        if not timeLeft and not isAvailable and not currentSeason:
            nextSeason = self.__eventController.getNextSeason()
            if nextSeason:
                currTime = time_utils.getCurrentLocalServerTimestamp()
                primeTime = self.__eventController.getPrimeTimes().get(serverInfo.getPeripheryID())
                startTime = primeTime.getNextPeriodStart(currTime, nextSeason.getEndDate())
                if startTime:
                    timeLeft = startTime - currTime
            else:
                self.destroy()
                return ''
        timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, rPrimeTime.timeValue)
        rKey = rPrimeTime.primeIsAvailable() if isAvailable else rPrimeTime.primeWillBeAvailable()
        return backport.text(rKey, server=serverName, time=text_styles.neutral(timeLeftStr))
