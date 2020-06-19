# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/spg_event/prime_time_view.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWOTSPGController
from gui.Scaleform.daapi.view.meta.Event10YCPrimeTimeMeta import Event10YCPrimeTimeMeta

class SPGServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IWOTSPGController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def _buildTooltip(self, peripheryID):
        isNow = self._getIsAvailable()
        if isNow:
            timeLeftStr = backport.getTillTimeStringByRClass(self.getTimeLeft(), R.strings.menu.Time.timeValueShort)
            timeLeftStr = text_styles.neutral(timeLeftStr)
            timeText = backport.text(R.strings.spg_event.primeTime.tooltip.server.primeIsAvailable(), time=timeLeftStr)
        else:
            timeText = backport.text(R.strings.spg_event.primeTime.tooltip.server.primeNotAvailable())
        serverName = text_styles.expText(backport.text(R.strings.spg_event.primeTime.tooltip.server.onServer(), server=self.getShortName()))
        timeText = text_styles.expText(timeText)
        tooltipStr = '{}\n{}'.format(serverName, timeText)
        return {'tooltip': tooltipStr,
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}


class SPGEventPrimeTimeView(Event10YCPrimeTimeMeta):
    __eventController = dependency.descriptor(IWOTSPGController)
    _serverPresenterClass = SPGServerPresenter

    def _populate(self):
        super(SPGEventPrimeTimeView, self)._populate()
        self.__updateTitle()
        self.__updateBackground()

    def __updateTitle(self):
        self.as_setTitleS(backport.text(R.strings.spg_event.primeTime.title()))

    def __updateBackground(self):
        self.as_setBgS(backport.image(R.images.gui.maps.icons.tenYearsCountdown.bg.primeTime()))

    def _getController(self):
        return self.__eventController

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.RANDOM

    def _getPrbActionName(self):
        return self._getPrbForcedActionName()

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': self.__getStatusTitle(),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo, True)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo))}

    def __getStatusTitle(self):
        currServerName = self._connectionMgr.serverUserNameShort
        status, timeLeft, _ = self.__eventController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_AVAILABLE:
            if not timeLeft:
                return text_styles.grandTitle(backport.text(R.strings.spg_event.primeTime.status.disabled(), server=currServerName))
            if not self._hasAvailableServers():
                return text_styles.grandTitle(backport.text(R.strings.spg_event.primeTime.status.allServersDisabled()))
            return text_styles.grandTitle(backport.text(R.strings.spg_event.primeTime.status.untill(), server=currServerName))
        return text_styles.grandTitle(backport.text(R.strings.spg_event.primeTime.status.disabled(), server=currServerName))

    def __getTimeText(self, serverInfo):
        if serverInfo is None:
            return ''
        else:
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getShortName()
            if not timeLeft:
                return backport.text(R.strings.spg_event.primeTime.status.disabled(), server=serverName)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort)
            return backport.text(R.strings.spg_event.primeTime.status.primeIsAvailable(), server=serverName, time=text_styles.neutral(timeLeftStr)) if isAvailable else backport.text(R.strings.spg_event.primeTime.status.primeWillBeAvailable(), server=serverName)
