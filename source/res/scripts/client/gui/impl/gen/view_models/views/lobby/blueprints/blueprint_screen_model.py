# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_screen_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialog_prices_content_model import DialogPricesContentModel
from frameworks.wulf import View

class BlueprintScreenModel(ViewModel):
    __slots__ = ('onGoToConversionScreen', 'onClose', 'onResearchVehicle', 'onGoToAllConversion', 'onSubmitUnavailableConfirm', 'onOpenVehicleViewBtnClicked')
    INIT = 0
    UPDATE = 1

    @property
    def conversionMaxCost(self):
        return self._getViewModel(0)

    def getBalanceContent(self):
        return self._getView(1)

    def setBalanceContent(self, value):
        self._setView(1, value)

    def getVehicleName(self):
        return self._getString(2)

    def setVehicleName(self, value):
        self._setString(2, value)

    def getVehicleType(self):
        return self._getString(3)

    def setVehicleType(self, value):
        self._setString(3, value)

    def getVehicleLevel(self):
        return self._getString(4)

    def setVehicleLevel(self, value):
        self._setString(4, value)

    def getIsElite(self):
        return self._getBool(5)

    def setIsElite(self, value):
        self._setBool(5, value)

    def getSchemeCols(self):
        return self._getNumber(6)

    def setSchemeCols(self, value):
        self._setNumber(6, value)

    def getSchemeRows(self):
        return self._getNumber(7)

    def setSchemeRows(self, value):
        self._setNumber(7, value)

    def getIsUnlocked(self):
        return self._getBool(8)

    def setIsUnlocked(self, value):
        self._setBool(8, value)

    def getIsAvailableForUnlock(self):
        return self._getBool(9)

    def setIsAvailableForUnlock(self, value):
        self._setBool(9, value)

    def getNeedXpToUnlock(self):
        return self._getBool(10)

    def setNeedXpToUnlock(self, value):
        self._setBool(10, value)

    def getConversionAvailable(self):
        return self._getBool(11)

    def setConversionAvailable(self, value):
        self._setBool(11, value)

    def getSchemeItems(self):
        return self._getArray(12)

    def setSchemeItems(self, value):
        self._setArray(12, value)

    def getFilledCount(self):
        return self._getNumber(13)

    def setFilledCount(self, value):
        self._setNumber(13, value)

    def getIsSchemeFullCompleted(self):
        return self._getBool(14)

    def setIsSchemeFullCompleted(self, value):
        self._setBool(14, value)

    def getIsPurchased(self):
        return self._getBool(15)

    def setIsPurchased(self, value):
        self._setBool(15, value)

    def getCost(self):
        return self._getString(16)

    def setCost(self, value):
        self._setString(16, value)

    def getDiscount(self):
        return self._getNumber(17)

    def setDiscount(self, value):
        self._setNumber(17, value)

    def getDiscountAbs(self):
        return self._getString(18)

    def setDiscountAbs(self, value):
        self._setString(18, value)

    def getBackBtnLabel(self):
        return self._getString(19)

    def setBackBtnLabel(self, value):
        self._setString(19, value)

    def getMaxConvertibleFragmentCount(self):
        return self._getNumber(20)

    def setMaxConvertibleFragmentCount(self, value):
        self._setNumber(20, value)

    def getShowUnavailableConfirm(self):
        return self._getBool(21)

    def setShowUnavailableConfirm(self, value):
        self._setBool(21, value)

    def getBlueprintAnimPaused(self):
        return self._getBool(22)

    def setBlueprintAnimPaused(self, value):
        self._setBool(22, value)

    def getCurrentStateView(self):
        return self._getNumber(23)

    def setCurrentStateView(self, value):
        self._setNumber(23, value)

    def getReceivedCount(self):
        return self._getNumber(24)

    def setReceivedCount(self, value):
        self._setNumber(24, value)

    def getShowBlueprintInfotypeIcon(self):
        return self._getBool(25)

    def setShowBlueprintInfotypeIcon(self, value):
        self._setBool(25, value)

    def _initialize(self):
        super(BlueprintScreenModel, self)._initialize()
        self._addViewModelProperty('conversionMaxCost', DialogPricesContentModel())
        self._addViewProperty('balanceContent')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLevel', '')
        self._addBoolProperty('isElite', False)
        self._addNumberProperty('schemeCols', 1)
        self._addNumberProperty('schemeRows', 1)
        self._addBoolProperty('isUnlocked', False)
        self._addBoolProperty('isAvailableForUnlock', False)
        self._addBoolProperty('needXpToUnlock', True)
        self._addBoolProperty('conversionAvailable', False)
        self._addArrayProperty('schemeItems', Array())
        self._addNumberProperty('filledCount', 0)
        self._addBoolProperty('isSchemeFullCompleted', False)
        self._addBoolProperty('isPurchased', False)
        self._addStringProperty('cost', '')
        self._addNumberProperty('discount', 0)
        self._addStringProperty('discountAbs', '0')
        self._addStringProperty('backBtnLabel', '')
        self._addNumberProperty('maxConvertibleFragmentCount', 0)
        self._addBoolProperty('showUnavailableConfirm', False)
        self._addBoolProperty('blueprintAnimPaused', False)
        self._addNumberProperty('currentStateView', -1)
        self._addNumberProperty('receivedCount', 0)
        self._addBoolProperty('showBlueprintInfotypeIcon', False)
        self.onGoToConversionScreen = self._addCommand('onGoToConversionScreen')
        self.onClose = self._addCommand('onClose')
        self.onResearchVehicle = self._addCommand('onResearchVehicle')
        self.onGoToAllConversion = self._addCommand('onGoToAllConversion')
        self.onSubmitUnavailableConfirm = self._addCommand('onSubmitUnavailableConfirm')
        self.onOpenVehicleViewBtnClicked = self._addCommand('onOpenVehicleViewBtnClicked')
