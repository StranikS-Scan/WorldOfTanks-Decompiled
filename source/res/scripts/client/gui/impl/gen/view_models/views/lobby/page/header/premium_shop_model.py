# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/premium_shop_model.py
from frameworks.wulf import ViewModel

class PremiumShopModel(ViewModel):
    __slots__ = ('onOpenExternalPremiumShop',)

    def __init__(self, properties=1, commands=1):
        super(PremiumShopModel, self).__init__(properties=properties, commands=commands)

    def getIsPremiumShop(self):
        return self._getBool(0)

    def setIsPremiumShop(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(PremiumShopModel, self)._initialize()
        self._addBoolProperty('isPremiumShop', False)
        self.onOpenExternalPremiumShop = self._addCommand('onOpenExternalPremiumShop')
