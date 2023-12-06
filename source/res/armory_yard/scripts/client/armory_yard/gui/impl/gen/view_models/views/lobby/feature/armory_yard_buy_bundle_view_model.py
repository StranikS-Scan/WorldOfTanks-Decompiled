# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_buy_bundle_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class BundleType(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class ArmoryYardBuyBundleViewModel(ViewModel):
    __slots__ = ('onBuyBundle', 'onBack', 'onClose')
    MAX_VISIBLE_REWARDS = 10

    def __init__(self, properties=8, commands=3):
        super(ArmoryYardBuyBundleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getBundleId(self):
        return self._getString(1)

    def setBundleId(self, value):
        self._setString(1, value)

    def getType(self):
        return BundleType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getStartLevel(self):
        return self._getNumber(3)

    def setStartLevel(self, value):
        self._setNumber(3, value)

    def getEndLevel(self):
        return self._getNumber(4)

    def setEndLevel(self, value):
        self._setNumber(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def getIsWalletAvailable(self):
        return self._getBool(6)

    def setIsWalletAvailable(self, value):
        self._setBool(6, value)

    def getIsBlurEnabled(self):
        return self._getBool(7)

    def setIsBlurEnabled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(ArmoryYardBuyBundleViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('bundleId', '')
        self._addStringProperty('type')
        self._addNumberProperty('startLevel', 0)
        self._addNumberProperty('endLevel', 0)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('isBlurEnabled', False)
        self.onBuyBundle = self._addCommand('onBuyBundle')
        self.onBack = self._addCommand('onBack')
        self.onClose = self._addCommand('onClose')
