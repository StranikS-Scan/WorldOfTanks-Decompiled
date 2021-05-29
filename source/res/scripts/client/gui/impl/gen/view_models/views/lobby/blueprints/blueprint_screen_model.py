# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_screen_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_price_content_model import BlueprintPriceContentModel

class BlueprintScreenModel(ViewModel):
    __slots__ = ('onGoToConversionScreen', 'onClose', 'onResearchVehicle', 'onGoToAllConversion', 'onSubmitUnavailableConfirm', 'onOpenVehicleViewBtnClicked')
    INIT = 0
    UPDATE = 1

    def __init__(self, properties=25, commands=6):
        super(BlueprintScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def conversionMaxCost(self):
        return self._getViewModel(0)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getVehicleLevel(self):
        return self._getString(3)

    def setVehicleLevel(self, value):
        self._setString(3, value)

    def getIsElite(self):
        return self._getBool(4)

    def setIsElite(self, value):
        self._setBool(4, value)

    def getSchemeCols(self):
        return self._getNumber(5)

    def setSchemeCols(self, value):
        self._setNumber(5, value)

    def getSchemeRows(self):
        return self._getNumber(6)

    def setSchemeRows(self, value):
        self._setNumber(6, value)

    def getIsUnlocked(self):
        return self._getBool(7)

    def setIsUnlocked(self, value):
        self._setBool(7, value)

    def getIsAvailableForUnlock(self):
        return self._getBool(8)

    def setIsAvailableForUnlock(self, value):
        self._setBool(8, value)

    def getNeedXpToUnlock(self):
        return self._getBool(9)

    def setNeedXpToUnlock(self, value):
        self._setBool(9, value)

    def getConversionAvailable(self):
        return self._getBool(10)

    def setConversionAvailable(self, value):
        self._setBool(10, value)

    def getSchemeItems(self):
        return self._getArray(11)

    def setSchemeItems(self, value):
        self._setArray(11, value)

    def getFilledCount(self):
        return self._getNumber(12)

    def setFilledCount(self, value):
        self._setNumber(12, value)

    def getIsSchemeFullCompleted(self):
        return self._getBool(13)

    def setIsSchemeFullCompleted(self, value):
        self._setBool(13, value)

    def getIsPurchased(self):
        return self._getBool(14)

    def setIsPurchased(self, value):
        self._setBool(14, value)

    def getCost(self):
        return self._getString(15)

    def setCost(self, value):
        self._setString(15, value)

    def getDiscount(self):
        return self._getNumber(16)

    def setDiscount(self, value):
        self._setNumber(16, value)

    def getDiscountAbs(self):
        return self._getString(17)

    def setDiscountAbs(self, value):
        self._setString(17, value)

    def getBackBtnLabel(self):
        return self._getString(18)

    def setBackBtnLabel(self, value):
        self._setString(18, value)

    def getMaxConvertibleFragmentCount(self):
        return self._getNumber(19)

    def setMaxConvertibleFragmentCount(self, value):
        self._setNumber(19, value)

    def getShowUnavailableConfirm(self):
        return self._getBool(20)

    def setShowUnavailableConfirm(self, value):
        self._setBool(20, value)

    def getBlueprintAnimPaused(self):
        return self._getBool(21)

    def setBlueprintAnimPaused(self, value):
        self._setBool(21, value)

    def getCurrentStateView(self):
        return self._getNumber(22)

    def setCurrentStateView(self, value):
        self._setNumber(22, value)

    def getReceivedCount(self):
        return self._getNumber(23)

    def setReceivedCount(self, value):
        self._setNumber(23, value)

    def getShowBlueprintInfotypeIcon(self):
        return self._getBool(24)

    def setShowBlueprintInfotypeIcon(self, value):
        self._setBool(24, value)

    def _initialize(self):
        super(BlueprintScreenModel, self)._initialize()
        self._addViewModelProperty('conversionMaxCost', BlueprintPriceContentModel())
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
