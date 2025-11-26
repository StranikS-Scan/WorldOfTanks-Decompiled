# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/vehicle_menu_key_bindings_model.py
from frameworks.wulf import ViewModel

class VehicleMenuKeyBindingsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(VehicleMenuKeyBindingsModel, self).__init__(properties=properties, commands=commands)

    def getRetrainCrew(self):
        return self._getNumber(0)

    def setRetrainCrew(self, value):
        self._setNumber(0, value)

    def getQuickTraining(self):
        return self._getNumber(1)

    def setQuickTraining(self, value):
        self._setNumber(1, value)

    def getReturnCrew(self):
        return self._getNumber(2)

    def setReturnCrew(self, value):
        self._setNumber(2, value)

    def getAboutVehicle(self):
        return self._getNumber(3)

    def setAboutVehicle(self, value):
        self._setNumber(3, value)

    def getUpgrades(self):
        return self._getNumber(4)

    def setUpgrades(self, value):
        self._setNumber(4, value)

    def getCompare(self):
        return self._getNumber(5)

    def setCompare(self, value):
        self._setNumber(5, value)

    def getResearch(self):
        return self._getNumber(6)

    def setResearch(self, value):
        self._setNumber(6, value)

    def getArmor(self):
        return self._getNumber(7)

    def setArmor(self, value):
        self._setNumber(7, value)

    def getQuickService(self):
        return self._getNumber(8)

    def setQuickService(self, value):
        self._setNumber(8, value)

    def getCustomization(self):
        return self._getNumber(9)

    def setCustomization(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(VehicleMenuKeyBindingsModel, self)._initialize()
        self._addNumberProperty('retrainCrew', 0)
        self._addNumberProperty('quickTraining', 0)
        self._addNumberProperty('returnCrew', 0)
        self._addNumberProperty('aboutVehicle', 0)
        self._addNumberProperty('upgrades', 0)
        self._addNumberProperty('compare', 0)
        self._addNumberProperty('research', 0)
        self._addNumberProperty('armor', 0)
        self._addNumberProperty('quickService', 0)
        self._addNumberProperty('customization', 0)
