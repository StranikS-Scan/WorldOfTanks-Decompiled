# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/stats_ctrl.py
import typing
from collections import namedtuple
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.reusable import _ReusableInfo
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)
BattleResults = namedtuple('BattleResults', ('results', 'reusable'))

class IBattleResultStatsCtrl(object):

    def clear(self):
        raise NotImplementedError

    def setResults(self, results, reusable):
        raise NotImplementedError

    def getVO(self):
        raise NotImplementedError

    def getBackportContextMenuData(self, databaseID, vehicleCD):
        pass

    def packModel(self, model, *args, **kwargs):
        pass

    def packTooltips(self, tooltipType, model, ctx=None):
        pass

    def updateModel(self, updateType, model, ctx=None, isFullUpdate=True):
        pass

    @staticmethod
    def onShowResults(arenaUniqueID):
        raise NotImplementedError

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        raise NotImplementedError
