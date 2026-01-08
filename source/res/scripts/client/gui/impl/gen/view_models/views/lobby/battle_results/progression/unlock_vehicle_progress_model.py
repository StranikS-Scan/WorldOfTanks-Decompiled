# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/unlock_vehicle_progress_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class UnlockVehicleProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(UnlockVehicleProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceItemModel

    def getVehicleId(self):
        return self._getNumber(1)

    def setVehicleId(self, value):
        self._setNumber(1, value)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getVehicleIcon(self):
        return self._getString(3)

    def setVehicleIcon(self, value):
        self._setString(3, value)

    def getVehicleType(self):
        return self._getString(4)

    def setVehicleType(self, value):
        self._setString(4, value)

    def getNationName(self):
        return self._getString(5)

    def setNationName(self, value):
        self._setString(5, value)

    def getLevel(self):
        return self._getNumber(6)

    def setLevel(self, value):
        self._setNumber(6, value)

    def getAvgBattlesTillUnlock(self):
        return self._getNumber(7)

    def setAvgBattlesTillUnlock(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(UnlockVehicleProgressModel, self)._initialize()
        self._addViewModelProperty('price', PriceItemModel())
        self._addNumberProperty('vehicleId', 0)
        self._addStringProperty('userName', '')
        self._addStringProperty('vehicleIcon', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('nationName', '')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('avgBattlesTillUnlock', 0)
