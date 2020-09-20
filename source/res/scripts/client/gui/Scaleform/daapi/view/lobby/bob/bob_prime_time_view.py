# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/bob_prime_time_view.py
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
from skeletons.gui.game_control import IBobController

class BobServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IBobController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def _buildTooltip(self, peripheryID):
        return {'tooltip': '',
         'specialArgs': [peripheryID],
         'specialAlias': TOOLTIPS_CONSTANTS.BOB_SERVER_PRIMETIME,
         'isSpecial': True}

    def isEnabled(self):
        return self.isActive()

    def __cmp__(self, other):
        peripheryID = self._connectionMgr.peripheryID
        result = cmp(self.getPeripheryID() == peripheryID, other.getPeripheryID() == peripheryID)
        return result if result else self.orderID - other.orderID


class BobPrimeTimeView(RankedPrimeTimeMeta):
    __bobController = dependency.descriptor(IBobController)
    _serverPresenterClass = BobServerPresenter

    def _getController(self):
        return self.__bobController

    def _populate(self):
        super(BobPrimeTimeView, self)._populate()
        self._setHeaderData()

    def _setHeaderData(self):
        header = {'title': backport.text(R.strings.bob.primeTime.header())}
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
         'background': backport.image(R.images.gui.maps.icons.bob.hangar.primeTimeView.bg())}

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.BOB if self._hasAvailableServers() else PREBATTLE_ACTION_NAME.BOB_FORCED

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.BOB_FORCED

    def _getWarningIcon(self):
        if self._hasAvailableServers():
            icon = R.images.gui.maps.icons.library.icon_clock_100x100()
        else:
            icon = R.images.gui.maps.icons.library.icon_alert_90x84()
        return backport.image(icon)

    def __getStatusTitle(self):
        if not self._hasAvailableServers():
            R.strings.bob.primeTime.status.allServersDisabled()
            status = backport.text(R.strings.bob.primeTime.status.allServersDisabled())
        else:
            currServerName = self._connectionMgr.serverUserNameShort
            primeTime = self.__bobController.getPrimeTimes().get(self._connectionMgr.peripheryID)
            if primeTime:
                currTime = time_utils.getCurrentLocalServerTimestamp()
                currentCycleEnd = self.__bobController.getCurrentSeason().getCycleEndDate()
                period = primeTime.getNextPeriodStart(currTime, currentCycleEnd)
                startTime = formatDate('%H:%M', period)
                status = backport.text(R.strings.bob.primeTime.status.until(), startTime=startTime, server=currServerName)
            else:
                status = backport.text(R.strings.bob.primeTime.status.disableFirst(), server=currServerName)
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
            return backport.text(R.strings.bob.systemMessage.notAvailable.primeTimeNotSet())
        if isAvailable:
            resId = R.strings.bob.primeTime.status.primeIsAvailable()
        elif currentCycleEnd:
            resId = R.strings.bob.primeTime.status.primeWillBeAvailable()
        else:
            return ''
        timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort)
        return backport.text(resId, server=serverName, time=text_styles.neutral(timeLeftStr))
