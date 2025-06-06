# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_bundles_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_bundle_model import ArmoryYardBundleModel

class ArmoryYardBundlesViewModel(ViewModel):
    __slots__ = ('onBuyBundle', 'onBuyTokens', 'onClose')

    def __init__(self, properties=7, commands=3):
        super(ArmoryYardBundlesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tokenPriceGold(self):
        return self._getViewModel(0)

    @staticmethod
    def getTokenPriceGoldType():
        return PriceModel

    @property
    def tokenPriceCrystal(self):
        return self._getViewModel(1)

    @staticmethod
    def getTokenPriceCrystalType():
        return PriceModel

    def getIsBlurEnabled(self):
        return self._getBool(2)

    def setIsBlurEnabled(self, value):
        self._setBool(2, value)

    def getCurrentLevel(self):
        return self._getNumber(3)

    def setCurrentLevel(self, value):
        self._setNumber(3, value)

    def getBundles(self):
        return self._getArray(4)

    def setBundles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBundlesType():
        return ArmoryYardBundleModel

    def getCurrentTime(self):
        return self._getNumber(5)

    def setCurrentTime(self, value):
        self._setNumber(5, value)

    def getEndTime(self):
        return self._getNumber(6)

    def setEndTime(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ArmoryYardBundlesViewModel, self)._initialize()
        self._addViewModelProperty('tokenPriceGold', PriceModel())
        self._addViewModelProperty('tokenPriceCrystal', PriceModel())
        self._addBoolProperty('isBlurEnabled', False)
        self._addNumberProperty('currentLevel', 0)
        self._addArrayProperty('bundles', Array())
        self._addNumberProperty('currentTime', 0)
        self._addNumberProperty('endTime', 0)
        self.onBuyBundle = self._addCommand('onBuyBundle')
        self.onBuyTokens = self._addCommand('onBuyTokens')
        self.onClose = self._addCommand('onClose')
