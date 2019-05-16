# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_item_vo.py
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
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

def buildCustomizationItemDataVO(item, count, plainView=False, showDetailItems=True, forceLocked=False, showUnsupportedAlert=False, isCurrentlyApplied=False, addExtraName=True, isAlreadyUsed=False, isDarked=False, noPrice=False, autoRentEnabled=False, customIcon=None, vehicle=None, isUnsupportedForm=False):
    isSpecial = item.isVehicleBound and (item.buyCount > 0 or item.inventoryCount > 0) or item.isLimited and item.buyCount > 0
    hasBonus = item.bonus is not None and not plainView
    locked = (not item.isUnlocked or forceLocked) and not plainView
    if plainView or item.isHidden or noPrice:
        buyPrice = ITEM_PRICE_EMPTY
    else:
        buyPrice = item.getBuyPrice()
    isNonHistoric = not item.isHistorical()
    if addExtraName and item.itemTypeID in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE):
        extraNames = (text_styles.bonusLocalText(item.userName), text_styles.highTitle(item.userName))
    else:
        extraNames = None
    imageCached = item.itemTypeID is not GUI_ITEM_TYPE.PROJECTION_DECAL
    rentalInfoText = ''
    if item.isRentable and count <= 0:
        rentalInfoText = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CAROUSEL_RENTALBATTLES, battlesNum=item.rentCount))
    icon = customIcon if customIcon else item.icon
    noveltyCounter = 0 if not vehicle else item.getNoveltyCounter(vehicle)
    formIconSource = ''
    iconAlpha = _ICON_ALPHA_BY_GUI_ITEM_TYPE.get(item.itemTypeID, 1)
    lockText = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_ONOTHER if isAlreadyUsed else VEHICLE_CUSTOMIZATION.CUSTOMIZATION_UNSUPPORTEDFORM
    return CustomizationCarouselRendererVO(item.intCD, item.itemTypeID, item.isWide(), icon, hasBonus, locked, buyPrice, count, item.isRentable, showDetailItems, isNonHistoric, isSpecial, isDarked, isAlreadyUsed, showUnsupportedAlert, extraNames=extraNames, showRareIcon=item.isRare(), isEquipped=isCurrentlyApplied, rentalInfoText=rentalInfoText, imageCached=imageCached, autoRentEnabled=autoRentEnabled, isAllSeasons=item.isAllSeason(), noveltyCounter=noveltyCounter, formIconSource=formIconSource, defaultIconAlpha=iconAlpha, lockText=lockText, isUnsupportedForm=isUnsupportedForm).asDict()


class CustomizationCarouselRendererVO(object):
    __slots__ = ('intCD', 'typeId', 'isWide', 'icon', 'hasBonus', 'locked', 'buyPrice', 'quantity', 'isRental', 'autoRentEnabled', 'showDetailItems', 'isNonHistoric', 'isSpecial', 'isDarked', 'isAlreadyUsed', 'showAlert', 'buyOperationAllowed', 'extraNames', 'showRareIcon', 'isEquipped', 'rentalInfoText', 'imageCached', 'isAllSeasons', 'noveltyCounter', 'formIconSource', 'defaultIconAlpha', 'lockText', 'isUnsupportedForm')

    def __init__(self, intCD, typeId, isWide, icon, hasBonus, locked, buyPrice, quantity=None, isRental=False, showDetailItems=True, isNonHistoric=False, isSpecial=False, isDarked=False, isAlreadyUsed=False, showAlert=False, buyOperationAllowed=True, extraNames=None, showRareIcon=False, isEquipped=False, rentalInfoText='', imageCached=True, noveltyCounter=0, autoRentEnabled=False, isAllSeasons=False, formIconSource='', defaultIconAlpha=1, lockText='', isUnsupportedForm=False):
        self.intCD = intCD
        self.typeId = typeId
        self.isWide = isWide
        self.icon = icon
        self.hasBonus = hasBonus
        self.locked = locked
        self.buyPrice = getItemPricesVO(buyPrice)[0]
        self.quantity = quantity
        self.isRental = isRental
        self.autoRentEnabled = autoRentEnabled
        self.showDetailItems = showDetailItems
        self.isNonHistoric = isNonHistoric
        self.isSpecial = isSpecial
        self.isDarked = isDarked
        self.isAlreadyUsed = isAlreadyUsed
        self.showAlert = showAlert
        self.buyOperationAllowed = buyOperationAllowed
        self.extraNames = extraNames
        self.showRareIcon = showRareIcon
        self.isEquipped = isEquipped
        self.rentalInfoText = rentalInfoText
        self.imageCached = imageCached
        self.noveltyCounter = noveltyCounter
        self.isAllSeasons = isAllSeasons
        self.formIconSource = formIconSource
        self.defaultIconAlpha = defaultIconAlpha
        self.lockText = lockText
        self.isUnsupportedForm = isUnsupportedForm

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
         'isUnsupportedForm': self.isUnsupportedForm}
        if self.extraNames is not None:
            ret.update(styleName=self.extraNames[0], styleNameSmall=self.extraNames[1])
        if self.quantity:
            ret.update(quantity=str(self.quantity))
        return ret
