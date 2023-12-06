# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_bundles_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_bundle_model import ArmoryYardBundleModel

class ArmoryYardBundlesViewModel(ViewModel):
    __slots__ = ('onBuyBundle', 'onBuyTokens', 'onClose')

    def __init__(self, properties=6, commands=3):
        super(ArmoryYardBundlesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tokenPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getTokenPriceType():
        return PriceModel

    def getIsBlurEnabled(self):
        return self._getBool(1)

    def setIsBlurEnabled(self, value):
        self._setBool(1, value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getBundles(self):
        return self._getArray(3)

    def setBundles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBundlesType():
        return ArmoryYardBundleModel

    def getCurrentTime(self):
        return self._getNumber(4)

    def setCurrentTime(self, value):
        self._setNumber(4, value)

    def getEndTime(self):
        return self._getNumber(5)

    def setEndTime(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ArmoryYardBundlesViewModel, self)._initialize()
        self._addViewModelProperty('tokenPrice', PriceModel())
        self._addBoolProperty('isBlurEnabled', False)
        self._addNumberProperty('currentLevel', 0)
        self._addArrayProperty('bundles', Array())
        self._addNumberProperty('currentTime', 0)
        self._addNumberProperty('endTime', 0)
        self.onBuyBundle = self._addCommand('onBuyBundle')
        self.onBuyTokens = self._addCommand('onBuyTokens')
        self.onClose = self._addCommand('onClose')
