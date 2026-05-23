# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/summer_sale_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.summer_sale.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.summer_sale.product_model import ProductModel
from gui.impl.gen.view_models.views.lobby.summer_sale.rewards_category_model import RewardsCategoryModel
from gui.impl.gen.view_models.views.lobby.summer_sale.stepper_view_model import StepperViewModel
from gui.impl.gen.view_models.views.lobby.summer_sale.time_range_model import TimeRangeModel

class SummerSaleMainViewModel(ViewModel):
    __slots__ = ('onStepperCountChange', 'onBuyCoinsClick', 'onBuyProductClick', 'onInfoClick', 'onPreviewVehicle', 'onOpenShop', 'onOpenQuests', 'onClose')

    def __init__(self, properties=10, commands=8):
        super(SummerSaleMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventTimeRange(self):
        return self._getViewModel(0)

    @staticmethod
    def getEventTimeRangeType():
        return TimeRangeModel

    @property
    def stepper(self):
        return self._getViewModel(1)

    @staticmethod
    def getStepperType():
        return StepperViewModel

    @property
    def summerSaleSetsTotalPrice(self):
        return self._getViewModel(2)

    @staticmethod
    def getSummerSaleSetsTotalPriceType():
        return PriceModel

    def getSummerSaleSetProductCode(self):
        return self._getString(3)

    def setSummerSaleSetProductCode(self, value):
        self._setString(3, value)

    def getBumblebeeCoinsBalance(self):
        return self._getNumber(4)

    def setBumblebeeCoinsBalance(self, value):
        self._setNumber(4, value)

    def getHoneyCoinsBalance(self):
        return self._getNumber(5)

    def setHoneyCoinsBalance(self, value):
        self._setNumber(5, value)

    def getProgressionLevel(self):
        return self._getNumber(6)

    def setProgressionLevel(self, value):
        self._setNumber(6, value)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return RewardsCategoryModel

    def getProducts(self):
        return self._getArray(8)

    def setProducts(self, value):
        self._setArray(8, value)

    @staticmethod
    def getProductsType():
        return ProductModel

    def getIsAnyRandomVehicleObtained(self):
        return self._getBool(9)

    def setIsAnyRandomVehicleObtained(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(SummerSaleMainViewModel, self)._initialize()
        self._addViewModelProperty('eventTimeRange', TimeRangeModel())
        self._addViewModelProperty('stepper', StepperViewModel())
        self._addViewModelProperty('summerSaleSetsTotalPrice', PriceModel())
        self._addStringProperty('summerSaleSetProductCode', '')
        self._addNumberProperty('bumblebeeCoinsBalance', 0)
        self._addNumberProperty('honeyCoinsBalance', 0)
        self._addNumberProperty('progressionLevel', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('products', Array())
        self._addBoolProperty('isAnyRandomVehicleObtained', False)
        self.onStepperCountChange = self._addCommand('onStepperCountChange')
        self.onBuyCoinsClick = self._addCommand('onBuyCoinsClick')
        self.onBuyProductClick = self._addCommand('onBuyProductClick')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onPreviewVehicle = self._addCommand('onPreviewVehicle')
        self.onOpenShop = self._addCommand('onOpenShop')
        self.onOpenQuests = self._addCommand('onOpenQuests')
        self.onClose = self._addCommand('onClose')
