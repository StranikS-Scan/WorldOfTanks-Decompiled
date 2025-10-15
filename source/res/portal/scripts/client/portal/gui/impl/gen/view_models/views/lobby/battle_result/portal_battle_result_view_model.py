# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/battle_result/portal_battle_result_view_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.leader_board.leaderboard_model import LeaderboardModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.personal_results_model import PersonalResultsModel

class FinishResultType(Enum):
    DEFAULT_WIN = 'default_win'
    SUPER_BOSS_WIN = 'super_boss_win'
    TIME_OUT_DEFEAT = 'timeout_defeat'
    PLAYER_BASE_CAPTURED_DEFEAT = 'player_base_captured_defeat'
    TECHNICAL_DEFEAT = 'technical_defeat'


class PortalBattleResultViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=11, commands=1):
        super(PortalBattleResultViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def playerResultsModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayerResultsModelType():
        return PersonalResultsModel

    @property
    def leaderboardModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getLeaderboardModelType():
        return LeaderboardModel

    def getFinishResultTitle(self):
        return self._getResource(2)

    def setFinishResultTitle(self, value):
        self._setResource(2, value)

    def getFinishResultType(self):
        return FinishResultType(self._getString(3))

    def setFinishResultType(self, value):
        self._setString(3, value.value)

    def getFinishResultDescr(self):
        return self._getString(4)

    def setFinishResultDescr(self, value):
        self._setString(4, value)

    def getBattleDifficulty(self):
        return self._getNumber(5)

    def setBattleDifficulty(self, value):
        self._setNumber(5, value)

    def getPlayerName(self):
        return self._getString(6)

    def setPlayerName(self, value):
        self._setString(6, value)

    def getClanAbbrev(self):
        return self._getString(7)

    def setClanAbbrev(self, value):
        self._setString(7, value)

    def getBattleDuration(self):
        return self._getString(8)

    def setBattleDuration(self, value):
        self._setString(8, value)

    def getArenaStartDateTime(self):
        return self._getString(9)

    def setArenaStartDateTime(self, value):
        self._setString(9, value)

    def getPlayerVehicleName(self):
        return self._getString(10)

    def setPlayerVehicleName(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(PortalBattleResultViewModel, self)._initialize()
        self._addViewModelProperty('playerResultsModel', PersonalResultsModel())
        self._addViewModelProperty('leaderboardModel', LeaderboardModel())
        self._addResourceProperty('finishResultTitle', R.invalid())
        self._addStringProperty('finishResultType')
        self._addStringProperty('finishResultDescr', '')
        self._addNumberProperty('battleDifficulty', 0)
        self._addStringProperty('playerName', '')
        self._addStringProperty('clanAbbrev', '')
        self._addStringProperty('battleDuration', '')
        self._addStringProperty('arenaStartDateTime', '')
        self._addStringProperty('playerVehicleName', '')
        self.onClose = self._addCommand('onClose')
