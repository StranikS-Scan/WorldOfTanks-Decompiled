# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_prime_time.py
from constants import Configs
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.EpicPrimeTimeMeta import EpicPrimeTimeMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.shared.event_dispatcher import showHangar
from gui.impl import backport
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers import time_utils
from gui.impl.gen import R
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.lobby_context import ILobbyContext

class FrontLineServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IEventProgressionController)

    def _buildTooltip(self, peripheryID):
        if not self.getTimeLeft():
            tooltipStr = text_styles.expText(_ms(EPIC_BATTLE.PRIMETIME_ENDOFCYCLE, server=self.getName()))
        else:
            timeStr = text_styles.neutral(time_utils.getTillTimeString(self.getTimeLeft(), MENU.TIME_TIMEVALUESHORT))
            if self._getIsAvailable():
                tooltipStr = text_styles.expText(_ms(EPIC_BATTLE.PRIMETIME_SERVERTOOLTIP, server=self.getName(), time=timeStr))
            else:
                tooltipStr = text_styles.expText(_ms(EPIC_BATTLE.PRIMETIME_SERVERUNAVAILABLETOOLTIP, time=timeStr))
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}

    def isEnabled(self):
        return self.isActive()


class EpicBattlesPrimeTimeView(EpicPrimeTimeMeta):
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _serverPresenterClass = FrontLineServerPresenter

    def _populate(self):
        super(EpicBattlesPrimeTimeView, self)._populate()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._setHeaderText()
        self._setBackground()

    def _dispose(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(EpicBattlesPrimeTimeView, self)._dispose()

    def _getController(self):
        return self.__eventProgression

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
        if self._hasAvailableServers():
            prbAction = PREBATTLE_ACTION_NAME.EPIC
        else:
            prbAction = PREBATTLE_ACTION_NAME.EPIC_FORCED
        return prbAction

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.EPIC_FORCED

    def __getStatusText(self):
        if not self._getController().hasAvailablePrimeTimeServers():
            return EPIC_BATTLE.PRIMETIME_STATUS_NOPRIMETIMESONALLSERVERS
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
                    return _ms(EPIC_BATTLE.PRIMETIME_STATUS_NOPRIMETIMEONTHISSERVER, startTime=startTimeStr, server=currServerName)
            season = self._getController().getCurrentSeason()
            if season is not None and primeTime is not None:
                lastCycle = season.getLastActiveCycleInfo(currTime)
                if lastCycle:
                    return self._getCycleFinishedOnThisServerText(cycleNumber=lastCycle.ordinalNumber, serverName=currServerName)
            return _ms(EPIC_BATTLE.PRIMETIME_STATUS_DISABLEDONTHISSERVER, server=currServerName)

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
            return _ms(EPIC_BATTLE.PRIMETIME_ENDOFCYCLE, server=serverName)
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
        timeLeftStr = time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUESHORT)
        i18nKey = EPIC_BATTLE.PRIMETIME_PRIMEISAVAILABLE if isAvailable else EPIC_BATTLE.PRIMETIME_PRIMEWILLBEAVAILABLE
        return _ms(i18nKey, server=serverName, time=text_styles.neutral(timeLeftStr))

    def _setHeaderText(self):
        self.as_setHeaderTextS(backport.text(self.__eventProgression.getPrimeTimeTitle()))

    def _setBackground(self):
        self.as_setBackgroundSourceS(backport.image(self.__eventProgression.getPrimeTimeBg()))

    def _getCycleFinishedOnThisServerText(self, cycleNumber, serverName):
        return backport.text(R.strings.epic_battle.primeTime.status.cycleFinishedOnThisServer(), cycleNo=cycleNumber, server=serverName)

    def __onServerSettingsChange(self, diff):
        eventConfigKeys = (Configs.BATTLE_ROYALE_CONFIG.value, Configs.EVENT_PROGRESSION_CONFIG.value)
        isDisabled = any([ diff.get(config, {}).get('isEnabled') is False for config in eventConfigKeys ])
        if isDisabled:
            showHangar()
