# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/weekend_brawl/weekend_brawl_prime_time_view.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.RankedPrimeTimeMeta import RankedPrimeTimeMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import formatDate
from helpers import dependency
from helpers import time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWeekendBrawlController

class WeekendBrawlServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IWeekendBrawlController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def _buildTooltip(self, peripheryID):
        return {'tooltip': '',
         'specialArgs': [peripheryID],
         'specialAlias': TOOLTIPS_CONSTANTS.WEEKEND_BRAWL_SERVER_PRIMETIME,
         'isSpecial': True}

    def isEnabled(self):
        return self.isActive()

    def __cmp__(self, other):
        peripheryID = self._connectionMgr.peripheryID
        result = cmp(self.getPeripheryID() == peripheryID, other.getPeripheryID() == peripheryID)
        return result if result else self.orderID - other.orderID


class WeekendBrawlPrimeTimeView(RankedPrimeTimeMeta):
    __wBrawlController = dependency.descriptor(IWeekendBrawlController)
    _serverPresenterClass = WeekendBrawlServerPresenter
    _STR_PATH = R.strings.weekend_brawl

    def _getController(self):
        return self.__wBrawlController

    def _populate(self):
        super(WeekendBrawlPrimeTimeView, self)._populate()
        self._setHeaderData()

    def _setHeaderData(self):
        header = {'title': backport.text(self._STR_PATH.primeTime.header())}
        self.as_setHeaderDataS(header)

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        if serverInfo is None and serverList:
            serverInfo = serverList[0]
        return {'warningIconSrc': self._getWarningIcon(),
         'status': self.__getStatusTitle(),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo, True)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo)),
         'background': backport.image(R.images.gui.maps.icons.weekendBrawl.hangar.primeTimeView.bg())}

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.WEEKEND_BRAWL if self._hasAvailableServers() else PREBATTLE_ACTION_NAME.WEEKEND_BRAWL_FORCED

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.WEEKEND_BRAWL_FORCED

    def _getWarningIcon(self):
        if self._hasAvailableServers():
            icon = R.images.gui.maps.icons.library.icon_clock_100x100()
        else:
            icon = R.images.gui.maps.icons.library.icon_alert_90x84()
        return backport.image(icon)

    def __getStatusTitle(self):
        if not self._hasAvailableServers():
            self._STR_PATH.primeTime.status.allServersDisabled()
            status = backport.text(self._STR_PATH.primeTime.status.allServersDisabled())
        else:
            currServerName = self._connectionMgr.serverUserNameShort
            primeTime = self.__wBrawlController.getPrimeTimes().get(self._connectionMgr.peripheryID)
            if primeTime:
                currTime = time_utils.getCurrentLocalServerTimestamp()
                currentCycleEnd = self.__wBrawlController.getCurrentSeason().getCycleEndDate()
                period = primeTime.getNextPeriodStart(currTime, currentCycleEnd)
                startTime = formatDate('%H:%M', period)
                status = backport.text(self._STR_PATH.primeTime.status.until(), startTime=startTime, server=currServerName)
            else:
                status = backport.text(self._STR_PATH.primeTime.status.disableFirst(), server=currServerName)
        return text_styles.grandTitle(status)

    def __getTimeText(self, serverInfo):
        controller = self._getController()
        if serverInfo:
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getShortName()
        else:
            _, timeLeft, isAvailable = controller.getPrimeTimeStatus()
            serverName = ''
        currentCycleEnd = controller.getCurrentSeason().getCycleEndDate()
        if timeLeft == 0:
            return backport.text(self._STR_PATH.systemMessage.notAvailable.primeTimeNotSet())
        if isAvailable:
            resId = self._STR_PATH.primeTime.status.primeIsAvailable()
        elif currentCycleEnd:
            resId = self._STR_PATH.primeTime.status.primeWillBeAvailable()
        else:
            return ''
        timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort)
        return backport.text(resId, server=serverName, time=text_styles.neutral(timeLeftStr))
