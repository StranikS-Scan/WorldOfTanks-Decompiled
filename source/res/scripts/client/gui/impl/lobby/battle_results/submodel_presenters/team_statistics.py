# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/team_statistics.py
import typing
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.pbs_helpers.team_stats_helpers import getPlayerContextMenuArgs
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_team_stats_model import RandomTeamStatsModel
from gui.impl.lobby.battle_results.random_packers import RandomTeamEfficiency
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class TeamStatisticsSubPresenter(BattleResultsSubPresenter):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    @classmethod
    def getViewModelType(cls):
        return RandomTeamStatsModel

    def packBattleResults(self, battleResults):
        RandomTeamEfficiency.packModel(self.getViewModel(), battleResults)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            databaseID = int(event.getArgument('databaseID', default=-1))
            if databaseID == self.__connectionMgr.databaseID:
                return
            vehicleCD = event.getArgument('vehicleCD', 0)
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, self.__getContextMenuArgs(databaseID, vehicleCD))
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return

    def _getEvents(self):
        return ((self.getViewModel().onStatsSorted, self.__onTeamStatsSorted),)

    def __getContextMenuArgs(self, databaseID, vehicleCD):
        reusable = self.getBattleResults().reusable
        return getPlayerContextMenuArgs(reusable, databaseID, vehicleCD)

    def __onTeamStatsSorted(self, event):
        column = event.get('column')
        sortDirection = event.get('sortDirection')
        self._battleResults.saveStatsSorting(self.parentView.arenaUniqueID, column, sortDirection)
