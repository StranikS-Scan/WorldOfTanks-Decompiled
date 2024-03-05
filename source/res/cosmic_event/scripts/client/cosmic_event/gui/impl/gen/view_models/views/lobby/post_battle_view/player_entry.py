# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/post_battle_view/player_entry.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringModel

class PlayerEntry(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PlayerEntry, self).__init__(properties=properties, commands=commands)

    def getPlayerName(self):
        return self._getString(0)

    def setPlayerName(self, value):
        self._setString(0, value)

    def getPlayerClan(self):
        return self._getString(1)

    def setPlayerClan(self, value):
        self._setString(1, value)

    def getTotalPoints(self):
        return self._getNumber(2)

    def setTotalPoints(self, value):
        self._setNumber(2, value)

    def getIsDeserter(self):
        return self._getBool(3)

    def setIsDeserter(self, value):
        self._setBool(3, value)

    def getPlace(self):
        return self._getNumber(4)

    def setPlace(self, value):
        self._setNumber(4, value)

    def getPlayersScore(self):
        return self._getArray(5)

    def setPlayersScore(self, value):
        self._setArray(5, value)

    @staticmethod
    def getPlayersScoreType():
        return ScoringModel

    def _initialize(self):
        super(PlayerEntry, self)._initialize()
        self._addStringProperty('playerName', '')
        self._addStringProperty('playerClan', '')
        self._addNumberProperty('totalPoints', 0)
        self._addBoolProperty('isDeserter', False)
        self._addNumberProperty('place', 1)
        self._addArrayProperty('playersScore', Array())
