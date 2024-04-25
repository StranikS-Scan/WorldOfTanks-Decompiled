# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/shop_item_view_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.multi_price_view_model import MultiPriceViewModel

class ShopItemViewModel(ViewModel):
    __slots__ = ('addFavorite',)

    def __init__(self, properties=9, commands=1):
        super(ShopItemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return MultiPriceViewModel

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getIconName(self):
        return self._getString(2)

    def setIconName(self, value):
        self._setString(2, value)

    def getIconOverlay(self):
        return self._getString(3)

    def setIconOverlay(self, value):
        self._setString(3, value)

    def getName(self):
        return self._getString(4)

    def setName(self, value):
        self._setString(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getDescription(self):
        return self._getString(6)

    def setDescription(self, value):
        self._setString(6, value)

    def getCount(self):
        return self._getNumber(7)

    def setCount(self, value):
        self._setNumber(7, value)

    def getIsFavorite(self):
        return self._getBool(8)

    def setIsFavorite(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(ShopItemViewModel, self)._initialize()
        self._addViewModelProperty('price', MultiPriceViewModel())
        self._addStringProperty('id', '')
        self._addStringProperty('iconName', '')
        self._addStringProperty('iconOverlay', '')
        self._addStringProperty('name', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isFavorite', False)
        self.addFavorite = self._addCommand('addFavorite')
