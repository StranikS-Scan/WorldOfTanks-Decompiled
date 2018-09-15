# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_item_vo.py
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers.i18n import makeString as _ms

def buildCustomizationItemDataVO(item, count, plainView=False, showDetailItems=True, forceLocked=False, showUnsupportedAlert=False):
    """ Build a CustomizationCarouselRendererVO out of the given item.
    """
    hasBonus = item.bonus is not None and not plainView
    locked = (not item.isUnlocked or forceLocked) and not plainView
    buyPrice = item.getBuyPrice()
    if plainView:
        buyPrice = ITEM_PRICE_EMPTY
    isNonHistoric = not item.isHistorical()
    if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
        extraName = text_styles.promoTitle(item.userName)
    elif item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        if item.isRentable:
            title = _ms(VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_RENT)
        else:
            title = _ms(VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_PERMANENT)
        extraName = text_styles.concatStylesToMultiLine(title, text_styles.promoTitle(item.userName))
    else:
        extraName = ''
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        extraIcon = RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_CAMOUFLAGE
    else:
        extraIcon = ''
    return CustomizationCarouselRendererVO(item.intCD, item.itemTypeID, item.isWide(), item.icon, hasBonus, locked, buyPrice, count, item.isRentable, showDetailItems, isNonHistoric, showUnsupportedAlert, extraName=extraName, extraIcon=extraIcon).asDict()


class CustomizationCarouselRendererVO(object):
    __slots__ = ('intCD', 'typeId', 'isWide', 'icon', 'hasBonus', 'locked', 'buyPrice', 'quantity', 'isRental', 'showDetailItems', 'isNonHistoric', 'showAlert', 'buyOperationAllowed', 'extraName', 'extraIcon')

    def __init__(self, intCD, typeId, isWide, icon, hasBonus, locked, buyPrice, quantity=None, isRental=False, showDetailItems=True, isNonHistoric=False, showAlert=False, buyOperationAllowed=True, extraName='', extraIcon=''):
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
        self.extraIcon = extraIcon

    def asDict(self):
        """
        Creates a dictionary with the class' relevant data.
        :return: data object
        """
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
         'buyOperationAllowed': self.buyOperationAllowed}
        if self.extraIcon:
            ret.update(styleIcon=self.extraIcon)
        if self.extraName:
            ret.update(styleName=self.extraName)
        if self.quantity:
            ret.update(quantity=str(self.quantity))
        return ret
