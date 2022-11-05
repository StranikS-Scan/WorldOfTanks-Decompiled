# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_prime_time_view.py
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_SUBVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.RankedPrimeTimeMeta import RankedPrimeTimeMeta
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController

class RankedServerPresenter(ServerListItemPresenter):
    _RES_ROOT = R.strings.ranked_battles.primeTimes.serverTooltip
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __cmp__(self, other):
        peripheryID = self._connectionMgr.peripheryID
        result = cmp(self.getPeripheryID() == peripheryID, other.getPeripheryID() == peripheryID)
        return result if result else self.orderID - other.orderID


class RankedBattlesPrimeTimeView(RankedPrimeTimeMeta):
    _COMMON_SOUND_SPACE = RANKED_SUBVIEW_SOUND_SPACE
    _RES_ROOT = R.strings.ranked_battles.primeTimes
    _serverPresenterClass = RankedServerPresenter
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _getController(self):
        return self.__rankedController

    def _populate(self):
        super(RankedBattlesPrimeTimeView, self)._populate()
        header = {'title': backport.text(R.strings.ranked_battles.rankedBattleView.title())}
        self.as_setHeaderDataS(header)
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()))

    def _isAlertBGVisible(self):
        return False

    def _getPrbActionName(self):
        return self._getPrbForcedActionName()

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.RANKED
