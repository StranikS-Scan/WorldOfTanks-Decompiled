# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_value_price.py
from gui.impl.gen.view_models.views.value_price import ValuePrice

class BlueprintValuePrice(ValuePrice):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(BlueprintValuePrice, self).__init__(properties=properties, commands=commands)

    def getHasDelimeter(self):
        return self._getBool(4)

    def setHasDelimeter(self, value):
        self._setBool(4, value)

    def getItemCD(self):
        return self._getNumber(5)

    def setItemCD(self, value):
        self._setNumber(5, value)

    def getTooltipId(self):
        return self._getString(6)

    def setTooltipId(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(BlueprintValuePrice, self)._initialize()
        self._addBoolProperty('hasDelimeter', False)
        self._addNumberProperty('itemCD', 0)
        self._addStringProperty('tooltipId', '')
