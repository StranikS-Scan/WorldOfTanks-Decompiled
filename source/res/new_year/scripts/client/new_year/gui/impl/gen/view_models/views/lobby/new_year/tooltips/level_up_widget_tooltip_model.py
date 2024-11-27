# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/level_up_widget_tooltip_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyTypeModel

class LevelUpWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(LevelUpWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def currency(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrencyType():
        return NyCurrencyTypeModel

    def getCustomizationZone(self):
        return self._getString(1)

    def setCustomizationZone(self, value):
        self._setString(1, value)

    def getPointsCount(self):
        return self._getNumber(2)

    def setPointsCount(self, value):
        self._setNumber(2, value)

    def getCurrentLevel(self):
        return self._getNumber(3)

    def setCurrentLevel(self, value):
        self._setNumber(3, value)

    def getToysCount(self):
        return self._getNumber(4)

    def setToysCount(self, value):
        self._setNumber(4, value)

    def getCurrencyCount(self):
        return self._getNumber(5)

    def setCurrencyCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(LevelUpWidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('currency', NyCurrencyTypeModel())
        self._addStringProperty('customizationZone', '')
        self._addNumberProperty('pointsCount', 0)
        self._addNumberProperty('currentLevel', 1)
        self._addNumberProperty('toysCount', 0)
        self._addNumberProperty('currencyCount', 0)
