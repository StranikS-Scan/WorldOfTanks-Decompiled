# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fun_random/fun_random_prime_time_view.py
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.RankedPrimeTimeMeta import RankedPrimeTimeMeta
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IFunRandomController

class FunRandomServerPresenter(ServerListItemPresenter):
    _RES_ROOT = R.strings.fun_random.primeTimes.serverTooltip
    _periodsController = dependency.descriptor(IFunRandomController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __cmp__(self, other):
        peripheryID = self._connectionMgr.peripheryID
        result = cmp(self.getPeripheryID() == peripheryID, other.getPeripheryID() == peripheryID)
        return result if result else self.orderID - other.orderID


class FunRandomPrimeTimeView(RankedPrimeTimeMeta):
    _RES_ROOT = R.strings.fun_random.primeTimes
    _serverPresenterClass = FunRandomServerPresenter
    __funRandomController = dependency.descriptor(IFunRandomController)

    def _getController(self):
        return self.__funRandomController

    def _populate(self):
        super(FunRandomPrimeTimeView, self)._populate()
        self.as_setHeaderDataS({'title': backport.text(R.strings.fun_random.primeTimes.title())})
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.fun_random.bg.prime_times()))

    def _isAlertBGVisible(self):
        return False

    def _getPrbActionName(self):
        return self._getPrbForcedActionName()

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.FUN_RANDOM
