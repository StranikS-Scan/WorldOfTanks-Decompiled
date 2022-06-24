# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/post_progression_purchase_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class PostProgressionPurchaseModel(ViewModel):
    __slots__ = ('onPurchaseClick',)

    def __init__(self, properties=6, commands=1):
        super(PostProgressionPurchaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def modificationBonuses(self):
        return self._getViewModel(0)

    @staticmethod
    def getModificationBonusesType():
        return BonusesModel

    @property
    def price(self):
        return self._getViewModel(1)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getCanPurchase(self):
        return self._getBool(2)

    def setCanPurchase(self, value):
        self._setBool(2, value)

    def getPurchasedSingleStepIds(self):
        return self._getArray(3)

    def setPurchasedSingleStepIds(self, value):
        self._setArray(3, value)

    @staticmethod
    def getPurchasedSingleStepIdsType():
        return int

    def getPurchasedFeatureStepIds(self):
        return self._getArray(4)

    def setPurchasedFeatureStepIds(self, value):
        self._setArray(4, value)

    @staticmethod
    def getPurchasedFeatureStepIdsType():
        return int

    def getUnlockedMultiStepIds(self):
        return self._getArray(5)

    def setUnlockedMultiStepIds(self, value):
        self._setArray(5, value)

    @staticmethod
    def getUnlockedMultiStepIdsType():
        return int

    def _initialize(self):
        super(PostProgressionPurchaseModel, self)._initialize()
        self._addViewModelProperty('modificationBonuses', BonusesModel())
        self._addViewModelProperty('price', PriceModel())
        self._addBoolProperty('canPurchase', True)
        self._addArrayProperty('purchasedSingleStepIds', Array())
        self._addArrayProperty('purchasedFeatureStepIds', Array())
        self._addArrayProperty('unlockedMultiStepIds', Array())
        self.onPurchaseClick = self._addCommand('onPurchaseClick')
