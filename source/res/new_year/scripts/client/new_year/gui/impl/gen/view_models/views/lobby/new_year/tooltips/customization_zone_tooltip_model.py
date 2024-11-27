# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/customization_zone_tooltip_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZoneTypeModel

class CustomizationZoneTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CustomizationZoneTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def customizationZone(self):
        return self._getViewModel(0)

    @staticmethod
    def getCustomizationZoneType():
        return CustomizationZoneTypeModel

    def getCurrentLevel(self):
        return self._getNumber(1)

    def setCurrentLevel(self, value):
        self._setNumber(1, value)

    def getMaxLevel(self):
        return self._getNumber(2)

    def setMaxLevel(self, value):
        self._setNumber(2, value)

    def getNextLevelDecorations(self):
        return self._getNumber(3)

    def setNextLevelDecorations(self, value):
        self._setNumber(3, value)

    def getUpgradeCost(self):
        return self._getNumber(4)

    def setUpgradeCost(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(CustomizationZoneTooltipModel, self)._initialize()
        self._addViewModelProperty('customizationZone', CustomizationZoneTypeModel())
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('nextLevelDecorations', 0)
        self._addNumberProperty('upgradeCost', 0)
