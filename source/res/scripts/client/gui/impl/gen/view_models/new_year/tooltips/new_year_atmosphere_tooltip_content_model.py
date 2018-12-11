# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_atmosphere_tooltip_content_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearAtmosphereTooltipContentModel(ViewModel):
    __slots__ = ()

    def getEarnedAtmosphere(self):
        return self._getNumber(0)

    def setEarnedAtmosphere(self, value):
        self._setNumber(0, value)

    def getTotalAtmosphere(self):
        return self._getNumber(1)

    def setTotalAtmosphere(self, value):
        self._setNumber(1, value)

    def getLevelNames(self):
        return self._getArray(2)

    def setLevelNames(self, value):
        self._setArray(2, value)

    def getLevelValues(self):
        return self._getArray(3)

    def setLevelValues(self, value):
        self._setArray(3, value)

    def getTankLevel(self):
        return self._getString(4)

    def setTankLevel(self, value):
        self._setString(4, value)

    def getHasTankwoman(self):
        return self._getBool(5)

    def setHasTankwoman(self, value):
        self._setBool(5, value)

    def getDiscountValue(self):
        return self._getNumber(6)

    def setDiscountValue(self, value):
        self._setNumber(6, value)

    def getIsLastLevel(self):
        return self._getBool(7)

    def setIsLastLevel(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NewYearAtmosphereTooltipContentModel, self)._initialize()
        self._addNumberProperty('earnedAtmosphere', 0)
        self._addNumberProperty('totalAtmosphere', 0)
        self._addArrayProperty('levelNames', Array())
        self._addArrayProperty('levelValues', Array())
        self._addStringProperty('tankLevel', '')
        self._addBoolProperty('hasTankwoman', False)
        self._addNumberProperty('discountValue', 0)
        self._addBoolProperty('isLastLevel', False)
