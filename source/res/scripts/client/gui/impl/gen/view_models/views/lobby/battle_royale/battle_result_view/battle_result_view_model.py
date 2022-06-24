# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/battle_result_view_model.py
from gui.impl.gen.view_models.views.battle_royale.battle_results.br_base_view_model import BrBaseViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_results_tab_model import BattleResultsTabModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.leaderboard_model import LeaderboardModel

class BattleResultViewModel(BrBaseViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BattleResultViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def personalResults(self):
        return self._getViewModel(2)

    @staticmethod
    def getPersonalResultsType():
        return BattleResultsTabModel

    @property
    def leaderboardLobbyModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getLeaderboardLobbyModelType():
        return LeaderboardModel

    def getMapName(self):
        return self._getString(4)

    def setMapName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BattleResultViewModel, self)._initialize()
        self._addViewModelProperty('personalResults', BattleResultsTabModel())
        self._addViewModelProperty('leaderboardLobbyModel', LeaderboardModel())
        self._addStringProperty('mapName', '')
