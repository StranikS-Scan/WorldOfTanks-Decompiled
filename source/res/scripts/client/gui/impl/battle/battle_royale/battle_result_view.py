# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_royale/battle_result_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.auxiliary.battle_royale.battle_result_view_base import BrBattleResultsViewBase
from gui.impl.gen.view_models.views.battle.battle_royale.battle_result_view_model import BattleResultViewModel
from gui.server_events.battle_royale_formatters import BRSections
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BrBattleResultsViewInBattle(BrBattleResultsViewBase):
    __slots__ = ('__doingExit',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.battle.battle_royale.BattleResultView())
        settings.model = BattleResultViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BrBattleResultsViewInBattle, self).__init__(settings, *args, **kwargs)
        self.__doingExit = False

    @property
    def viewModel(self):
        return super(BrBattleResultsViewInBattle, self).getViewModel()

    @property
    def isInBattle(self):
        return self._data[BRSections.IN_BATTLE] if self._data is not None and BRSections.IN_BATTLE in self._data else False

    def _initialize(self, *args, **kwargs):
        super(BrBattleResultsViewInBattle, self)._initialize()
        self.__addListeners()

    def _onLoading(self, *args, **kwargs):
        super(BrBattleResultsViewInBattle, self)._onLoading()
        self.__doingExit = False
        self._setTabsData(self.viewModel)

    def _finalize(self):
        self.__removeListeners()
        super(BrBattleResultsViewInBattle, self)._finalize()

    def _getData(self, **kwargs):
        return kwargs.get('ctx', {}).get('data', {})

    def _getFinishReason(self):
        return self._data[BRSections.FINISH_REASON]

    def _getStats(self):
        return self._data[BRSections.STATS]

    def _getFinancialData(self):
        return self._data[BRSections.FINANCE]

    def _fillLeaderboardGroups(self, leaderboard, groupList):
        groupListData = leaderboard['group_list']
        for groupData in groupListData:
            points = groupData['rewardCount']
            place = groupData['place']
            group = groupData['players_list']
            isPersonalSquad = groupData['isPersonalSquad']
            self._fillLeaderbordGroup(groupList, group, points, place, isPersonalSquad)

    def __addListeners(self):
        self.viewModel.onHangarBtnClick += self.__doExitToHangar
        self.viewModel.onCloseBtnClick += self.__doExitToHangar

    def __removeListeners(self):
        self.viewModel.onHangarBtnClick -= self.__doExitToHangar
        self.viewModel.onCloseBtnClick -= self.__doExitToHangar

    def __doExitToHangar(self):
        if self.__doingExit:
            return
        self.__doingExit = True
        if self.isInBattle:
            sessionProvider = dependency.instance(IBattleSessionProvider)
            sessionProvider.exit()
        else:
            self.destroyWindow()
