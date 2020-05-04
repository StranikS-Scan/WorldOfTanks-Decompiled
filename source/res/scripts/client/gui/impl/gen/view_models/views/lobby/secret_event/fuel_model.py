# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/fuel_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class FuelModel(ViewModel):
    __slots__ = ('onChangeBerlin',)

    def __init__(self, properties=6, commands=1):
        super(FuelModel, self).__init__(properties=properties, commands=commands)

    def getFuelCount(self):
        return self._getNumber(0)

    def setFuelCount(self, value):
        self._setNumber(0, value)

    def getIsBerlin(self):
        return self._getBool(1)

    def setIsBerlin(self, value):
        self._setBool(1, value)

    def getIsBerlinActive(self):
        return self._getBool(2)

    def setIsBerlinActive(self, value):
        self._setBool(2, value)

    def getIsDisabled(self):
        return self._getBool(3)

    def setIsDisabled(self, value):
        self._setBool(3, value)

    def getIsShowNotification(self):
        return self._getBool(4)

    def setIsShowNotification(self, value):
        self._setBool(4, value)

    def getTitle(self):
        return self._getResource(5)

    def setTitle(self, value):
        self._setResource(5, value)

    def _initialize(self):
        super(FuelModel, self)._initialize()
        self._addNumberProperty('fuelCount', 0)
        self._addBoolProperty('isBerlin', False)
        self._addBoolProperty('isBerlinActive', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isShowNotification', False)
        self._addResourceProperty('title', R.invalid())
        self.onChangeBerlin = self._addCommand('onChangeBerlin')
