# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/shell_model.py
from frameworks.wulf import ViewModel

class ShellModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ShellModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def getItemType(self):
        return self._getString(1)

    def setItemType(self, value):
        self._setString(1, value)

    def getIsPremium(self):
        return self._getBool(2)

    def setIsPremium(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ShellModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('itemType', '')
        self._addBoolProperty('isPremium', False)
