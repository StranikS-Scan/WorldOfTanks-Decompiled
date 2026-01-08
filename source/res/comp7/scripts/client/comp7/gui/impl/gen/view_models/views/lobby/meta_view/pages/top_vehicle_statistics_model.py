# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/top_vehicle_statistics_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class TopVehicleStatisticsModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(TopVehicleStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getBattles(self):
        return self._getNumber(11)

    def setBattles(self, value):
        self._setNumber(11, value)

    def getWinSeries(self):
        return self._getReal(12)

    def setWinSeries(self, value):
        self._setReal(12, value)

    def getDamage(self):
        return self._getNumber(13)

    def setDamage(self, value):
        self._setNumber(13, value)

    def getAssist(self):
        return self._getNumber(14)

    def setAssist(self, value):
        self._setNumber(14, value)

    def getPrestigePoints(self):
        return self._getNumber(15)

    def setPrestigePoints(self, value):
        self._setNumber(15, value)

    def getMaxFrags(self):
        return self._getReal(16)

    def setMaxFrags(self, value):
        self._setReal(16, value)

    def getDestruction(self):
        return self._getReal(17)

    def setDestruction(self, value):
        self._setReal(17, value)

    def _initialize(self):
        super(TopVehicleStatisticsModel, self)._initialize()
        self._addNumberProperty('battles', 0)
        self._addRealProperty('winSeries', 0.0)
        self._addNumberProperty('damage', 0)
        self._addNumberProperty('assist', 0)
        self._addNumberProperty('prestigePoints', 0)
        self._addRealProperty('maxFrags', 0.0)
        self._addRealProperty('destruction', 0.0)
