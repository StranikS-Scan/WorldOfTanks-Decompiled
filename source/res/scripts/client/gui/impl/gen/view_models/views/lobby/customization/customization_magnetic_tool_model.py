# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_magnetic_tool_model.py
from frameworks.wulf import ViewModel

class CustomizationMagneticToolModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CustomizationMagneticToolModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getIsWide(self):
        return self._getBool(2)

    def setIsWide(self, value):
        self._setBool(2, value)

    def getIsDim(self):
        return self._getBool(3)

    def setIsDim(self, value):
        self._setBool(3, value)

    def getFormFactor(self):
        return self._getNumber(4)

    def setFormFactor(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(CustomizationMagneticToolModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)
        self._addStringProperty('icon', '')
        self._addBoolProperty('isWide', False)
        self._addBoolProperty('isDim', False)
        self._addNumberProperty('formFactor', 0)
