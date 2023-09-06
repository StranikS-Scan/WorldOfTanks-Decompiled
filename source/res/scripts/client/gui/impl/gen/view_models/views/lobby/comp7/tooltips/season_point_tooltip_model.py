# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/season_point_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SeasonPointState(Enum):
    ACHIEVED = 'achieved'
    POSSIBLE = 'possible'
    NOTACHIEVED = 'notAchieved'


class SeasonPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SeasonPointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return SeasonPointState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getSeasonPointExchangeRate(self):
        return self._getNumber(1)

    def setSeasonPointExchangeRate(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(SeasonPointTooltipModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('seasonPointExchangeRate', 0)
