# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/marketplace/ny_marketplace_kit_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.rewards_model import RewardsModel

class NyMarketplaceKitModel(ViewModel):
    __slots__ = ('onBuy', 'onSwitchResource', 'onOpenStyle')

    def __init__(self, properties=8, commands=3):
        super(NyMarketplaceKitModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return RewardsModel

    def getResources(self):
        return self._getArray(1)

    def setResources(self, value):
        self._setArray(1, value)

    @staticmethod
    def getResourcesType():
        return unicode

    def getCurrentResource(self):
        return self._getString(2)

    def setCurrentResource(self, value):
        self._setString(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getPriceWithDiscount(self):
        return self._getNumber(4)

    def setPriceWithDiscount(self, value):
        self._setNumber(4, value)

    def getNotEnoughResource(self):
        return self._getBool(5)

    def setNotEnoughResource(self, value):
        self._setBool(5, value)

    def getDiscount(self):
        return self._getNumber(6)

    def setDiscount(self, value):
        self._setNumber(6, value)

    def getStyleOnVehicle(self):
        return self._getString(7)

    def setStyleOnVehicle(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(NyMarketplaceKitModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('resources', Array())
        self._addStringProperty('currentResource', '')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('priceWithDiscount', 0)
        self._addBoolProperty('notEnoughResource', False)
        self._addNumberProperty('discount', 0)
        self._addStringProperty('styleOnVehicle', '')
        self.onBuy = self._addCommand('onBuy')
        self.onSwitchResource = self._addCommand('onSwitchResource')
        self.onOpenStyle = self._addCommand('onOpenStyle')
