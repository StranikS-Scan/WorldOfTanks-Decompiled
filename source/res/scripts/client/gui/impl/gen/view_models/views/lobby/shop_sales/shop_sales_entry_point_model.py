# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/shop_sales/shop_sales_entry_point_model.py
from frameworks.wulf import ViewModel

class ShopSalesEntryPointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(ShopSalesEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getItemsCount(self):
        return self._getNumber(0)

    def setItemsCount(self, value):
        self._setNumber(0, value)

    def getState(self):
        return self._getNumber(1)

    def setState(self, value):
        self._setNumber(1, value)

    def getCooldownTime(self):
        return self._getString(2)

    def setCooldownTime(self, value):
        self._setString(2, value)

    def getIsDoubleRowsCarousel(self):
        return self._getBool(3)

    def setIsDoubleRowsCarousel(self, value):
        self._setBool(3, value)

    def getIsSmallDoubleCarouselEnable(self):
        return self._getBool(4)

    def setIsSmallDoubleCarouselEnable(self, value):
        self._setBool(4, value)

    def getIsDisabled(self):
        return self._getBool(5)

    def setIsDisabled(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ShopSalesEntryPointModel, self)._initialize()
        self._addNumberProperty('itemsCount', 0)
        self._addNumberProperty('state', -1)
        self._addStringProperty('cooldownTime', '')
        self._addBoolProperty('isDoubleRowsCarousel', False)
        self._addBoolProperty('isSmallDoubleCarouselEnable', False)
        self._addBoolProperty('isDisabled', False)
        self.onClick = self._addCommand('onClick')
