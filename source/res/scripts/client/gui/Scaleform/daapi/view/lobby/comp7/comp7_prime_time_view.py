# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/comp7_prime_time_view.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.Comp7PrimeTimeMeta import Comp7PrimeTimeMeta
from helpers import dependency, time_utils
from skeletons.gui.game_control import IComp7Controller
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.periodic_battles.models import PrimeTimeStatus
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, time_formatters

class Comp7ServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IComp7Controller)

    def isEnabled(self):
        return self.isActive()

    def _buildTooltip(self, peripheryID):
        if not self.getTimeLeft():
            tooltipStr = text_styles.expText(backport.text(R.strings.comp7.primeTimeView.endOfCycle(), server=self.getName()))
        else:
            timeStr = text_styles.neutral(backport.getTillTimeStringByRClass(self.getTimeLeft(), R.strings.menu.Time.timeValueShort.noLeadingZeroes))
            if self._getIsAvailable():
                tooltipStr = text_styles.expText(backport.text(R.strings.comp7.primeTimeView.serverTooltip(), server=self.getName(), time=timeStr))
            else:
                tooltipStr = text_styles.expText(backport.text(R.strings.comp7.primeTimeView.serverUnavailableTooltip(), time=timeStr, server=self.getName()))
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}


class Comp7PrimeTimeView(Comp7PrimeTimeMeta):
    _serverPresenterClass = Comp7ServerPresenter
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _populate(self):
        super(Comp7PrimeTimeView, self)._populate()
        self.as_setHeaderTextS(backport.text(R.strings.comp7.primeTimeView.title()))
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.comp7.backgrounds.prime_time_back()))

    def _getController(self):
        return self.__comp7Ctrl

    def _startControllerListening(self):
        self._getController().onStatusUpdated += self._onControllerUpdated

    def _stopControllerListening(self):
        self._getController().onStatusUpdated -= self._onControllerUpdated

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': self.__getStatusTitle(),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo, True)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo))}

    def _getActualServers(self):
        actualServers = super(Comp7PrimeTimeView, self)._getActualServers()
        if len(actualServers) > 1:
            actualServers = [ server for server in actualServers if server.getPeripheryID() != self._connectionMgr.peripheryID ]
        return actualServers

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.COMP7

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.COMP7

    def __getStatusTitle(self):
        currServerName = self._connectionMgr.serverUserNameShort
        status, timeLeft, _ = self._getController().getPrimeTimeStatus()
        if not self._hasAvailableServers():
            return text_styles.grandTitle(backport.text(R.strings.comp7.primeTimeView.status.allServersDisabled()))
        if status == PrimeTimeStatus.NOT_AVAILABLE:
            if not timeLeft:
                return text_styles.grandTitle(backport.text(R.strings.comp7.primeTimeView.status.seasonDisabled(), server=currServerName))
            if timeLeft < time_utils.ONE_DAY:
                startTime = time_formatters.formatDate('%H:%M', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            else:
                startTime = time_formatters.formatDate('%d.%m.%Y', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            return text_styles.grandTitle(backport.text(R.strings.comp7.primeTimeView.status.untill(), startTime=startTime, server=currServerName))
        return text_styles.grandTitle(backport.text(R.strings.comp7.primeTimeView.status.disableFirst(), server=currServerName)) if status in (PrimeTimeStatus.FROZEN, PrimeTimeStatus.NOT_SET) else ''

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
                return backport.text(R.strings.comp7.primeTimeView.status.seasonDisabled(), server=serverName)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort.noLeadingZeroes)
            if isAvailable:
                resId = R.strings.comp7.primeTimeView.status.primeIsAvailable()
            else:
                resId = R.strings.comp7.primeTimeView.status.primeWillBeAvailable()
            return backport.text(resId, time=text_styles.neutral(timeLeftStr), server=serverName)
