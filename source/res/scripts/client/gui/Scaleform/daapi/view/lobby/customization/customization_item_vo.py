# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_item_vo.py
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.shared import PROJECTION_DECAL_FORM_TO_UI_ID, PROJECTION_DECAL_IMAGE_FORM_TAG
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_components import EditingStyleReason
from items.components.c11n_constants import ProjectionDecalFormTags, EDITING_STYLE_REASONS
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

def buildCustomizationItemDataVO(item, count=None, isApplied=False, isDarked=False, isUsedUp=False, autoRentEnabled=False, vehicle=None, progressionLevel=None, icon=None, showDetailItems=True, plainView=False, showEditableHint=False, showEditBtnHint=False, isChained=False, isUnsuitable=False):
    if plainView:
        hasBonus = False
        locked = False
        buyPrice = ITEM_PRICE_EMPTY
    else:
        hasBonus = item.bonus is not None
        locked = isUsedUp or not item.isUnlocked
        buyPrice = ITEM_PRICE_EMPTY if item.isHidden or item.buyCount <= 0 else item.getBuyPrice()
    if isUnsuitable:
        locked = True
    if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
        formFactor = PROJECTION_DECAL_FORM_TO_UI_ID[item.formfactor]
        formIconSource = PROJECTION_DECAL_IMAGE_FORM_TAG[item.formfactor]
        scale = _PROJECTION_DECAL_FORM_TO_IMAGE_SCALE[item.formfactor]
    else:
        formFactor = -1
        formIconSource = ''
        scale = _DEFAULT_IMAGE_SCALE
    if item.isRentable and count <= 0:
        rentalInfoText = R.strings.vehicle_customization.carousel.rentalBattles()
        rentalInfoText = text_styles.main(backport.text(rentalInfoText, battlesNum=item.rentCount))
    else:
        rentalInfoText = ''
    if item.itemTypeID in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE):
        extraNames = (text_styles.bonusLocalText(item.userName), text_styles.highTitle(item.userName))
    else:
        extraNames = None
    if isUsedUp:
        lockText = backport.text(R.strings.vehicle_customization.customization.limited.onOther())
    elif isUnsuitable:
        lockText = backport.text(R.strings.vehicle_customization.customization.unsuitable())
    else:
        lockText = backport.text(R.strings.vehicle_customization.customization.UnsupportedForm())
    showAlert = __isNeedToShowAlert(item)
    imageCached = item.itemTypeID is not GUI_ITEM_TYPE.PROJECTION_DECAL
    editingReason, editableIcon = __getEditableBlockData(item, vehicle)
    editBtnEnabled = bool(editingReason)
    showEditableHint = showEditableHint and bool(editableIcon) and editBtnEnabled
    showEditBtnHint = showEditBtnHint and editBtnEnabled
    isSpecial = __isItemSpecial(item)
    if vehicle is not None:
        progressionLevel = progressionLevel or item.getLatestOpenedProgressionLevel(vehicle)
        noveltyCounter = item.getNoveltyCounter(vehicle)
    else:
        progressionLevel = progressionLevel or -1
        noveltyCounter = 0
    icon = icon or __getIcon(item, progressionLevel)
    iconAlpha = _ICON_ALPHA_BY_GUI_ITEM_TYPE.get(item.itemTypeID, 1)
    tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_SLOT_EDITBTN_ENABLED
    if editingReason.reason == EDITING_STYLE_REASONS.NOT_REACHED_LEVEL:
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_SLOT_EDITBTN_DISABLED_NOTREACHEDLEVEL
    elif not editingReason:
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_SLOT_EDITBTN_DISABLED
    return CustomizationCarouselRendererVO(item=item, icon=icon, hasBonus=hasBonus, locked=locked, buyPrice=buyPrice, quantity=count, showDetailItems=showDetailItems, isSpecial=isSpecial, isDarked=isDarked, isAlreadyUsed=isUsedUp, showAlert=showAlert, extraNames=extraNames, isEquipped=isApplied, rentalInfoText=rentalInfoText, imageCached=imageCached, autoRentEnabled=autoRentEnabled, noveltyCounter=noveltyCounter, formIconSource=formIconSource, defaultIconAlpha=iconAlpha, lockText=lockText, formFactor=formFactor, progressionLevel=progressionLevel, editableIcon=editableIcon, editBtnEnabled=editBtnEnabled, showEditableHint=showEditableHint, showEditBtnHint=showEditBtnHint, imageScale=scale, tooltip=tooltip, isChained=isChained, isUnsuitable=isUnsuitable).asDict()


class CustomizationCarouselRendererVO(object):
    __slots__ = ('intCD', 'typeId', 'isWide', 'icon', 'hasBonus', 'locked', 'buyPrice', 'quantity', 'isRental', 'autoRentEnabled', 'showDetailItems', 'isNonHistoric', 'isSpecial', 'isDarked', 'isAlreadyUsed', 'showAlert', 'buyOperationAllowed', 'extraNames', 'showRareIcon', 'isEquipped', 'rentalInfoText', 'imageCached', 'isAllSeasons', 'noveltyCounter', 'formIconSource', 'defaultIconAlpha', 'lockText', 'isDim', 'formFactor', 'progressionLevel', 'editableIcon', 'editBtnEnabled', 'showEditableHint', 'showEditBtnHint', 'imageScale', 'tooltip', 'isChained', 'isUnsuitable')

    def __init__(self, item, icon, hasBonus, locked, buyPrice, quantity=None, showDetailItems=True, isSpecial=False, isDarked=False, isAlreadyUsed=False, showAlert=False, buyOperationAllowed=True, extraNames=None, isEquipped=False, rentalInfoText='', imageCached=True, noveltyCounter=0, autoRentEnabled=False, formIconSource='', defaultIconAlpha=1, lockText='', formFactor=-1, progressionLevel=-1, imageScale=1, editableIcon='', editBtnEnabled=False, showEditableHint=False, showEditBtnHint=False, tooltip='', isChained=False, isUnsuitable=False):
        self.intCD = item.intCD
        self.typeId = item.itemTypeID
        self.isWide = item.isWide()
        self.icon = icon
        self.hasBonus = hasBonus
        self.locked = locked
        self.buyPrice = getItemPricesVO(buyPrice)[0]
        self.quantity = quantity
        self.isRental = item.isRentable
        self.autoRentEnabled = autoRentEnabled
        self.showDetailItems = showDetailItems
        self.isNonHistoric = not item.isHistorical()
        self.isSpecial = isSpecial
        self.isDarked = isDarked
        self.isAlreadyUsed = isAlreadyUsed
        self.showAlert = showAlert
        self.buyOperationAllowed = buyOperationAllowed
        self.extraNames = extraNames
        self.showRareIcon = item.isRare()
        self.isEquipped = isEquipped
        self.rentalInfoText = rentalInfoText
        self.imageCached = imageCached
        self.noveltyCounter = noveltyCounter
        self.isAllSeasons = item.isAllSeason()
        self.formIconSource = formIconSource
        self.defaultIconAlpha = defaultIconAlpha
        self.lockText = lockText
        self.isDim = item.isDim()
        self.formFactor = formFactor
        self.progressionLevel = progressionLevel
        self.editableIcon = editableIcon
        self.editBtnEnabled = editBtnEnabled
        self.showEditableHint = showEditableHint
        self.showEditBtnHint = showEditBtnHint
        self.imageScale = imageScale
        self.tooltip = tooltip
        self.isChained = isChained
        self.isUnsuitable = isUnsuitable

    def asDict(self):
        ret = {'intCD': self.intCD,
         'typeId': self.typeId,
         'isWide': self.isWide,
         'icon': self.icon,
         'locked': self.locked,
         'buyPrice': self.buyPrice,
         'isRental': self.isRental,
         'autoRentEnabled': self.autoRentEnabled,
         'showDetailItems': self.showDetailItems,
         'isNonHistoric': self.isNonHistoric,
         'isSpecial': self.isSpecial,
         'isDarked': self.isDarked,
         'isAlreadyUsed': self.isAlreadyUsed,
         'showAlert': self.showAlert,
         'buyOperationAllowed': self.buyOperationAllowed,
         'showRareIcon': self.showRareIcon,
         'isEquipped': self.isEquipped,
         'rentalInfoText': self.rentalInfoText,
         'imageCached': self.imageCached,
         'noveltyCounter': self.noveltyCounter,
         'isAllSeasons': self.isAllSeasons,
         'formIconSource': self.formIconSource,
         'defaultIconAlpha': self.defaultIconAlpha,
         'lockText': self.lockText,
         'isDim': self.isDim,
         'formFactor': self.formFactor,
         'progressionLevel': self.progressionLevel,
         'editableIcon': self.editableIcon,
         'editBtnEnabled': self.editBtnEnabled,
         'showEditableHint': self.showEditableHint,
         'showEditBtnHint': self.showEditBtnHint,
         'scale': self.imageScale,
         'tooltip': self.tooltip,
         'isChained': self.isChained,
         'isUnsuitable': self.isUnsuitable}
        if self.extraNames is not None:
            ret.update(styleName=self.extraNames[0], styleNameSmall=self.extraNames[1])
        if self.quantity:
            ret.update(quantity=str(self.quantity))
        return ret


def __getIcon(item, progressionLevel):
    isProjectionDecal = item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL
    if progressionLevel > 0:
        if isProjectionDecal:
            icon = item.previewIconUrlByProgressionLevel(progressionLevel)
        else:
            icon = item.iconByProgressionLevel(progressionLevel)
    else:
        icon = item.previewIconUrl if isProjectionDecal else item.icon
    return icon


def __isItemSpecial(item):
    if item.isVehicleBound and not item.isProgressionAutoBound and (item.buyCount > 0 or item.inventoryCount > 0):
        return True
    return True if item.isLimited and item.buyCount > 0 else False


def __isNeedToShowAlert(item):
    if isRendererPipelineDeferred():
        return False
    if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
        return True
    return bool(item.descriptor.glossTexture) if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL else False


def __getEditableBlockData(item, vehicle=None):
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
