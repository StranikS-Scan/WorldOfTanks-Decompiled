# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_statistics_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class RankedStatisticsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RankedStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getTotalEfficiency(self):
        return self._getString(0)

    def setTotalEfficiency(self, value):
        self._setString(0, value)

    def getEfficiencyByDivision(self):
        return self._getArray(1)

    def setEfficiencyByDivision(self, value):
        self._setArray(1, value)

    @staticmethod
    def getEfficiencyByDivisionType():
        return unicode

    def getStagesCount(self):
        return self._getNumber(2)

    def setStagesCount(self, value):
        self._setNumber(2, value)

    def getBattlesCount(self):
        return self._getNumber(3)

    def setBattlesCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(RankedStatisticsModel, self)._initialize()
        self._addStringProperty('totalEfficiency', '')
        self._addArrayProperty('efficiencyByDivision', Array())
        self._addNumberProperty('stagesCount', 0)
        self._addNumberProperty('battlesCount', 0)
