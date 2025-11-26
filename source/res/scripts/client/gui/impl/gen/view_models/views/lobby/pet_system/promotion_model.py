# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/promotion_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel

class PromoBonus(Enum):
    BONDS = 'bonds'
    COMBAT = 'combat'
    CREDITS = 'credits'
    CREW = 'crew'
    EVENTS = 'events'
    SHOWOFF = 'showoff'


class PromotionModel(ViewModel):
    __slots__ = ('onChallengeSelect', 'onPurchaseSelect')

    def __init__(self, properties=4, commands=2):
        super(PromotionModel, self).__init__(properties=properties, commands=commands)

    def getIsPromotionEnabled(self):
        return self._getBool(0)

    def setIsPromotionEnabled(self, value):
        self._setBool(0, value)

    def getPromotionBonuses(self):
        return self._getArray(1)

    def setPromotionBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPromotionBonusesType():
        return unicode

    def getIsChallengeButtonEnabled(self):
        return self._getBool(2)

    def setIsChallengeButtonEnabled(self, value):
        self._setBool(2, value)

    def getIsPurchaseButtonEnabled(self):
        return self._getBool(3)

    def setIsPurchaseButtonEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PromotionModel, self)._initialize()
        self._addBoolProperty('isPromotionEnabled', True)
        self._addArrayProperty('promotionBonuses', Array())
        self._addBoolProperty('isChallengeButtonEnabled', True)
        self._addBoolProperty('isPurchaseButtonEnabled', True)
        self.onChallengeSelect = self._addCommand('onChallengeSelect')
        self.onPurchaseSelect = self._addCommand('onPurchaseSelect')
