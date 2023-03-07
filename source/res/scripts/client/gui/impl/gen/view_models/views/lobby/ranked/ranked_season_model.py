# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_season_model.py
from frameworks.wulf import ViewModel

class RankedSeasonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RankedSeasonModel, self).__init__(properties=properties, commands=commands)

    def getSeasonNumber(self):
        return self._getNumber(0)

    def setSeasonNumber(self, value):
        self._setNumber(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getIsValid(self):
        return self._getBool(3)

    def setIsValid(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(RankedSeasonModel, self)._initialize()
        self._addNumberProperty('seasonNumber', -1)
        self._addNumberProperty('startDate', -1)
        self._addNumberProperty('endDate', -1)
        self._addBoolProperty('isValid', False)
