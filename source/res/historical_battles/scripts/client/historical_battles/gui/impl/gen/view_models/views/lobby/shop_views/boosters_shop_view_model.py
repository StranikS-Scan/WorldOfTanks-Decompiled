# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/boosters_shop_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_view_model import BundleViewModel

class BoostersShopViewModel(ViewModel):
    __slots__ = ('onClose', 'onInfoIconClicked', 'onBundleBuyClicked')
    TOOLTIP_NOT_ENOUGH_MONEY = 'TOOLTIP_NOT_ENOUGH_MONEY'
    TOOLTIP_MONEY = 'TOOLTIP_MONEY'
    TOOLTIP_BONUS = 'TOOLTIP_BONUS'

    def __init__(self, properties=4, commands=3):
        super(BoostersShopViewModel, self).__init__(properties=properties, commands=commands)

    def getCredits(self):
        return self._getNumber(0)

    def setCredits(self, value):
        self._setNumber(0, value)

    def getGold(self):
        return self._getNumber(1)

    def setGold(self, value):
        self._setNumber(1, value)

    def getExchangeRate(self):
        return self._getNumber(2)

    def setExchangeRate(self, value):
        self._setNumber(2, value)

    def getBundles(self):
        return self._getArray(3)

    def setBundles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBundlesType():
        return BundleViewModel

    def _initialize(self):
        super(BoostersShopViewModel, self)._initialize()
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('gold', 0)
        self._addNumberProperty('exchangeRate', 0)
        self._addArrayProperty('bundles', Array())
        self.onClose = self._addCommand('onClose')
        self.onInfoIconClicked = self._addCommand('onInfoIconClicked')
        self.onBundleBuyClicked = self._addCommand('onBundleBuyClicked')
