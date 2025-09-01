# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/team_statistics.py
import typing
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
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
        contextMenuData = None
        if event.contentID == R.aliases.battle_result.contextMenu.Vehicle():
            vehicleId = event.getArgument('id')
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.PROFILE_VEHICLE, {'id': vehicleId})
        if event.contentID == R.aliases.battle_result.contextMenu.User():
            databaseID = int(event.getArgument('databaseID', default=-1))
            if databaseID != self.__connectionMgr.databaseID:
                vehicleCD = event.getArgument('vehicleCD')
                contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, self.__getContextMenuArgs(databaseID, vehicleCD))
        if contextMenuData is not None:
            window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(TeamStatisticsSubPresenter, self).createContextMenu(event)

    def _getEvents(self):
        return ((self.getViewModel().onStatsSorted, self.__onTeamStatsSorted),)

    def __getContextMenuArgs(self, databaseID, vehicleCD):
        reusable = self.getBattleResults().reusable
        playerInfo = reusable.players.getPlayerInfo(databaseID)
        return {'dbID': databaseID,
         'userName': playerInfo.realName,
         'clanAbbrev': playerInfo.clanAbbrev,
         'isAlly': playerInfo.team == reusable.getPersonalTeam(),
         'vehicleCD': vehicleCD,
         'wasInBattle': True,
         'clientArenaIdx': reusable.arenaUniqueID,
         'arenaType': reusable.common.arenaGuiType}

    def __onTeamStatsSorted(self, event):
        column = event.get('column')
        sortDirection = event.get('sortDirection')
        self._battleResults.saveStatsSorting(self.parentView.arenaUniqueID, column, sortDirection)
