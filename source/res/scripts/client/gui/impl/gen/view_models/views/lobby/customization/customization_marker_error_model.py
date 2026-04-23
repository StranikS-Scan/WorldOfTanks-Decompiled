# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_marker_error_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CustomizationMarkerErrorModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CustomizationMarkerErrorModel, self).__init__(properties=properties, commands=commands)

    def getText(self):
        return self._getString(0)

    def setText(self, value):
        self._setString(0, value)

    def getIcons(self):
        return self._getArray(1)

    def setIcons(self, value):
        self._setArray(1, value)

    @staticmethod
    def getIconsType():
        return unicode

    def getIsIncorrectInput(self):
        return self._getBool(2)

    def setIsIncorrectInput(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CustomizationMarkerErrorModel, self)._initialize()
        self._addStringProperty('text', '')
        self._addArrayProperty('icons', Array())
        self._addBoolProperty('isIncorrectInput', False)
