# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_style_availability_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CustomizationStyleAvailabilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CustomizationStyleAvailabilityModel, self).__init__(properties=properties, commands=commands)

    def getNations(self):
        return self._getArray(0)

    def setNations(self, value):
        self._setArray(0, value)

    @staticmethod
    def getNationsType():
        return unicode

    def getIsPremium(self):
        return self._getBool(1)

    def setIsPremium(self, value):
        self._setBool(1, value)

    def getIsPremiumIGR(self):
        return self._getBool(2)

    def setIsPremiumIGR(self, value):
        self._setBool(2, value)

    def getLevels(self):
        return self._getArray(3)

    def setLevels(self, value):
        self._setArray(3, value)

    @staticmethod
    def getLevelsType():
        return unicode

    def getVehTypes(self):
        return self._getArray(4)

    def setVehTypes(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehTypesType():
        return unicode

    def getTankNames(self):
        return self._getString(5)

    def setTankNames(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(CustomizationStyleAvailabilityModel, self)._initialize()
        self._addArrayProperty('nations', Array())
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isPremiumIGR', False)
        self._addArrayProperty('levels', Array())
        self._addArrayProperty('vehTypes', Array())
        self._addStringProperty('tankNames', '')
