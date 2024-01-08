# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/season_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SeasonPointState(Enum):
    ACHIEVED = 'achieved'
    POSSIBLE = 'possible'
    NOTACHIEVED = 'notAchieved'


class SeasonName(Enum):
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class SeasonPointModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SeasonPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return SeasonPointState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getSeason(self):
        return SeasonName(self._getString(1))

    def setSeason(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(SeasonPointModel, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('season')
