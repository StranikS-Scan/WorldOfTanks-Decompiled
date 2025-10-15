# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_price.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BlueprintPrice(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BlueprintPrice, self).__init__(properties=properties, commands=commands)

    def getIconBig(self):
        return self._getResource(0)

    def setIconBig(self, value):
        self._setResource(0, value)

    def getNationName(self):
        return self._getString(1)

    def setNationName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getNumber(2)

    def setValue(self, value):
        self._setNumber(2, value)

    def getHasDelimeter(self):
        return self._getBool(3)

    def setHasDelimeter(self, value):
        self._setBool(3, value)

    def getItemCD(self):
        return self._getNumber(4)

    def setItemCD(self, value):
        self._setNumber(4, value)

    def getTooltipId(self):
        return self._getString(5)

    def setTooltipId(self, value):
        self._setString(5, value)

    def getType(self):
        return self._getString(6)

    def setType(self, value):
        self._setString(6, value)

    def getIcon(self):
        return self._getResource(7)

    def setIcon(self, value):
        self._setResource(7, value)

    def getNotEnough(self):
        return self._getBool(8)

    def setNotEnough(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(BlueprintPrice, self)._initialize()
        self._addResourceProperty('iconBig', R.invalid())
        self._addStringProperty('nationName', '')
        self._addNumberProperty('value', 0)
        self._addBoolProperty('hasDelimeter', False)
        self._addNumberProperty('itemCD', 0)
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('type', 'custom')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('notEnough', False)
