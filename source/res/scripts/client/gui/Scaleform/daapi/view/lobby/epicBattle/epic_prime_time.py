# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_prime_time.py
from constants import Configs
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.EpicPrimeTimeMeta import EpicPrimeTimeMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.event_dispatcher import showHangar
from gui.shared.formatters import text_styles, time_formatters
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext

class EpicBattleServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IEpicBattleMetaGameController)

    def _buildTooltip(self, peripheryID):
        if not self.getTimeLeft():
            tooltipStr = text_styles.expText(backport.text(R.strings.epic_battle.primeTime.endOfCycle(), server=self.getName()))
        else:
            timeStr = text_styles.neutral(time_formatters.getTillTimeByResource(self.getTimeLeft(), R.strings.menu.Time.timeValueShort))
            if self._getIsAvailable():
                tooltipStr = text_styles.expText(backport.text(R.strings.epic_battle.primeTime.serverTooltip(), server=self.getName(), time=timeStr))
            else:
                tooltipStr = text_styles.expText(backport.text(R.strings.epic_battle.primeTime.serverUnavailableTooltip(), time=timeStr))
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}

    def isEnabled(self):
        return self.isActive()


class EpicBattlesPrimeTimeView(EpicPrimeTimeMeta):
    _serverPresenterClass = EpicBattleServerPresenter
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def _populate(self):
        super(EpicBattlesPrimeTimeView, self)._populate()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.as_setHeaderTextS(backport.text(R.strings.epic_battle.primeTime.title()))
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.epicBattles.primeTime.prime_time_back_default()))

    def _dispose(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        super(EpicBattlesPrimeTimeView, self)._dispose()

    def _isAlertBGVisible(self):
        return not self.__epicController.hasAvailablePrimeTimeServers()

    def _getController(self):
        return self.__epicController

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': text_styles.grandTitle(self.__getStatusText()),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo)),
         'showAlertBG': not self._getController().hasAvailablePrimeTimeServers()}

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.EPIC

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.EPIC

    def __getStatusText(self):
        if not self._getController().hasAvailablePrimeTimeServers():
            return backport.text(R.strings.epic_battle.primeTime.status.noPrimeTimesOnAllServers())
        else:
            currServerName = self._connectionMgr.serverUserName
            primeTime = self._getController().getPrimeTimes().get(self._connectionMgr.peripheryID)
            timestamp, status = self._getController().getCurrentCycleInfo()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if status and primeTime:
                startTime = primeTime.getNextPeriodStart(currTime, timestamp)
                if startTime:
                    if startTime - currTime > time_utils.ONE_DAY:
                        startTimeStr = backport.getShortDateFormat(startTime)
                    else:
                        startTimeStr = backport.getShortTimeFormat(startTime)
                    return backport.text(R.strings.epic_battle.primeTime.status.noPrimeTimeOnThisServer(), startTime=startTimeStr, server=currServerName)
            season = self._getController().getCurrentSeason()
            if season is not None and primeTime is not None:
                lastCycle = season.getLastActiveCycleInfo(currTime)
                if lastCycle:
                    return self._getCycleFinishedOnThisServerText(cycleNumber=lastCycle.ordinalNumber, serverName=currServerName)
            return backport.text(R.strings.epic_battle.primeTime.status.disabledOnThisServer(), server=currServerName)

    def __getTimeText(self, serverInfo):
        if serverInfo:
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getName()
        else:
            _, timeLeft, isAvailable = self._getController().getPrimeTimeStatus()
            serverName = ''
        currentSeason = self._getController().getCurrentSeason()
        if currentSeason and not timeLeft:
            return backport.text(R.strings.epic_battle.primeTime.endOfCycle(), server=serverName)
        if not timeLeft and not isAvailable and not currentSeason:
            nextSeason = self._getController().getNextSeason()
            if nextSeason:
                currTime = time_utils.getCurrentLocalServerTimestamp()
                primeTime = self._getController().getPrimeTimes().get(serverInfo.getPeripheryID())
                startTime = primeTime.getNextPeriodStart(currTime, nextSeason.getEndDate())
                if startTime:
                    timeLeft = startTime - currTime
            else:
                self.destroy()
                return ''
        timeLeftStr = time_formatters.getTillTimeByResource(timeLeft, R.strings.menu.Time.timeValueShort)
        if isAvailable:
            stringR = R.strings.epic_battle.primeTime.primeIsAvailable()
        else:
            stringR = R.strings.epic_battle.primeTime.primeWillBeAvailable()
        return backport.text(stringR, server=serverName, time=text_styles.neutral(timeLeftStr))

    def _setHeaderText(self):
        self.as_setHeaderTextS(backport.text(self.__eventProgression.getPrimeTimeTitle()))

    def _setBackground(self):
        self.as_setBackgroundSourceS(backport.image(self.__eventProgression.getPrimeTimeBg()))

    def _getCycleFinishedOnThisServerText(self, cycleNumber, serverName):
        return backport.text(R.strings.epic_battle.primeTime.status.cycleFinishedOnThisServer(), cycleNo=cycleNumber, server=serverName)

    def _onServerSettingsChange(self, diff):
        if diff.get(Configs.EPIC_CONFIG.value, {}).get('isEnabled') is False:
            showHangar()
