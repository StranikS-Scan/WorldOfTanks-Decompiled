# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/ability_tooltip_view_model.py
from frameworks.wulf import Array, ViewModel

class AbilityTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(AbilityTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getAbilityName(self):
        return self._getString(0)

    def setAbilityName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getCooldown(self):
        return self._getNumber(2)

    def setCooldown(self, value):
        self._setNumber(2, value)

    def getMiriumCost(self):
        return self._getNumber(3)

    def setMiriumCost(self, value):
        self._setNumber(3, value)

    def getAbilityPrice(self):
        return self._getNumber(4)

    def setAbilityPrice(self, value):
        self._setNumber(4, value)

    def getCurrencyType(self):
        return self._getString(5)

    def setCurrencyType(self, value):
        self._setString(5, value)

    def getRequiredMore(self):
        return self._getNumber(6)

    def setRequiredMore(self, value):
        self._setNumber(6, value)

    def getInDepot(self):
        return self._getNumber(7)

    def setInDepot(self, value):
        self._setNumber(7, value)

    def getInVehiclesList(self):
        return self._getArray(8)

    def setInVehiclesList(self, value):
        self._setArray(8, value)

    @staticmethod
    def getInVehiclesListType():
        return unicode

    def getShowPriceBlock(self):
        return self._getBool(9)

    def setShowPriceBlock(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(AbilityTooltipViewModel, self)._initialize()
        self._addStringProperty('abilityName', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('cooldown', 0)
        self._addNumberProperty('miriumCost', 0)
        self._addNumberProperty('abilityPrice', 0)
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('requiredMore', 0)
        self._addNumberProperty('inDepot', 0)
        self._addArrayProperty('inVehiclesList', Array())
        self._addBoolProperty('showPriceBlock', True)
