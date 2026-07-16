# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/submodel_presenters/team_statistics.py
from __future__ import absolute_import
import typing
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_team_stats_model import Comp7LightTeamStatsModel
from comp7_light.gui.impl.lobby.battle_results.comp7_light_packers import Comp7LightTeamEfficiency
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.pbs_helpers.team_stats_helpers import getPlayerContextMenuArgs
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow
from gui.impl.gen import R
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class Comp7LightTeamStatisticsSubPresenter(BattleResultsSubPresenter):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    @classmethod
    def getViewModelType(cls):
        return Comp7LightTeamStatsModel

    def packBattleResults(self, battleResults):
        Comp7LightTeamEfficiency.packModel(self.getViewModel(), battleResults)

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
        self._battleResults.saveStatsSorting(ARENA_BONUS_TYPE.COMP7_LIGHT, column, sortDirection)
