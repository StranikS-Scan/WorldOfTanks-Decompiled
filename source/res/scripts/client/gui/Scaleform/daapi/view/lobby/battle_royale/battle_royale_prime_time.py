# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_prime_time.py
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_sounds import BATTLE_ROYALE_OVERLAY_SOUND_SPACE
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
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IBattleRoyaleController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def _buildTooltip(self, peripheryID):
        return {'tooltip': '',
         'specialArgs': [peripheryID],
         'specialAlias': TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SERVER_PRIME_TIME,
         'isSpecial': True}

    def isEnabled(self):
        return self.isActive()

    def __cmp__(self, other):
        peripheryID = self._connectionMgr.peripheryID
        result = cmp(self.getPeripheryID() == peripheryID, other.getPeripheryID() == peripheryID)
        return result if result else self.orderID - other.orderID


class BattleRoyalePrimeTimeView(RankedPrimeTimeMeta):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)
    _COMMON_SOUND_SPACE = BATTLE_ROYALE_OVERLAY_SOUND_SPACE
    _serverPresenterClass = BattleRoyaleServerPresenter

    def _getController(self):
        return self.__battleRoyale

    def _populate(self):
        super(BattleRoyalePrimeTimeView, self)._populate()
        self._setHeaderData()
        self._setBackground()

    def _setHeaderData(self):
        header = {'title': backport.text(R.strings.battle_royale.event.name())}
        self.as_setHeaderDataS(header)

    def _setBackground(self):
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.battleRoyale.bg.main()))

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        if serverInfo is None and serverList:
            serverInfo = serverList[0]
        return {'warningIconSrc': self._getWarningIcon(),
         'status': self.__getStatusTitle(),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo))}

    def _getPrbActionName(self):
        return self._getPrbForcedActionName()

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.BATTLE_ROYALE

    def _getWarningIcon(self):
        if self._hasAvailableServers():
            icon = R.images.gui.maps.icons.library.icon_clock_100x100()
        else:
            icon = R.images.gui.maps.icons.library.icon_alert_90x84()
        return backport.image(icon)

    def __getStatusTitle(self):
        currServerName = self._connectionMgr.serverUserName
        primeTime = self.__battleRoyale.getPrimeTimes().get(self._connectionMgr.peripheryID)
        if primeTime:
            if not self._hasAvailableServers():
                status = backport.text(R.strings.battle_royale.primeTime.status.allServersDisabled())
            else:
                currTime = time_utils.getCurrentLocalServerTimestamp()
                currentCycleEnd = self.__battleRoyale.getCurrentSeason().getCycleEndDate()
                period = primeTime.getNextPeriodStart(currTime, currentCycleEnd)
                startTime = formatDate('%H:%M', period)
                status = backport.text(R.strings.battle_royale.primeTime.status.untill(), startTime=startTime, server=currServerName)
        elif self.__battleRoyale.hasConfiguredPrimeTimeServers():
            status = backport.text(R.strings.battle_royale.primeTime.status.disableFirst(), server=currServerName)
        else:
            status = backport.text(R.strings.battle_royale.primeTime.status.allServersDisabled())
        return text_styles.grandTitle(status)

    def __getTimeText(self, serverInfo):
        controller = self._getController()
        if serverInfo:
            timeLeft = serverInfo.getTimeLeft()
            isAvailable = serverInfo.isAvailable()
            serverName = serverInfo.getName()
        else:
            return ''
        currentSeason = controller.getCurrentSeason()
        if currentSeason and not timeLeft:
            return backport.text(R.strings.battle_royale.primeTime.status.seasonDisabled(), server=serverName)
        if isAvailable:
            resId = R.strings.battle_royale.primeTime.status.primeIsAvailable()
        else:
            resId = R.strings.battle_royale.primeTime.status.primeWillBeAvailable()
        timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort)
        return backport.text(resId, server=serverName, time=text_styles.neutral(timeLeftStr))
