# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/convertation_vehicle_tooltip_model.py
from frameworks.wulf import ViewModel

class ConvertationVehicleTooltipModel(ViewModel):
    __slots__ = ()
    MOBILIZATION = 'mobilization'
    DEFAULT = 'default'

    def __init__(self, properties=7, commands=0):
        super(ConvertationVehicleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getIsPremium(self):
        return self._getBool(5)

    def setIsPremium(self, value):
        self._setBool(5, value)

    def getPremiumVehicle(self):
        return self._getString(6)

    def setPremiumVehicle(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(ConvertationVehicleTooltipModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('type', '')
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('premiumVehicle', '')
