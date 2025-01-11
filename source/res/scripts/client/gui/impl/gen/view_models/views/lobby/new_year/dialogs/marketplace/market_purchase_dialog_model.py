# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/marketplace/market_purchase_dialog_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class MarketPurchaseDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=7, commands=2):
        super(MarketPurchaseDialogModel, self).__init__(properties=properties, commands=commands)

    def getResources(self):
        return self._getArray(0)

    def setResources(self, value):
        self._setArray(0, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def getCollectionNameAndYear(self):
        return self._getString(2)

    def setCollectionNameAndYear(self, value):
        self._setString(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getPriceWithDiscount(self):
        return self._getNumber(4)

    def setPriceWithDiscount(self, value):
        self._setNumber(4, value)

    def getResourceType(self):
        return self._getString(5)

    def setResourceType(self, value):
        self._setString(5, value)

    def getIsWalletAvailable(self):
        return self._getBool(6)

    def setIsWalletAvailable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(MarketPurchaseDialogModel, self)._initialize()
        self._addArrayProperty('resources', Array())
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('collectionNameAndYear', 'NewYear_ny21')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('priceWithDiscount', 0)
        self._addStringProperty('resourceType', '')
        self._addBoolProperty('isWalletAvailable', True)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
