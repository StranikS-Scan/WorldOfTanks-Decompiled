# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_team_stats.py
from __future__ import absolute_import
import typing
from constants import ARENA_BONUS_TYPE
from fun_random.gui.battle_results.packers.fun_packers import FunRandomTeamStats
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_team_stats_model import FunTeamStatsModel
from gui.battle_results.pbs_helpers.team_stats_helpers import getPlayerContextMenuArgs
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gen import R
from gui.impl.backport import BackportContextMenuWindow, createContextMenuData
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunTeamStatsSubPresenter(BattleResultsSubPresenter):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    _CONTEXT_MENU_TYPE = CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER

    @classmethod
    def getViewModelType(cls):
        return FunTeamStatsModel

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            FunRandomTeamStats.packModel(model, battleResults)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            databaseID = int(event.getArgument('databaseID', default=-1))
            if databaseID == self.__connectionMgr.databaseID:
                return
            vehicleCD = event.getArgument('vehicleCD')
            contextMenuData = self.__getBackportContextMenuData(databaseID, vehicleCD)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(FunTeamStatsSubPresenter, self).createContextMenu(event)

    def _getEvents(self):
        return super(FunTeamStatsSubPresenter, self)._getEvents() + ((self.getViewModel().onStatsSorted, self.__onTeamStatsSorted),)

    def __getBackportContextMenuData(self, databaseID, vehicleCD):
        return createContextMenuData(self._CONTEXT_MENU_TYPE, self.__getContextMenuArgs(databaseID, vehicleCD)) if self._CONTEXT_MENU_TYPE is not None else None

    def __getContextMenuArgs(self, databaseID, vehicleCD):
        return getPlayerContextMenuArgs(self.getBattleResults().reusable, databaseID, vehicleCD)

    def __onTeamStatsSorted(self, event):
        column = event.get('column')
        sortDirection = event.get('sortDirection')
        self._battleResults.saveStatsSorting(ARENA_BONUS_TYPE.FUN_RANDOM, column, sortDirection)
