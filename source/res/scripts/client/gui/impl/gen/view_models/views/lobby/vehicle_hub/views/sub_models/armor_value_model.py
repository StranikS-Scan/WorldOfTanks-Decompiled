# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/armor_value_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class ArmorValueModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ArmorValueModel, self).__init__(properties=properties, commands=commands)

    def getColor(self):
        return self._getString(0)

    def setColor(self, value):
        self._setString(0, value)

    def getLeftValue(self):
        return self._getString(1)

    def setLeftValue(self, value):
        self._setString(1, value)

    def getRightValue(self):
        return self._getString(2)

    def setRightValue(self, value):
        self._setString(2, value)

    def getOverlay(self):
        return self._getResource(3)

    def setOverlay(self, value):
        self._setResource(3, value)

    def getIsActive(self):
        return self._getBool(4)

    def setIsActive(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ArmorValueModel, self)._initialize()
        self._addStringProperty('color', '')
        self._addStringProperty('leftValue', '')
        self._addStringProperty('rightValue', '')
        self._addResourceProperty('overlay', R.invalid())
        self._addBoolProperty('isActive', True)
