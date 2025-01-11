# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/bundle_purchase_dialog_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_purchase_model import NyPurchaseModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_reward_item_model import BundleRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_sack_model import BundleSackModel

class BundlePurchaseDialogViewModel(NyPurchaseModel):
    __slots__ = ('onOpenConverter', 'onSwitchBundle', 'onStylePreview')

    def __init__(self, properties=12, commands=5):
        super(BundlePurchaseDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentBundle(self):
        return self._getString(5)

    def setCurrentBundle(self, value):
        self._setString(5, value)

    def getIsBundleReceived(self):
        return self._getBool(6)

    def setIsBundleReceived(self, value):
        self._setBool(6, value)

    def getIsApplied(self):
        return self._getBool(7)

    def setIsApplied(self, value):
        self._setBool(7, value)

    def getTimeTill(self):
        return self._getNumber(8)

    def setTimeTill(self, value):
        self._setNumber(8, value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRewardsType():
        return BundleRewardItemModel

    def getInstantRewards(self):
        return self._getArray(10)

    def setInstantRewards(self, value):
        self._setArray(10, value)

    @staticmethod
    def getInstantRewardsType():
        return BundleRewardItemModel

    def getSacks(self):
        return self._getArray(11)

    def setSacks(self, value):
        self._setArray(11, value)

    @staticmethod
    def getSacksType():
        return BundleSackModel

    def _initialize(self):
        super(BundlePurchaseDialogViewModel, self)._initialize()
        self._addStringProperty('currentBundle', '')
        self._addBoolProperty('isBundleReceived', False)
        self._addBoolProperty('isApplied', False)
        self._addNumberProperty('timeTill', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('instantRewards', Array())
        self._addArrayProperty('sacks', Array())
        self.onOpenConverter = self._addCommand('onOpenConverter')
        self.onSwitchBundle = self._addCommand('onSwitchBundle')
        self.onStylePreview = self._addCommand('onStylePreview')
