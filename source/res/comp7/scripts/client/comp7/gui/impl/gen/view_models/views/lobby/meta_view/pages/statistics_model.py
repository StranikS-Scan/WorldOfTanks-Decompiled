# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/statistics_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Rank
from frameworks.wulf import ViewModel

class StatisticsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(StatisticsModel, self).__init__(properties=properties, commands=commands)

    def getMaxAchievedRatingPoints(self):
        return self._getNumber(0)

    def setMaxAchievedRatingPoints(self, value):
        self._setNumber(0, value)

    def getMaxAchievedRank(self):
        return Rank(self._getNumber(1))

    def setMaxAchievedRank(self, value):
        self._setNumber(1, value.value)

    def getSoloBattlesCount(self):
        return self._getNumber(2)

    def setSoloBattlesCount(self, value):
        self._setNumber(2, value)

    def getSuperPlatoonBattlesCount(self):
        return self._getNumber(3)

    def setSuperPlatoonBattlesCount(self, value):
        self._setNumber(3, value)

    def getWinRate(self):
        return self._getReal(4)

    def setWinRate(self, value):
        self._setReal(4, value)

    def getWinsCount(self):
        return self._getNumber(5)

    def setWinsCount(self, value):
        self._setNumber(5, value)

    def getLossCount(self):
        return self._getNumber(6)

    def setLossCount(self, value):
        self._setNumber(6, value)

    def getDrawCount(self):
        return self._getNumber(7)

    def setDrawCount(self, value):
        self._setNumber(7, value)

    def getAverageDamageDealt(self):
        return self._getReal(8)

    def setAverageDamageDealt(self, value):
        self._setReal(8, value)

    def getAveragePrestige(self):
        return self._getReal(9)

    def setAveragePrestige(self, value):
        self._setReal(9, value)

    def getRecordDamageDealt(self):
        return self._getReal(10)

    def setRecordDamageDealt(self, value):
        self._setReal(10, value)

    def getRecordDamageDealtVehicleName(self):
        return self._getString(11)

    def setRecordDamageDealtVehicleName(self, value):
        self._setString(11, value)

    def getRecordPrestige(self):
        return self._getReal(12)

    def setRecordPrestige(self, value):
        self._setReal(12, value)

    def getRecordPrestigeVehicleName(self):
        return self._getString(13)

    def setRecordPrestigeVehicleName(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(StatisticsModel, self)._initialize()
        self._addNumberProperty('maxAchievedRatingPoints', 0)
        self._addNumberProperty('maxAchievedRank')
        self._addNumberProperty('soloBattlesCount', 0)
        self._addNumberProperty('superPlatoonBattlesCount', 0)
        self._addRealProperty('winRate', 0.0)
        self._addNumberProperty('winsCount', 0)
        self._addNumberProperty('lossCount', 0)
        self._addNumberProperty('drawCount', 0)
        self._addRealProperty('averageDamageDealt', 0.0)
        self._addRealProperty('averagePrestige', 0.0)
        self._addRealProperty('recordDamageDealt', 0.0)
        self._addStringProperty('recordDamageDealtVehicleName', '')
        self._addRealProperty('recordPrestige', 0.0)
        self._addStringProperty('recordPrestigeVehicleName', '')
