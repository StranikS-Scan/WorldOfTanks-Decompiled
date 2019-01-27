# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_prime_time.py
import BigWorld
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.EpicPrimeTimeMeta import EpicPrimeTimeMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import text_styles
from gui.shared.formatters.servers import makePingStatusIcon
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IEpicBattleMetaGameController

def _makeServerString(serverInfo):
    pingStr = text_styles.neutral(text_styles.concatStylesToSingleLine(serverInfo.getName(), ' (', text_styles.neutral(serverInfo.getPingValue()), makePingStatusIcon(serverInfo.getPingStatus()), ')'))
    return _ms(EPIC_BATTLE.PRIMETIME_ONESERVERAVAILABLE, serverPing=pingStr)


class FrontLineServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IEpicBattleMetaGameController)

    def _buildTooltip(self):
        if not self.getTimeLeft():
            return _ms(EPIC_BATTLE.PRIMETIME_ENDOFCYCLE, server=self.getName())
        timeStr = text_styles.neutral(time_utils.getTillTimeString(self.getTimeLeft(), MENU.TIME_TIMEVALUEWITHSECS))
        return _ms(EPIC_BATTLE.PRIMETIME_SERVERTOOLTIP, server=self._shortName, time=timeStr) if self._getIsAvailable() else _ms(EPIC_BATTLE.PRIMETIME_SERVERUNAVAILABLETOOLTIP, time=timeStr)

    def isEnabled(self):
        return self.isActive()


class EpicBattlesPrimeTimeView(EpicPrimeTimeMeta):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    _serverPresenterClass = FrontLineServerPresenter

    def _getController(self):
        return self.__epicController

    def _prepareData(self, serverList, serverInfo):
        if len(serverList) == 1:
            serversDDEnabled = serverDDVisible = False
            serversText = _makeServerString(serverInfo)
        else:
            serversDDEnabled = serverDDVisible = True
            serversText = EPIC_BATTLE.PRIMETIME_MANYSERVERSAVAILABLE
        isActiveOnOtherServers = self.__epicController.hasAvailablePrimeTimeServers()
        if self.__epicController.hasAvailablePrimeTimeServers():
            warningIconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ICON_CLOCK_100X100
        else:
            warningIconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_90X84
        return {'warningIconSrc': warningIconSrc,
         'status': text_styles.grandTitle(self.__getStatusText()),
         'serversText': text_styles.expText(serversText),
         'serversDDEnabled': serversDDEnabled,
         'serverDDVisible': serverDDVisible,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo)),
         'showAlertBG': isActiveOnOtherServers}

    def _getPrbActionName(self):
        if self._isEnabled:
            prbAction = PREBATTLE_ACTION_NAME.EPIC
        else:
            prbAction = PREBATTLE_ACTION_NAME.EPIC_FORCED
        return prbAction

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.EPIC_FORCED

    def __getStatusText(self):
        if not self.__epicController.hasAvailablePrimeTimeServers():
            return EPIC_BATTLE.PRIMETIME_STATUS_NOPRIMETIMESONALLSERVERS
        else:
            currServerName = self._connectionMgr.serverUserNameShort
            primeTime = self.__epicController.getPrimeTimes().get(self._connectionMgr.peripheryID)
            timestamp, status = self.__epicController.getCurrentCycleInfo()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if status and primeTime:
                startTime = primeTime.getNextPeriodStart(currTime, timestamp)
                if startTime:
                    if startTime - currTime > time_utils.ONE_DAY:
                        startTimeStr = BigWorld.wg_getShortDateFormat(startTime)
                    else:
                        startTimeStr = BigWorld.wg_getShortTimeFormat(startTime)
                    return _ms(EPIC_BATTLE.PRIMETIME_STATUS_NOPRIMETIMEONTHISSERVER, startTime=startTimeStr, server=currServerName)
            season = self.__epicController.getCurrentSeason()
            if season is not None and primeTime is not None:
                lastCycle = season.getLastActiveCycleInfo(currTime)
                if lastCycle:
                    return _ms(EPIC_BATTLE.PRIMETIME_STATUS_CYCLEFINISHEDONTHISSERVER, cycleNo=lastCycle.ordinalNumber, server=currServerName)
            return _ms(EPIC_BATTLE.PRIMETIME_STATUS_DISABLEDONTHISSERVER, server=currServerName)

    def __getTimeText(self, serverInfo):
        if serverInfo:
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getName()
        else:
            _, timeLeft, isAvailable = self.__epicController.getPrimeTimeStatus()
            serverName = ''
        currentSeason = self.__epicController.getCurrentSeason()
        if currentSeason and not timeLeft:
            return _ms(EPIC_BATTLE.PRIMETIME_ENDOFCYCLE, server=serverName)
        if not timeLeft and not isAvailable and not currentSeason:
            nextSeason = self.__epicController.getNextSeason()
            if nextSeason:
                currTime = time_utils.getCurrentLocalServerTimestamp()
                primeTime = self.__epicController.getPrimeTimes().get(serverInfo.getPeripheryID())
                startTime = primeTime.getNextPeriodStart(currTime, nextSeason.getEndDate())
                if startTime:
                    timeLeft = startTime - currTime
            else:
                self.destroy()
                return ''
        timeLeftStr = time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUESHORT)
        i18nKey = EPIC_BATTLE.PRIMETIME_PRIMEISAVAILABLE if isAvailable else EPIC_BATTLE.PRIMETIME_PRIMEWILLBEAVAILABLE
        return _ms(i18nKey, server=serverName, time=text_styles.neutral(timeLeftStr))
