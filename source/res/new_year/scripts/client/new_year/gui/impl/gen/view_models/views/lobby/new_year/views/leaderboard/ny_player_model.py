# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_player_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PositionType(Enum):
    NOCHANGES = 'noChanges'
    UP = 'up'
    DOWN = 'down'


class NyPlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyPlayerModel, self).__init__(properties=properties, commands=commands)

    def getPositionType(self):
        return PositionType(self._getString(0))

    def setPositionType(self, value):
        self._setString(0, value.value)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getPosition(self):
        return self._getNumber(2)

    def setPosition(self, value):
        self._setNumber(2, value)

    def getScore(self):
        return self._getNumber(3)

    def setScore(self, value):
        self._setNumber(3, value)

    def getTop(self):
        return self._getNumber(4)

    def setTop(self, value):
        self._setNumber(4, value)

    def getStartPos(self):
        return self._getNumber(5)

    def setStartPos(self, value):
        self._setNumber(5, value)

    def getEndPos(self):
        return self._getNumber(6)

    def setEndPos(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(NyPlayerModel, self)._initialize()
        self._addStringProperty('positionType')
        self._addStringProperty('userName', '')
        self._addNumberProperty('position', 0)
        self._addNumberProperty('score', 0)
        self._addNumberProperty('top', 0)
        self._addNumberProperty('startPos', 0)
        self._addNumberProperty('endPos', 0)
