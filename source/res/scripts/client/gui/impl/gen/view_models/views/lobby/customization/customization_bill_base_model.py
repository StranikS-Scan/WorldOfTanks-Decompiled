# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_bill_base_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class CustomizationBillBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(CustomizationBillBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def buyPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getBuyPriceType():
        return PriceModel

    def getBuyButtonEnabled(self):
        return self._getBool(1)

    def setBuyButtonEnabled(self, value):
        self._setBool(1, value)

    def getIsVehicleCustomized(self):
        return self._getBool(2)

    def setIsVehicleCustomized(self, value):
        self._setBool(2, value)

    def getIsApplyButton(self):
        return self._getBool(3)

    def setIsApplyButton(self, value):
        self._setBool(3, value)

    def getIsGoldPrice(self):
        return self._getBool(4)

    def setIsGoldPrice(self, value):
        self._setBool(4, value)

    def getIsEnoughMoney(self):
        return self._getBool(5)

    def setIsEnoughMoney(self, value):
        self._setBool(5, value)

    def getIsRentable(self):
        return self._getBool(6)

    def setIsRentable(self, value):
        self._setBool(6, value)

    def getRentCount(self):
        return self._getNumber(7)

    def setRentCount(self, value):
        self._setNumber(7, value)

    def getInStorageCount(self):
        return self._getNumber(8)

    def setInStorageCount(self, value):
        self._setNumber(8, value)

    def getLockedCount(self):
        return self._getNumber(9)

    def setLockedCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(CustomizationBillBaseModel, self)._initialize()
        self._addViewModelProperty('buyPrice', PriceModel())
        self._addBoolProperty('buyButtonEnabled', False)
        self._addBoolProperty('isVehicleCustomized', False)
        self._addBoolProperty('isApplyButton', False)
        self._addBoolProperty('isGoldPrice', False)
        self._addBoolProperty('isEnoughMoney', False)
        self._addBoolProperty('isRentable', False)
        self._addNumberProperty('rentCount', 0)
        self._addNumberProperty('inStorageCount', 0)
        self._addNumberProperty('lockedCount', 0)
