# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_carousel_item_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class CustomizationCarouselItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=46, commands=0):
        super(CustomizationCarouselItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def buyPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getBuyPriceType():
        return PriceModel

    def getIsFilled(self):
        return self._getBool(1)

    def setIsFilled(self, value):
        self._setBool(1, value)

    def getTypeId(self):
        return self._getNumber(2)

    def setTypeId(self, value):
        self._setNumber(2, value)

    def getImageCached(self):
        return self._getBool(3)

    def setImageCached(self, value):
        self._setBool(3, value)

    def getAutoRentEnabled(self):
        return self._getBool(4)

    def setAutoRentEnabled(self, value):
        self._setBool(4, value)

    def getCustomizationDisplayType(self):
        return self._getNumber(5)

    def setCustomizationDisplayType(self, value):
        self._setNumber(5, value)

    def getDefaultIconAlpha(self):
        return self._getReal(6)

    def setDefaultIconAlpha(self, value):
        self._setReal(6, value)

    def getShowAlert(self):
        return self._getBool(7)

    def setShowAlert(self, value):
        self._setBool(7, value)

    def getRentalInfoText(self):
        return self._getString(8)

    def setRentalInfoText(self, value):
        self._setString(8, value)

    def getEditBtnEnabled(self):
        return self._getBool(9)

    def setEditBtnEnabled(self, value):
        self._setBool(9, value)

    def getShowDetailItems(self):
        return self._getBool(10)

    def setShowDetailItems(self, value):
        self._setBool(10, value)

    def getIsNew(self):
        return self._getBool(11)

    def setIsNew(self, value):
        self._setBool(11, value)

    def getIsLinked(self):
        return self._getBool(12)

    def setIsLinked(self, value):
        self._setBool(12, value)

    def getIsDarked(self):
        return self._getBool(13)

    def setIsDarked(self, value):
        self._setBool(13, value)

    def getLockText(self):
        return self._getString(14)

    def setLockText(self, value):
        self._setString(14, value)

    def getEditableIcon(self):
        return self._getString(15)

    def setEditableIcon(self, value):
        self._setString(15, value)

    def getScale(self):
        return self._getNumber(16)

    def setScale(self, value):
        self._setNumber(16, value)

    def getBuyOperationAllowed(self):
        return self._getBool(17)

    def setBuyOperationAllowed(self, value):
        self._setBool(17, value)

    def getIsUnsuitable(self):
        return self._getBool(18)

    def setIsUnsuitable(self, value):
        self._setBool(18, value)

    def getIsSpecial(self):
        return self._getBool(19)

    def setIsSpecial(self, value):
        self._setBool(19, value)

    def getIsInProgress(self):
        return self._getBool(20)

    def setIsInProgress(self, value):
        self._setBool(20, value)

    def getIsWide(self):
        return self._getBool(21)

    def setIsWide(self, value):
        self._setBool(21, value)

    def getIsEquipped(self):
        return self._getBool(22)

    def setIsEquipped(self, value):
        self._setBool(22, value)

    def getIcon(self):
        return self._getString(23)

    def setIcon(self, value):
        self._setString(23, value)

    def getShowEditableHint(self):
        return self._getBool(24)

    def setShowEditableHint(self, value):
        self._setBool(24, value)

    def getFormFactor(self):
        return self._getNumber(25)

    def setFormFactor(self, value):
        self._setNumber(25, value)

    def getIsChained(self):
        return self._getBool(26)

    def setIsChained(self, value):
        self._setBool(26, value)

    def getNoveltyCounter(self):
        return self._getNumber(27)

    def setNoveltyCounter(self, value):
        self._setNumber(27, value)

    def getLocked(self):
        return self._getBool(28)

    def setLocked(self, value):
        self._setBool(28, value)

    def getIsWithSerialNumber(self):
        return self._getBool(29)

    def setIsWithSerialNumber(self, value):
        self._setBool(29, value)

    def getIntCD(self):
        return self._getNumber(30)

    def setIntCD(self, value):
        self._setNumber(30, value)

    def getIsRental(self):
        return self._getBool(31)

    def setIsRental(self, value):
        self._setBool(31, value)

    def getTooltip(self):
        return self._getString(32)

    def setTooltip(self, value):
        self._setString(32, value)

    def getProgressionLevel(self):
        return self._getNumber(33)

    def setProgressionLevel(self, value):
        self._setNumber(33, value)

    def getShowRareIcon(self):
        return self._getBool(34)

    def setShowRareIcon(self, value):
        self._setBool(34, value)

    def getIsAllSeasons(self):
        return self._getBool(35)

    def setIsAllSeasons(self, value):
        self._setBool(35, value)

    def getEditNoveltyCounter(self):
        return self._getNumber(36)

    def setEditNoveltyCounter(self, value):
        self._setNumber(36, value)

    def getShowEditBtnHint(self):
        return self._getBool(37)

    def setShowEditBtnHint(self, value):
        self._setBool(37, value)

    def getIsAlreadyUsed(self):
        return self._getBool(38)

    def setIsAlreadyUsed(self, value):
        self._setBool(38, value)

    def getIsDim(self):
        return self._getBool(39)

    def setIsDim(self, value):
        self._setBool(39, value)

    def getFormIconSource(self):
        return self._getString(40)

    def setFormIconSource(self, value):
        self._setString(40, value)

    def getIsProgressionRewindEnabled(self):
        return self._getBool(41)

    def setIsProgressionRewindEnabled(self, value):
        self._setBool(41, value)

    def getIsMainType(self):
        return self._getBool(42)

    def setIsMainType(self, value):
        self._setBool(42, value)

    def getQuantity(self):
        return self._getNumber(43)

    def setQuantity(self, value):
        self._setNumber(43, value)

    def getExtraName(self):
        return self._getString(44)

    def setExtraName(self, value):
        self._setString(44, value)

    def getIsSelected(self):
        return self._getBool(45)

    def setIsSelected(self, value):
        self._setBool(45, value)

    def _initialize(self):
        super(CustomizationCarouselItemModel, self)._initialize()
        self._addViewModelProperty('buyPrice', PriceModel())
        self._addBoolProperty('isFilled', False)
        self._addNumberProperty('typeId', 0)
        self._addBoolProperty('imageCached', False)
        self._addBoolProperty('autoRentEnabled', False)
        self._addNumberProperty('customizationDisplayType', 0)
        self._addRealProperty('defaultIconAlpha', 0.0)
        self._addBoolProperty('showAlert', False)
        self._addStringProperty('rentalInfoText', '')
        self._addBoolProperty('editBtnEnabled', False)
        self._addBoolProperty('showDetailItems', False)
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isLinked', False)
        self._addBoolProperty('isDarked', False)
        self._addStringProperty('lockText', '')
        self._addStringProperty('editableIcon', '')
        self._addNumberProperty('scale', 0)
        self._addBoolProperty('buyOperationAllowed', False)
        self._addBoolProperty('isUnsuitable', False)
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('isInProgress', False)
        self._addBoolProperty('isWide', False)
        self._addBoolProperty('isEquipped', False)
        self._addStringProperty('icon', '')
        self._addBoolProperty('showEditableHint', False)
        self._addNumberProperty('formFactor', 0)
        self._addBoolProperty('isChained', False)
        self._addNumberProperty('noveltyCounter', 0)
        self._addBoolProperty('locked', False)
        self._addBoolProperty('isWithSerialNumber', False)
        self._addNumberProperty('intCD', 0)
        self._addBoolProperty('isRental', False)
        self._addStringProperty('tooltip', '')
        self._addNumberProperty('progressionLevel', 0)
        self._addBoolProperty('showRareIcon', False)
        self._addBoolProperty('isAllSeasons', False)
        self._addNumberProperty('editNoveltyCounter', 0)
        self._addBoolProperty('showEditBtnHint', False)
        self._addBoolProperty('isAlreadyUsed', False)
        self._addBoolProperty('isDim', False)
        self._addStringProperty('formIconSource', '')
        self._addBoolProperty('isProgressionRewindEnabled', False)
        self._addBoolProperty('isMainType', False)
        self._addNumberProperty('quantity', 0)
        self._addStringProperty('extraName', '')
        self._addBoolProperty('isSelected', False)
