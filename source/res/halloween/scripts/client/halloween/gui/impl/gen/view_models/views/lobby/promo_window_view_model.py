# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/promo_window_view_model.py
from frameworks.wulf import ViewModel

class PromoWindowViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=7, commands=1):
        super(PromoWindowViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleUserName(self):
        return self._getString(0)

    def setVehicleUserName(self, value):
        self._setString(0, value)

    def getVehicleLevel(self):
        return self._getString(1)

    def setVehicleLevel(self, value):
        self._setString(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getVehicleIsPremium(self):
        return self._getBool(3)

    def setVehicleIsPremium(self, value):
        self._setBool(3, value)

    def getStartDate(self):
        return self._getNumber(4)

    def setStartDate(self, value):
        self._setNumber(4, value)

    def getEndDate(self):
        return self._getNumber(5)

    def setEndDate(self, value):
        self._setNumber(5, value)

    def getRegularArtefactsLength(self):
        return self._getNumber(6)

    def setRegularArtefactsLength(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(PromoWindowViewModel, self)._initialize()
        self._addStringProperty('vehicleUserName', '')
        self._addStringProperty('vehicleLevel', '')
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('vehicleIsPremium', False)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('regularArtefactsLength', 0)
        self.onClose = self._addCommand('onClose')
