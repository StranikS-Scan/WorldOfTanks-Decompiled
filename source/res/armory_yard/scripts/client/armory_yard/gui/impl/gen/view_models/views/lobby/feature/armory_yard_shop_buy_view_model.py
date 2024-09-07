# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_shop_buy_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_shop_item import ArmoryYardShopItem

class ArmoryYardShopBuyViewModel(ViewModel):
    __slots__ = ('onBuyProduct', 'onBack', 'onClose', 'onShowVehiclePreview')
    MAX_VISIBLE_REWARDS = 4

    def __init__(self, properties=6, commands=4):
        super(ArmoryYardShopBuyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def item(self):
        return self._getViewModel(0)

    @staticmethod
    def getItemType():
        return ArmoryYardShopItem

    def getIsWalletAvailable(self):
        return self._getBool(1)

    def setIsWalletAvailable(self, value):
        self._setBool(1, value)

    def getGoldConversion(self):
        return self._getNumber(2)

    def setGoldConversion(self, value):
        self._setNumber(2, value)

    def getCurrencyAmount(self):
        return self._getNumber(3)

    def setCurrencyAmount(self, value):
        self._setNumber(3, value)

    def getGoldAmount(self):
        return self._getNumber(4)

    def setGoldAmount(self, value):
        self._setNumber(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(ArmoryYardShopBuyViewModel, self)._initialize()
        self._addViewModelProperty('item', ArmoryYardShopItem())
        self._addBoolProperty('isWalletAvailable', False)
        self._addNumberProperty('goldConversion', 0)
        self._addNumberProperty('currencyAmount', 0)
        self._addNumberProperty('goldAmount', 0)
        self._addArrayProperty('rewards', Array())
        self.onBuyProduct = self._addCommand('onBuyProduct')
        self.onBack = self._addCommand('onBack')
        self.onClose = self._addCommand('onClose')
        self.onShowVehiclePreview = self._addCommand('onShowVehiclePreview')
