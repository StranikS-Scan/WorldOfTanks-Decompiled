# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/bundle_purchase_dialog_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_reward_item_model import BundleRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_sack_model import BundleSackModel

class PurchaseState(Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    LOCKED = 'locked'


class BundlePurchaseDialogViewModel(ViewModel):
    __slots__ = ('onBuy', 'onOpenConverter', 'onBuyGold', 'onSwitchBundle', 'onStylePreview')

    def __init__(self, properties=9, commands=5):
        super(BundlePurchaseDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentBundle(self):
        return self._getString(0)

    def setCurrentBundle(self, value):
        self._setString(0, value)

    def getIsBundleReceived(self):
        return self._getBool(1)

    def setIsBundleReceived(self, value):
        self._setBool(1, value)

    def getBalance(self):
        return self._getNumber(2)

    def setBalance(self, value):
        self._setNumber(2, value)

    def getCurrency(self):
        return self._getString(3)

    def setCurrency(self, value):
        self._setString(3, value)

    def getPrice(self):
        return self._getNumber(4)

    def setPrice(self, value):
        self._setNumber(4, value)

    def getPurchaseState(self):
        return PurchaseState(self._getString(5))

    def setPurchaseState(self, value):
        self._setString(5, value.value)

    def getTimeTill(self):
        return self._getNumber(6)

    def setTimeTill(self, value):
        self._setNumber(6, value)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return BundleRewardItemModel

    def getSacks(self):
        return self._getArray(8)

    def setSacks(self, value):
        self._setArray(8, value)

    @staticmethod
    def getSacksType():
        return BundleSackModel

    def _initialize(self):
        super(BundlePurchaseDialogViewModel, self)._initialize()
        self._addStringProperty('currentBundle', '')
        self._addBoolProperty('isBundleReceived', False)
        self._addNumberProperty('balance', 0)
        self._addStringProperty('currency', '')
        self._addNumberProperty('price', 0)
        self._addStringProperty('purchaseState')
        self._addNumberProperty('timeTill', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('sacks', Array())
        self.onBuy = self._addCommand('onBuy')
        self.onOpenConverter = self._addCommand('onOpenConverter')
        self.onBuyGold = self._addCommand('onBuyGold')
        self.onSwitchBundle = self._addCommand('onSwitchBundle')
        self.onStylePreview = self._addCommand('onStylePreview')
