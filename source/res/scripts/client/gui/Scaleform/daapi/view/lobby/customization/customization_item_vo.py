# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_item_vo.py
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION

def buildCustomizationItemDataVO(item, count, plainView=False, showDetailItems=True, forceLocked=False, showUnsupportedAlert=False, isCurrentlyApplied=False, addExtraName=True, isAlreadyUsed=False, isDarked=False, noPrice=False, autoRentEnabled=False):
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
    return CustomizationCarouselRendererVO(item.intCD, item.itemTypeID, item.isWide(), item.icon, hasBonus, locked, buyPrice, count, item.isRentable, showDetailItems, isNonHistoric, isSpecial, isDarked, isAlreadyUsed, showUnsupportedAlert, extraNames=extraNames, showRareIcon=item.isRare(), isEquipped=isCurrentlyApplied, rentalInfoText=rentalInfoText, imageCached=imageCached, autoRentEnabled=autoRentEnabled).asDict()


class CustomizationCarouselRendererVO(object):
    __slots__ = ('intCD', 'typeId', 'isWide', 'icon', 'hasBonus', 'locked', 'buyPrice', 'quantity', 'isRental', 'autoRentEnabled', 'showDetailItems', 'isNonHistoric', 'isSpecial', 'isDarked', 'isAlreadyUsed', 'showAlert', 'buyOperationAllowed', 'extraNames', 'showRareIcon', 'isEquipped', 'rentalInfoText', 'imageCached')

    def __init__(self, intCD, typeId, isWide, icon, hasBonus, locked, buyPrice, quantity=None, isRental=False, showDetailItems=True, isNonHistoric=False, isSpecial=False, isDarked=False, isAlreadyUsed=False, showAlert=False, buyOperationAllowed=True, extraNames=None, showRareIcon=False, isEquipped=False, rentalInfoText='', imageCached=True, autoRentEnabled=False):
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
         'imageCached': self.imageCached}
        if self.extraNames is not None:
            ret.update(styleName=self.extraNames[0], styleNameSmall=self.extraNames[1])
        if self.quantity:
            ret.update(quantity=str(self.quantity))
        return ret
