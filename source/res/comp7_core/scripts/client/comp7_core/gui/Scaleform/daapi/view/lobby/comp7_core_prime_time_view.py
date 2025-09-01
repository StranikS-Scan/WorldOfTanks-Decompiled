# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/lobby/comp7_core_prime_time_view.py
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter, PrimeTimeViewBase
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.formatters import text_styles, time_formatters
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import time_utils

class Comp7CoreServerPresenter(ServerListItemPresenter):

    def isEnabled(self):
        return self.isActive()

    def _buildTooltip(self, peripheryID):
        if not self.getTimeLeft():
            tooltipStr = text_styles.expText(backport.text(R.strings.comp7_core.primeTimeView.endOfCycle(), server=self.getName()))
        else:
            timeStr = text_styles.neutral(backport.getTillTimeStringByRClass(self.getTimeLeft(), R.strings.menu.Time.timeValueShort.noLeadingZeroes))
            if self._getIsAvailable():
                tooltipStr = text_styles.expText(backport.text(R.strings.comp7_core.primeTimeView.serverTooltip(), server=self.getName(), time=timeStr))
            else:
                tooltipStr = text_styles.expText(backport.text(R.strings.comp7_core.primeTimeView.serverUnavailableTooltip(), time=timeStr, server=self.getName()))
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}


class Comp7CorePrimeTimeView(PrimeTimeViewBase):
    _RES_STATUS_ROOT = None
    _serverPresenterClass = Comp7CoreServerPresenter
    __BLUR_INTENSITY = 0.5

    def __init__(self, **kwargs):
        super(Comp7CorePrimeTimeView, self).__init__(**kwargs)
        self.__blur = None
        return

    @property
    def _seasonNameClazz(self):
        raise NotImplementedError

    def _populate(self):
        super(Comp7CorePrimeTimeView, self)._populate()
        self.__blur = CachedBlur(blurRadius=self.__BLUR_INTENSITY)
        self.__blur.enable()

    def _dispose(self):
        if self.__blur is not None:
            self.__blur.disable()
            self.__blur.fini()
        super(Comp7CorePrimeTimeView, self)._dispose()
        return

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
        actualServers = super(Comp7CorePrimeTimeView, self)._getActualServers()
        if len(actualServers) > 1:
            actualServers = [ server for server in actualServers if server.getPeripheryID() != self._connectionMgr.peripheryID ]
        return actualServers

    def __getStatusTitle(self):
        currServerName = self._connectionMgr.serverUserNameShort
        status, timeLeft, _ = self._getController().getPrimeTimeStatus()
        if not self._hasAvailableServers():
            return text_styles.grandTitle(backport.text(R.strings.comp7_core.primeTimeView.status.allServersDisabled()))
        if status == PrimeTimeStatus.NOT_AVAILABLE:
            if not timeLeft:
                season = comp7_core_model_helpers.getSeasonNameEnum(self._getController(), self._seasonNameClazz)
                return text_styles.grandTitle(backport.text(self._RES_STATUS_ROOT.seasonDisabled.dyn(season.value)(), server=currServerName))
            if timeLeft < time_utils.ONE_DAY:
                startTime = time_formatters.formatDate('%H:%M', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            else:
                startTime = time_formatters.formatDate('%d.%m.%Y', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            return text_styles.grandTitle(backport.text(R.strings.comp7_core.primeTimeView.status.untill(), startTime=startTime, server=currServerName))
        return text_styles.grandTitle(backport.text(R.strings.comp7_core.primeTimeView.status.disableFirst(), server=currServerName)) if status in (PrimeTimeStatus.FROZEN, PrimeTimeStatus.NOT_SET) else ''

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
                season = comp7_core_model_helpers.getSeasonNameEnum(self._getController(), self._seasonNameClazz)
                return backport.text(self._RES_STATUS_ROOT.seasonDisabled.dyn(season.value)(), server=serverName)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort.noLeadingZeroes)
            if isAvailable:
                resId = R.strings.comp7_core.primeTimeView.status.primeIsAvailable()
            else:
                resId = R.strings.comp7_core.primeTimeView.status.primeWillBeAvailable()
            return backport.text(resId, time=text_styles.neutral(timeLeftStr), server=serverName)
