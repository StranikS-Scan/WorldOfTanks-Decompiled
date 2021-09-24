# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_battles/wt_event_prime_time_view.py
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import text_styles, time_formatters
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase, ServerListItemPresenter
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameEventController

class WTEventServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IGameEventController)

    def isEnabled(self):
        return self.isActive()

    def _buildTooltip(self, peripheryID):
        if not self.getTimeLeft():
            tooltipStr = text_styles.expText(backport.text(R.strings.event.primeTime.endOfCycle(), server=self.getName()))
        else:
            timeStr = text_styles.neutral(backport.getTillTimeStringByRClass(self.getTimeLeft(), R.strings.menu.Time.timeValueShort.noLeadingZeroes))
            if self._getIsAvailable():
                tooltipStr = text_styles.expText(backport.text(R.strings.event.primeTime.serverTooltip(), server=self.getName(), time=timeStr))
            else:
                tooltipStr = text_styles.expText(backport.text(R.strings.event.primeTime.serverUnavailableTooltip(), server=self.getName(), time=timeStr))
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}


class WTEventPrimeTimeView(PrimeTimeViewBase):
    _serverPresenterClass = WTEventServerPresenter
    __eventController = dependency.descriptor(IGameEventController)

    def closeView(self):
        self.app.setBackgroundAlpha(0)
        self.destroy()

    def _getController(self):
        return self.__eventController

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': self.__getStatusTitle(),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo, True)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo)),
         'showAlertBG': not self.__eventController.hasAvailablePrimeTimeServers()}

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.EVENT_BATTLE

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.EVENT_BATTLE

    def __getStatusTitle(self):
        currServerName = self._connectionMgr.serverUserNameShort
        status, timeLeft, _ = self._getController().getPrimeTimeStatus()
        if not self._hasAvailableServers():
            return text_styles.grandTitle(backport.text(R.strings.event.primeTime.status.allServersDisabled()))
        if status == PrimeTimeStatus.NOT_AVAILABLE:
            if not timeLeft:
                return text_styles.grandTitle(backport.text(R.strings.event.primeTime.status.allServersDisabled()))
            if timeLeft < time_utils.ONE_DAY:
                startTime = time_formatters.formatDate('%H:%M', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            else:
                startTime = time_formatters.formatDate('%d.%m.%Y', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            return text_styles.grandTitle(backport.text(R.strings.event.primeTime.status.untill(), startTime=startTime, server=currServerName))
        return text_styles.grandTitle(backport.text(R.strings.event.primeTime.status.disableFirst(), server=currServerName)) if status in (PrimeTimeStatus.FROZEN, PrimeTimeStatus.NOT_SET) else text_styles.grandTitle(backport.text(R.strings.event.primeTime.status.allServersDisabled()))

    def __getTimeText(self, serverInfo):
        if serverInfo is None:
            return ''
        else:
            controller = self._getController()
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getShortName()
            currentSeason = controller.getCurrentSeason()
            if currentSeason and not timeLeft:
                return text_styles.grandTitle(backport.text(R.strings.event.primeTime.status.allServersDisabled()))
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort.noLeadingZeroes)
            if isAvailable:
                resId = R.strings.event.primeTime.status.primeIsAvailable()
            else:
                resId = R.strings.event.primeTime.status.primeWillBeAvailable()
            return backport.text(resId, time=text_styles.neutral(timeLeftStr), server=serverName)
