# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/customization_zone/customization_zone_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZoneTypeModel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyTypeModel

class CustomizationZoneModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(CustomizationZoneModel, self).__init__(properties=properties, commands=commands)

    @property
    def customizationZone(self):
        return self._getViewModel(0)

    @staticmethod
    def getCustomizationZoneType():
        return CustomizationZoneTypeModel

    @property
    def currencyType(self):
        return self._getViewModel(1)

    @staticmethod
    def getCurrencyTypeType():
        return NyCurrencyTypeModel

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getCurrencyCount(self):
        return self._getNumber(3)

    def setCurrencyCount(self, value):
        self._setNumber(3, value)

    def getLevelUpCurrencyNeed(self):
        return self._getNumber(4)

    def setLevelUpCurrencyNeed(self, value):
        self._setNumber(4, value)

    def getMaxLevel(self):
        return self._getNumber(5)

    def setMaxLevel(self, value):
        self._setNumber(5, value)

    def getAtmospherePoints(self):
        return self._getNumber(6)

    def setAtmospherePoints(self, value):
        self._setNumber(6, value)

    def getCanUpgrade(self):
        return self._getBool(7)

    def setCanUpgrade(self, value):
        self._setBool(7, value)

    def getHasNewToys(self):
        return self._getBool(8)

    def setHasNewToys(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(CustomizationZoneModel, self)._initialize()
        self._addViewModelProperty('customizationZone', CustomizationZoneTypeModel())
        self._addViewModelProperty('currencyType', NyCurrencyTypeModel())
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('currencyCount', 0)
        self._addNumberProperty('levelUpCurrencyNeed', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('atmospherePoints', 0)
        self._addBoolProperty('canUpgrade', True)
        self._addBoolProperty('hasNewToys', True)
