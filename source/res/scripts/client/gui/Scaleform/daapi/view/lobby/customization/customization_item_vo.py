# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_item_vo.py
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION

def buildCustomizationItemDataVO(item, count, plainView=False, showDetailItems=True, forceLocked=False, showUnsupportedAlert=False, isCurrentlyApplied=False, addExtraName=True):
    hasBonus = item.bonus is not None and not plainView
    locked = (not item.isUnlocked or forceLocked) and not plainView
    if plainView or item.isHidden:
        buyPrice = ITEM_PRICE_EMPTY
    else:
        buyPrice = item.getBuyPrice()
    isNonHistoric = not item.isHistorical()
    if addExtraName and item.itemTypeID in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE):
        extraName = text_styles.bonusLocalText(item.userName)
    else:
        extraName = ''
    isEquipped = isCurrentlyApplied
    rentalInfoText = ''
    if item.isRentable and count <= 0:
        rentalInfoText = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CAROUSEL_RENTALBATTLES, battlesNum=item.rentCount))
    return CustomizationCarouselRendererVO(item.intCD, item.itemTypeID, item.isWide(), item.icon, hasBonus, locked, buyPrice, count, item.isRentable, showDetailItems, isNonHistoric, showUnsupportedAlert, extraName=extraName, showRareIcon=item.isRare(), isEquipped=isEquipped, rentalInfoText=rentalInfoText).asDict()


class CustomizationCarouselRendererVO(object):
    __slots__ = ('intCD', 'typeId', 'isWide', 'icon', 'hasBonus', 'locked', 'buyPrice', 'quantity', 'isRental', 'showDetailItems', 'isNonHistoric', 'showAlert', 'buyOperationAllowed', 'extraName', 'showRareIcon', 'isEquipped', 'rentalInfoText')

    def __init__(self, intCD, typeId, isWide, icon, hasBonus, locked, buyPrice, quantity=None, isRental=False, showDetailItems=True, isNonHistoric=False, showAlert=False, buyOperationAllowed=True, extraName='', showRareIcon=False, isEquipped=False, rentalInfoText=''):
        self.intCD = intCD
        self.typeId = typeId
        self.isWide = isWide
        self.icon = icon
        self.hasBonus = hasBonus
        self.locked = locked
        self.buyPrice = getItemPricesVO(buyPrice)[0]
        self.quantity = quantity
        self.isRental = isRental
        self.showDetailItems = showDetailItems
        self.isNonHistoric = isNonHistoric
        self.showAlert = showAlert
        self.buyOperationAllowed = buyOperationAllowed
        self.extraName = extraName
        self.showRareIcon = showRareIcon
        self.isEquipped = isEquipped
        self.rentalInfoText = rentalInfoText

    def asDict(self):
        ret = {'intCD': self.intCD,
         'typeId': self.typeId,
         'isWide': self.isWide,
         'icon': self.icon,
         'locked': self.locked,
         'buyPrice': self.buyPrice,
         'isRental': self.isRental,
         'showDetailItems': self.showDetailItems,
         'isNonHistoric': self.isNonHistoric,
         'showAlert': self.showAlert,
         'buyOperationAllowed': self.buyOperationAllowed,
         'showRareIcon': self.showRareIcon,
         'isEquipped': self.isEquipped,
         'rentalInfoText': self.rentalInfoText}
        if self.extraName:
            ret.update(styleName=self.extraName)
        if self.quantity:
            ret.update(quantity=str(self.quantity))
        return ret
