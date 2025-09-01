# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/stats_ctrl.py
import typing
from collections import namedtuple
from frameworks.wulf import ViewModel
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)
BattleResults = namedtuple('BattleResults', ('results', 'reusable'))

class IBattleResultStatsCtrl(object):
    CTRL_IMPL_TYPE_GAMEFACE = 0
    CTRL_IMPL_TYPE_FLASH = 1

    def clear(self):
        raise NotImplementedError

    @property
    def ctrlImplType(self):
        return self.CTRL_IMPL_TYPE_FLASH

    def setResults(self, results, reusable):
        raise NotImplementedError

    def getResults(self):
        return None

    def getVO(self):
        raise NotImplementedError

    @staticmethod
    def onShowResults(arenaUniqueID):
        raise NotImplementedError

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        raise NotImplementedError
