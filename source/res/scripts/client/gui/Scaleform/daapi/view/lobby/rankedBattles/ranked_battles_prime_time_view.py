# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_prime_time_view.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.RankedPrimeTimeMeta import RankedPrimeTimeMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_SUBVIEW_SOUND_SPACE
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import formatDate
from helpers import dependency
from helpers import time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController

class RankedServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IRankedBattlesController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def _buildTooltip(self, peripheryID):
        return {'tooltip': '',
         'specialArgs': [peripheryID],
         'specialAlias': TOOLTIPS_CONSTANTS.RANKED_SERVER_PRIMETIME,
         'isSpecial': True}

    def isEnabled(self):
        return self.isActive()

    def __cmp__(self, other):
        peripheryID = self._connectionMgr.peripheryID
        result = cmp(self.getPeripheryID() == peripheryID, other.getPeripheryID() == peripheryID)
        return result if result else self.orderID - other.orderID


class RankedBattlesPrimeTimeView(RankedPrimeTimeMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    _COMMON_SOUND_SPACE = RANKED_SUBVIEW_SOUND_SPACE
    _serverPresenterClass = RankedServerPresenter

    def _getController(self):
        return self.__rankedController

    def _populate(self):
        super(RankedBattlesPrimeTimeView, self)._populate()
        self._setHeaderData()
        self._setBackground()

    def _setHeaderData(self):
        header = {'title': backport.text(R.strings.ranked_battles.rankedBattleView.title())}
        self.as_setHeaderDataS(header)

    def _setBackground(self):
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()))

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': self.__getStatusTitle(),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo, True)),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer,
         'timeText': text_styles.expText(self.__getTimeText(serverInfo))}

    def _getPrbActionName(self):
        return self._getPrbForcedActionName()

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.RANKED

    def __getStatusTitle(self):
        currServerName = self._connectionMgr.serverUserNameShort
        status, timeLeft, _ = self.__rankedController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_AVAILABLE:
            if not timeLeft:
                currentSeason = self.__rankedController.getCurrentSeason()
                return text_styles.grandTitle(backport.text(R.strings.ranked_battles.primeTime.status.seasonDisabled(), season=currentSeason.getUserName(), server=currServerName))
            if not self._hasAvailableServers():
                return text_styles.grandTitle(backport.text(R.strings.ranked_battles.primeTime.status.allServersDisabled()))
            startTime = formatDate('%H:%M', time_utils.getCurrentLocalServerTimestamp() + timeLeft)
            return text_styles.grandTitle(backport.text(R.strings.ranked_battles.primeTime.status.untill(), startTime=startTime, server=currServerName))
        return text_styles.grandTitle(backport.text(R.strings.ranked_battles.primeTime.status.disableFirst(), server=currServerName))

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
                return backport.text(R.strings.ranked_battles.primeTime.status.seasonDisabled(), season=controller.getCurrentSeason().getUserName(), server=serverName)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeValueShort)
            if isAvailable:
                resId = R.strings.ranked_battles.primeTime.status.primeIsAvailable()
            else:
                resId = R.strings.ranked_battles.primeTime.status.primeWillBeAvailable()
            return backport.text(resId, server=serverName, time=text_styles.neutral(timeLeftStr))
