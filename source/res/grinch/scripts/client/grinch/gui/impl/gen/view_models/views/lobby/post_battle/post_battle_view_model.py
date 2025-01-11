# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/lobby/post_battle/post_battle_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.post_battle_mission_model import PostBattleMissionModel
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.score_item_model import ScoreItemModel
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.score_player_model import ScorePlayerModel

class TeamPlaceIconEnum(Enum):
    NONE = ''
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class TeamColorEnum(Enum):
    YELLOW = 'yellow'
    CYAN = 'cyan'
    MAGENTA = 'magenta'


class PostBattleViewModel(ViewModel):
    __slots__ = ('onClose', 'onSelectedPlayerChange')

    def __init__(self, properties=12, commands=2):
        super(PostBattleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentPlayer(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentPlayerType():
        return ScorePlayerModel

    def getTeamColor(self):
        return TeamColorEnum(self._getString(1))

    def setTeamColor(self, value):
        self._setString(1, value.value)

    def getTeamPlace(self):
        return TeamPlaceIconEnum(self._getString(2))

    def setTeamPlace(self, value):
        self._setString(2, value.value)

    def getPlayerPlace(self):
        return self._getNumber(3)

    def setPlayerPlace(self, value):
        self._setNumber(3, value)

    def getBattleOverTimestamp(self):
        return self._getNumber(4)

    def setBattleOverTimestamp(self, value):
        self._setNumber(4, value)

    def getTotalCoinsEarned(self):
        return self._getNumber(5)

    def setTotalCoinsEarned(self, value):
        self._setNumber(5, value)

    def getDailyQuests(self):
        return self._getArray(6)

    def setDailyQuests(self, value):
        self._setArray(6, value)

    @staticmethod
    def getDailyQuestsType():
        return PostBattleMissionModel

    def getSelectedPlayerScoreItems(self):
        return self._getArray(7)

    def setSelectedPlayerScoreItems(self, value):
        self._setArray(7, value)

    @staticmethod
    def getSelectedPlayerScoreItemsType():
        return ScoreItemModel

    def getCyanPlayers(self):
        return self._getArray(8)

    def setCyanPlayers(self, value):
        self._setArray(8, value)

    @staticmethod
    def getCyanPlayersType():
        return ScorePlayerModel

    def getMagentaPlayers(self):
        return self._getArray(9)

    def setMagentaPlayers(self, value):
        self._setArray(9, value)

    @staticmethod
    def getMagentaPlayersType():
        return ScorePlayerModel

    def getYellowPlayers(self):
        return self._getArray(10)

    def setYellowPlayers(self, value):
        self._setArray(10, value)

    @staticmethod
    def getYellowPlayersType():
        return ScorePlayerModel

    def getTeamOrder(self):
        return self._getArray(11)

    def setTeamOrder(self, value):
        self._setArray(11, value)

    @staticmethod
    def getTeamOrderType():
        return TeamColorEnum

    def _initialize(self):
        super(PostBattleViewModel, self)._initialize()
        self._addViewModelProperty('currentPlayer', ScorePlayerModel())
        self._addStringProperty('teamColor', TeamColorEnum.YELLOW.value)
        self._addStringProperty('teamPlace', TeamPlaceIconEnum.NONE.value)
        self._addNumberProperty('playerPlace', 0)
        self._addNumberProperty('battleOverTimestamp', 0)
        self._addNumberProperty('totalCoinsEarned', 0)
        self._addArrayProperty('dailyQuests', Array())
        self._addArrayProperty('selectedPlayerScoreItems', Array())
        self._addArrayProperty('cyanPlayers', Array())
        self._addArrayProperty('magentaPlayers', Array())
        self._addArrayProperty('yellowPlayers', Array())
        self._addArrayProperty('teamOrder', Array())
        self.onClose = self._addCommand('onClose')
        self.onSelectedPlayerChange = self._addCommand('onSelectedPlayerChange')
