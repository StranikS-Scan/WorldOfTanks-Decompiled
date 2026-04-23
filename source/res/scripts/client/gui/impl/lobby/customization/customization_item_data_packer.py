# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_item_data_packer.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import PROJECTION_DECAL_FORM_TO_UI_ID, PROJECTION_DECAL_IMAGE_FORM_TAG
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_item_model import CustomizationCarouselItemModel
from gui.impl.lobby.customization.settings_constants import CUSTOMIZATION_STYLE_ITEMS_VISITED
from gui.impl.lobby.customization.shared import CustomizationTabs
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_components import EditingStyleReason
from items.components.c11n_constants import EDITING_STYLE_REASONS, ProjectionDecalFormTags
_ICON_ALPHA_BY_GUI_ITEM_TYPE = {GUI_ITEM_TYPE.PAINT: 1,
 GUI_ITEM_TYPE.CAMOUFLAGE: 1,
 GUI_ITEM_TYPE.MODIFICATION: 0.8,
 GUI_ITEM_TYPE.DECAL: 1,
 GUI_ITEM_TYPE.EMBLEM: 1,
 GUI_ITEM_TYPE.INSCRIPTION: 1,
 GUI_ITEM_TYPE.OUTFIT: 1,
 GUI_ITEM_TYPE.STYLE: 0.5,
 GUI_ITEM_TYPE.PROJECTION_DECAL: 1,
 GUI_ITEM_TYPE.INSIGNIA: 1,
 GUI_ITEM_TYPE.PERSONAL_NUMBER: 0.8}
_PROJECTION_DECAL_FORM_TO_IMAGE_SCALE = {ProjectionDecalFormTags.SQUARE: 0.725,
 ProjectionDecalFormTags.RECT1X2: 0.85,
 ProjectionDecalFormTags.RECT1X3: 0.85,
 ProjectionDecalFormTags.RECT1X4: 1,
 ProjectionDecalFormTags.RECT1X6: 1}
_DEFAULT_IMAGE_SCALE = 1

def packEmptyCustomizationItemData(item, vehicle=None, isApplied=False):
    itemModel = CustomizationCarouselItemModel()
    itemModel.setIntCD(item.intCD)
    itemModel.setIsWide(item.isWide())
    itemModel.setIsEquipped(isApplied)
    itemModel.setIsMainType(item.markedAsFavorite)
    itemModel.setNoveltyCounter(item.getNoveltyCounter(vehicle) if vehicle is not None else 0)
    return itemModel


def packCustomizationItemData(settingsProvider, item, count=None, isApplied=False, isDarked=False, isUsedUp=False, autoRentEnabled=False, vehicle=None, progressionLevel=None, icon=None, showDetailItems=True, plainView=False, showEditableHint=False, showEditBtnHint=False, isChained=False, isUnsuitable=False, isInProgress=False, isSelected=False):
    if plainView:
        locked = False
        buyPrice = ITEM_PRICE_EMPTY
    else:
        locked = isUsedUp or not item.isUnlockedByToken()
        buyPrice = ITEM_PRICE_EMPTY if item.isHidden or item.buyCount <= 0 else item.getBuyPrice()
    if isUnsuitable:
        locked = True
    if locked:
        count = None
    formFactor, formIconSource, scale = _getFormFactor(item)
    if item.isRentable and count <= 0:
        rentalInfoText = backport.text(R.strings.vehicle_customization.carousel.rentalBattles(), battlesNum=item.rentCount)
    else:
        rentalInfoText = ''
    if item.itemTypeID in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE):
        extraName = item.userName
    else:
        extraName = None
    if isUsedUp:
        lockText = backport.text(R.strings.vehicle_customization.customization.limited.onOther())
    elif isUnsuitable:
        lockText = backport.text(R.strings.vehicle_customization.customization.unsuitable())
    else:
        lockText = backport.text(R.strings.vehicle_customization.customization.UnsupportedForm())
    showAlert = _isNeedToShowAlert(item)
    imageCached = item.itemTypeID is not GUI_ITEM_TYPE.PROJECTION_DECAL
    editingReason, editableIcon = _getEditableBlockData(item, vehicle)
    editBtnEnabled = bool(editingReason)
    showEditableHint = showEditableHint and bool(editableIcon) and editBtnEnabled
    showEditBtnHint = showEditBtnHint and editBtnEnabled
    isSpecial = _isItemSpecial(item)
    if vehicle is not None:
        progressionLevel = progressionLevel or item.getLatestOpenedProgressionLevel(vehicle)
        noveltyCounter = item.getNoveltyCounter(vehicle)
    else:
        progressionLevel = progressionLevel or -1
        noveltyCounter = 0
    isProgressionRewindEnabled = item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isProgressionRewindEnabled
    icon = icon or _getIcon(item, progressionLevel)
    iconAlpha = _ICON_ALPHA_BY_GUI_ITEM_TYPE.get(item.itemTypeID, 1)
    isLinked = item.isQuestsProgression
    editNoveltyCounter = 0
    if isLinked:
        _, level = item.getQuestsProgressionInfo()
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            progressionLevel = 0
            for alternateItem in item.alternateItems:
                editNoveltyCounter += alternateItem.getNoveltyCounter(vehicle)

        else:
            progressionLevel = level
    tooltip = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM
    isNew = False
    if noveltyCounter > 0 and isLinked:
        visitedSet = settingsProvider.getSetting(CUSTOMIZATION_STYLE_ITEMS_VISITED, set())
        isNew = item.intCD not in visitedSet
    isWithSerialNumber = item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isWithSerialNumber
    isMainType = item.markedAsFavorite
    return makeCustomizationItemModel(item=item, icon=icon, locked=locked, buyPrice=buyPrice, quantity=count, showDetailItems=showDetailItems, isSpecial=isSpecial, isDarked=isDarked, isAlreadyUsed=isUsedUp, showAlert=showAlert, extraName=extraName, isEquipped=isApplied, rentalInfoText=rentalInfoText, imageCached=imageCached, autoRentEnabled=autoRentEnabled, noveltyCounter=noveltyCounter, editNoveltyCounter=editNoveltyCounter, formIconSource=formIconSource, defaultIconAlpha=iconAlpha, lockText=lockText, formFactor=formFactor, progressionLevel=progressionLevel, editableIcon=editableIcon, editBtnEnabled=editBtnEnabled, showEditableHint=showEditableHint, showEditBtnHint=showEditBtnHint, imageScale=scale, tooltip=tooltip, isChained=isChained, isUnsuitable=isUnsuitable, isProgressionRewindEnabled=isProgressionRewindEnabled, isWithSerialNumber=isWithSerialNumber, isInProgress=isInProgress, isLinked=isLinked, isNew=isNew, isMainType=isMainType, isSelected=isSelected)


def makeCustomizationItemModel(item=None, icon='', locked=False, buyPrice=ITEM_PRICE_EMPTY, quantity=None, showDetailItems=True, isSpecial=False, isDarked=False, isAlreadyUsed=False, showAlert=False, buyOperationAllowed=True, extraName=None, isEquipped=False, rentalInfoText='', imageCached=True, noveltyCounter=0, editNoveltyCounter=0, autoRentEnabled=False, formIconSource='', defaultIconAlpha=1, lockText='', formFactor=-1, progressionLevel=-1, imageScale=1, editableIcon='', editBtnEnabled=False, showEditableHint=False, showEditBtnHint=False, tooltip='', isChained=False, isUnsuitable=False, isProgressionRewindEnabled=False, isWithSerialNumber=False, isInProgress=False, isLinked=False, isNew=False, isMainType=False, isSelected=False):
    itemModel = CustomizationCarouselItemModel()
    itemModel.setTypeId(item.itemTypeID)
    itemModel.setImageCached(imageCached)
    itemModel.setAutoRentEnabled(autoRentEnabled)
    itemModel.setCustomizationDisplayType(item.customizationDisplayType())
    itemModel.setDefaultIconAlpha(defaultIconAlpha)
    itemModel.setShowAlert(showAlert)
    itemModel.setRentalInfoText(rentalInfoText)
    itemModel.setEditBtnEnabled(editBtnEnabled)
    itemModel.setShowDetailItems(showDetailItems)
    itemModel.setIsNew(isNew)
    itemModel.setIsLinked(isLinked)
    itemModel.setIsDarked(isDarked)
    itemModel.setLockText(lockText)
    itemModel.setEditableIcon(editableIcon)
    itemModel.setScale(imageScale)
    itemModel.setBuyOperationAllowed(buyOperationAllowed)
    itemModel.setIsUnsuitable(isUnsuitable)
    itemModel.setIsSpecial(isSpecial)
    itemModel.setIsInProgress(isInProgress)
    itemModel.setIsWide(item.isWide())
    itemModel.setIsEquipped(isEquipped)
    itemModel.setIcon(icon)
    itemModel.setShowEditableHint(showEditableHint)
    itemModel.setFormFactor(formFactor)
    itemModel.setIsChained(isChained)
    itemModel.setNoveltyCounter(noveltyCounter)
    itemModel.setLocked(locked)
    itemModel.setIsWithSerialNumber(isWithSerialNumber)
    itemModel.setIntCD(item.intCD)
    itemModel.setIsRental(item.isRentable)
    itemModel.setTooltip(tooltip)
    itemModel.setProgressionLevel(progressionLevel)
    itemModel.setShowRareIcon(item.isRare())
    itemModel.setIsAllSeasons(item.isAllSeason())
    itemModel.setEditNoveltyCounter(editNoveltyCounter)
    itemModel.setShowEditBtnHint(showEditBtnHint)
    itemModel.setIsAlreadyUsed(isAlreadyUsed)
    itemModel.setIsDim(item.isDim())
    itemModel.setFormIconSource(formIconSource)
    itemModel.setIsProgressionRewindEnabled(isProgressionRewindEnabled)
    itemModel.setIsMainType(isMainType)
    itemModel.setIsSelected(isSelected)
    if quantity is not None:
        itemModel.setQuantity(quantity)
    if extraName is not None:
        itemModel.setExtraName(extraName)
    if buyPrice:
        BuyPriceModelBuilder.fillPriceModelByItemPrice(itemModel.buyPrice, buyPrice)
    itemModel.setIsFilled(True)
    return itemModel


def _getIcon(item, progressionLevel):
    isProjectionDecal = item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL
    if progressionLevel > 0:
        if isProjectionDecal:
            icon = item.previewIconUrlByProgressionLevel(progressionLevel)
        else:
            icon = item.iconUrlByProgressionLevel(progressionLevel)
    else:
        icon = item.iconUrl
    return icon


def _getFormFactor(item):
    if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
        formFactor = PROJECTION_DECAL_FORM_TO_UI_ID[item.formfactor]
        formIconSource = PROJECTION_DECAL_IMAGE_FORM_TAG[item.formfactor]
        scale = _PROJECTION_DECAL_FORM_TO_IMAGE_SCALE[item.formfactor]
        return (formFactor, formIconSource, scale)
    return (-1, '', _DEFAULT_IMAGE_SCALE)


def _isItemSpecial(item):
    if item.isVehicleBound and not item.isProgressionAutoBound and (item.buyCount > 0 or item.inventoryCount > 0):
        return True
    return True if item.isLimited and item.buyCount > 0 else False


def _isNeedToShowAlert(item):
    if isRendererPipelineDeferred():
        return False
    if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
        return True
    return bool(item.descriptor.glossTexture) if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL else False


def _getEditableBlockData(item, vehicle=None):
    isEditableStyle = item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isEditable
    if isEditableStyle and vehicle is not None:
        vehicleIntCD = vehicle.intCD
        editingReason = item.canBeEditedForVehicle(vehicleIntCD)
        if not bool(editingReason):
            editableIcon = backport.image(R.images.gui.maps.icons.customization.editable_small_disable())
        elif item.isEditedForVehicle(vehicleIntCD):
            editableIcon = backport.image(R.images.gui.maps.icons.customization.edited_small())
        else:
            editableIcon = backport.image(R.images.gui.maps.icons.customization.editable_small())
    else:
        editingReason, editableIcon = EditingStyleReason(EDITING_STYLE_REASONS.NOT_EDITABLE), ''
    return (editingReason, editableIcon)


def fillMagneticTool(model, item, vehicle, tabId):
    isEnabled = item is not None and tabId not in CustomizationTabs.STYLES_ALL
    model.setIsEnabled(isEnabled)
    if isEnabled:
        progressionLevel = item.getLatestOpenedProgressionLevel(vehicle) if vehicle is not None else -1
        icon = _getIcon(item, progressionLevel)
        formFactor, _, _ = _getFormFactor(item)
        model.setIcon(icon)
        model.setIsDim(item.isDim())
        model.setIsWide(item.isWide())
        model.setFormFactor(formFactor)
    return
