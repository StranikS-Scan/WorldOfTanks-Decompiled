# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/ny_city_marker_model.py
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZoneTypeModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_marker_model import NyMarkerModel

class NyCityMarkerModel(NyMarkerModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NyCityMarkerModel, self).__init__(properties=properties, commands=commands)

    @property
    def customizationZone(self):
        return self._getViewModel(5)

    @staticmethod
    def getCustomizationZoneType():
        return CustomizationZoneTypeModel

    def getIsZoneHovered(self):
        return self._getBool(6)

    def setIsZoneHovered(self, value):
        self._setBool(6, value)

    def getCurrentLevel(self):
        return self._getNumber(7)

    def setCurrentLevel(self, value):
        self._setNumber(7, value)

    def getCurrencyCount(self):
        return self._getNumber(8)

    def setCurrencyCount(self, value):
        self._setNumber(8, value)

    def getLevelUpCurrencyNeed(self):
        return self._getNumber(9)

    def setLevelUpCurrencyNeed(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(NyCityMarkerModel, self)._initialize()
        self._addViewModelProperty('customizationZone', CustomizationZoneTypeModel())
        self._addBoolProperty('isZoneHovered', False)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('currencyCount', 0)
        self._addNumberProperty('levelUpCurrencyNeed', 0)
