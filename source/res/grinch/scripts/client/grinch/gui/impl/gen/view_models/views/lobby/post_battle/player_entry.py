# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/lobby/post_battle/player_entry.py
from frameworks.wulf import ViewModel

class PlayerEntry(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=5, commands=1):
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

    def _initialize(self):
        super(PlayerEntry, self)._initialize()
        self._addStringProperty('playerName', '')
        self._addStringProperty('playerClan', '')
        self._addNumberProperty('totalPoints', 0)
        self._addBoolProperty('isDeserter', False)
        self._addNumberProperty('place', 1)
        self.onClose = self._addCommand('onClose')
