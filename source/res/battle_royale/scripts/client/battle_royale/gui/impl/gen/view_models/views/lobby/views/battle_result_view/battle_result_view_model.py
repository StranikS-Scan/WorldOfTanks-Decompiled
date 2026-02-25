# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/battle_result_view/battle_result_view_model.py
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.battle_results_tab_model import BattleResultsTabModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.leaderboard_model import LeaderboardModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.br_base_view_model import BrBaseViewModel

class BattleResultViewModel(BrBaseViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
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

    @property
    def eventInfo(self):
        return self._getViewModel(4)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    def getMapName(self):
        return self._getString(5)

    def setMapName(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(BattleResultViewModel, self)._initialize()
        self._addViewModelProperty('personalResults', BattleResultsTabModel())
        self._addViewModelProperty('leaderboardLobbyModel', LeaderboardModel())
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addStringProperty('mapName', '')
