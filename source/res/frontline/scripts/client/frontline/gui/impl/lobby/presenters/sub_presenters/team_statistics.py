# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/sub_presenters/team_statistics.py
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_team_stats_model import BattleTeamStatsModel
from helpers import dependency
from frontline.gui.frontline_presenters_packers import FrontlineTeamEfficiency
from skeletons.connection_mgr import IConnectionManager
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.pbs_helpers.team_stats_helpers import getPlayerContextMenuArgs
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow
from gui.impl.gen import R
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class FrontlineTeamStatisticsSubPresenter(BattleResultsSubPresenter):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    @classmethod
    def getViewModelType(cls):
        return BattleTeamStatsModel

    def packBattleResults(self, battleResults):
        FrontlineTeamEfficiency.packModel(self.getViewModel(), battleResults)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            databaseID = int(event.getArgument('databaseID', default=-1))
            if databaseID == self.__connectionMgr.databaseID:
                return
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, self.__getContextMenuArgs(databaseID, None))
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
