# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_post_battle_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
from races.gui.impl.gen.view_models.views.lobby.player_information import PlayerInformation

class QuestsState(Enum):
    HASCOMPLETEDQUESTS = 'hasCompletedQuests'
    NOCOMLETEDQUESTS = 'noComletedQuests'
    NOPOINTS = 'noPoints'
    ALLQUESTSCOMPLETEDDAILY = 'allQuestsCompletedDaily'
    ALLQUESTSCOMPLETED = 'allQuestsCompleted'


class RacesPostBattleViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=6, commands=1):
        super(RacesPostBattleViewModel, self).__init__(properties=properties, commands=commands)

    def getPlayerId(self):
        return self._getNumber(0)

    def setPlayerId(self, value):
        self._setNumber(0, value)

    def getPlayerNickname(self):
        return self._getString(1)

    def setPlayerNickname(self, value):
        self._setString(1, value)

    def getBattleFinishDate(self):
        return self._getNumber(2)

    def setBattleFinishDate(self, value):
        self._setNumber(2, value)

    def getQuestsState(self):
        return QuestsState(self._getString(3))

    def setQuestsState(self, value):
        self._setString(3, value.value)

    def getPlayers(self):
        return self._getArray(4)

    def setPlayers(self, value):
        self._setArray(4, value)

    @staticmethod
    def getPlayersType():
        return PlayerInformation

    def getDailyQuests(self):
        return self._getArray(5)

    def setDailyQuests(self, value):
        self._setArray(5, value)

    @staticmethod
    def getDailyQuestsType():
        return DailyQuestModel

    def _initialize(self):
        super(RacesPostBattleViewModel, self)._initialize()
        self._addNumberProperty('playerId', 0)
        self._addStringProperty('playerNickname', '')
        self._addNumberProperty('battleFinishDate', 0)
        self._addStringProperty('questsState')
        self._addArrayProperty('players', Array())
        self._addArrayProperty('dailyQuests', Array())
        self.onClose = self._addCommand('onClose')
