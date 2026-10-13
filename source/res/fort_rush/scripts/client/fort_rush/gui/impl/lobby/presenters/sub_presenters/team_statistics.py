# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/sub_presenters/team_statistics.py
from __future__ import absolute_import
import typing
from fort_rush_common.fort_rush_constants import ARENA_BONUS_TYPE
from fort_rush.gui.fort_rush_presenters_packers import FortRushTeamEfficiency
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.battle_team_stats_model import BattleTeamStatsModel
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.battle_results.pbs_helpers.team_stats_helpers import getPlayerContextMenuArgs
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow
from gui.impl.gen import R
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class FortRushTeamStatisticsSubPresenter(BattleResultsSubPresenter):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    @classmethod
    def getViewModelType(cls):
        return BattleTeamStatsModel

    def packBattleResults(self, battleResults):
        FortRushTeamEfficiency.packModel(self.getViewModel(), battleResults)

    def createContextMenu(self, event):
        if event.contentID != R.views.common.BackportContextMenu():
            return
        databaseID = int(event.getArgument('databaseID', default=-1))
        if databaseID == self.__connectionMgr.databaseID:
            return
        contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, self.__getContextMenuArgs(databaseID, None))
        if contextMenuData is not None:
            window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            window.load()
            return window
        else:
            return

    def _getEvents(self):
        return ((self.getViewModel().onStatsSorted, self.__onTeamStatsSorted),)

    def __getContextMenuArgs(self, databaseID, vehicleCD):
        reusable = self.getBattleResults().reusable
        return getPlayerContextMenuArgs(reusable, databaseID, vehicleCD)

    def __onTeamStatsSorted(self, event):
        column = event.get('column')
        sortDirection = event.get('sortDirection')
        self._battleResults.saveStatsSorting(ARENA_BONUS_TYPE.FORT_RUSH, column, sortDirection)
