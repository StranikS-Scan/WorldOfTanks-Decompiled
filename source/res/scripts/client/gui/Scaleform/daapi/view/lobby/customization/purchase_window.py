# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/purchase_window.py
import itertools
from adisp import process
from Event import Event
from gui import makeHtmlString
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip, getAbsoluteUrl
from gui.Scaleform.daapi.view.meta.CustomizationBuyWindowMeta import CustomizationBuyWindowMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from helpers.i18n import makeString as _ms
from shared import getDialogReplaceElements
from gui.customization import g_customizationController
from gui.customization.shared import formatPriceCredits, formatPriceGold, getSalePriceString, DURATION
_CUSTOMIZATION_TYPE_TITLES = (VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_CAMOUFLAGE, VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_EMBLEM, VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_INSCRIPTION)
_DURATION_LABELS = (VEHICLE_CUSTOMIZATION.BUYWINDOW_BUYTIME_EVER, VEHICLE_CUSTOMIZATION.BUYWINDOW_BUYTIME_THIRTYDAYS, VEHICLE_CUSTOMIZATION.BUYWINDOW_BUYTIME_SEVENDAYS)

def _getDropdownPriceVO(element):
    result = []
    for duration, text in zip(DURATION.ALL, _DURATION_LABELS):
        if duration == DURATION.PERMANENT:
            textStyle = text_styles.gold
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2
        else:
            textStyle = text_styles.credits
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2
        dropdownItem = {'labelPrice': text_styles.main(_ms(text)),
         'label': makeHtmlString('html_templates:lobby/customization', 'DDString', {'text': textStyle(element.getPrice(duration)),
                   'icon': getAbsoluteUrl(icon)})}
        if element.isOnSale(duration):
            isGold = duration == DURATION.PERMANENT
            dropdownItem['salePrice'] = getSalePriceString(isGold, element, duration)
            dropdownItem['isSale'] = True
        result.append(dropdownItem)

    return result


def _getColumnHeaderVO(idx, label, buttonWidth):
    return {'id': idx,
     'label': _ms(label),
     'iconSource': '',
     'buttonWidth': buttonWidth,
     'toolTip': '',
     'sortOrder': -1,
     'defaultSortDirection': 'ascending',
     'buttonHeight': 50,
     'showSeparator': True,
     'enabled': False}


class PurchaseWindow(CustomizationBuyWindowMeta):

    def __init__(self, ctx=None):
        super(PurchaseWindow, self).__init__()
        self.__controller = None
        return

    def selectItem(self, itemIdx):
        self.__searchDP.setSelected(itemIdx, True)

    def deselectItem(self, itemIdx):
        self.__searchDP.setSelected(itemIdx, False)

    def changePriceItem(self, itemIdx, price):
        self.__searchDP.setPrice(itemIdx, price)

    def onWindowClose(self):
        self.destroy()

    def buy(self):
        replacedElementGroups = [[], [], []]
        purchaseItems = []
        for item in self.__searchDP.items:
            slotData = self.__controller.slots.getInstalledSlotData(item['slotIdx'], item['cType'])
            if slotData['duration'] > 0:
                element = slotData['element']
                replacedElementGroups[item['cType']].append(text_styles.main(element.getName()))
            if item['isDuplicatePrice']:
                item['price'] = 0
            purchaseItems.append(item)

        self.__buyElements(purchaseItems, replacedElementGroups)

    def _dispose(self):
        self.__searchDP.selectionChanged -= self.__setTotalData
        self.__searchDP.fini()
        self.__controller.events.onMultiplePurchaseProcessed -= self.destroy
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__controller.cart is not None:
            for item in self.__controller.cart.items:
                item['isSelected'] = True
                item['duration'] = item['initialDuration']

            self.__controller.cart.recalculateTotalPrice()
        self.__controller = None
        super(PurchaseWindow, self)._dispose()
        return

    def _populate(self):
        super(PurchaseWindow, self)._populate()
        self.__controller = g_customizationController
        self.__controller.events.onMultiplePurchaseProcessed += self.destroy
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__setTotalData,
         'stats.gold': self.__setTotalData})
        self.__searchDP = PurchaseDataProvider(self.__controller.cart)
        self.__searchDP.setFlashObject(self.as_getPurchaseDPS())
        self.__searchDP.selectionChanged += self.__setTotalData
        self.as_setInitDataS({'windowTitle': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_HEADER,
         'imgGold': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1,
         'imgCredits': RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1,
         'btnBuyLabel': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY,
         'btnCancelLabel': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNCANCEL,
         'buyDisabledTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY,
         'defaultSortIndex': 0,
         'tableHeader': [_getColumnHeaderVO('itemName', text_styles.main(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TABLEHEADER_ITEMS), 250), _getColumnHeaderVO('lblBonus', text_styles.main(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TABLEHEADER_BONUS), 110), _getColumnHeaderVO('lblPrice', text_styles.main(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TABLEHEADER_COST), 150)]})
        self.__setTotalData()

    def __setTotalData(self, *args):
        if self.__controller.cart.processingMultiplePurchase:
            return
        priceGold = self.__controller.cart.totalPriceGold
        priceCredits = self.__controller.cart.totalPriceCredits
        notEnoughGoldTooltip = notEnoughCreditsTooltip = ''
        enoughGold = g_itemsCache.items.stats.gold >= priceGold
        enoughCredits = g_itemsCache.items.stats.credits >= priceCredits
        canBuy = bool(priceGold or priceCredits) and enoughGold and enoughCredits
        if not enoughGold:
            diff = text_styles.gold(priceGold - g_itemsCache.items.stats.gold)
            notEnoughGoldTooltip = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.gold())))
        if not enoughCredits:
            diff = text_styles.credits(priceCredits - g_itemsCache.items.stats.credits)
            notEnoughCreditsTooltip = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.credits())))
        self.as_setTotalDataS({'credits': formatPriceCredits(priceCredits),
         'gold': formatPriceGold(priceGold),
         'totalLabel': text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TOTALCOST, selected=len(self.__searchDP.selectedItems), total=len(self.__searchDP.items))),
         'enoughGold': enoughGold,
         'enoughCredits': enoughCredits,
         'notEnoughGoldTooltip': notEnoughGoldTooltip,
         'notEnoughCreditsTooltip': notEnoughCreditsTooltip})
        self.as_setBuyBtnEnabledS(canBuy)

    @process
    def __buyElements(self, purchaseItems, replacedElementGroups):
        if any(replacedElementGroups):
            isContinue = yield DialogsInterface.showDialog(getDialogReplaceElements(replacedElementGroups))
        else:
            isContinue = True
        if isContinue:
            self.as_setBuyBtnEnabledS(False)
            self.__controller.cart.purchaseMultiple(purchaseItems)


class PurchaseDataProvider(SortableDAAPIDataProvider):

    def __init__(self, cart):
        super(PurchaseDataProvider, self).__init__()
        self._list = []
        self._cart = cart
        self.buildList(self._cart.items)
        self.selectionChanged = Event()

    def emptyItem(self):
        return None

    @property
    def collection(self):
        return self._list

    @property
    def items(self):
        """ Get a collection of cart items excluding group headers.
        
        Group headers(e.g. "Camouflages:") are presented as regular items, but they
        have a special key (titleMode) so they can be tracked and thrown out.
        
        :return: list
        """
        return filter(lambda item: not item['titleMode'], self._list)

    @property
    def selectedItems(self):
        """ Get only selected cart items.
        
        :return: list
        """
        return filter(lambda item: item['selected'], self.items)

    def buildList(self, cartItems):
        self.clear()
        elementGroups = [[], [], []]
        for item in cartItems:
            element = item['object']
            dropdownItem = {'id': element.getID(),
             'slotIdx': item['idx'],
             'selected': item['isSelected'],
             'cType': item['type'],
             'itemName': element.getName(),
             'imgBonus': element.qualifier.getIcon16x16(),
             'price': element.getPrice(item['duration']),
             'lblBonus': text_styles.stats('+{0}%{1}'.format(element.qualifier.getValue(), '*' if element.qualifier.getDescription() is not None else '')),
             'titleMode': False,
             'DDPrice': _getDropdownPriceVO(element),
             'selectIndex': DURATION.ALL.index(item['duration']),
             'isDuplicatePrice': item['isDuplicate'],
             'duplicatePriceText': icons.info() + _ms(VEHICLE_CUSTOMIZATION.BUYWINDOW_BUYTIME_COPY),
             'duplicatePriceTooltip': makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYWINDOW_COPY_HEADER), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYWINDOW_COPY_BODY))}
            elementGroups[item['type']].append(dropdownItem)

        for elements, title in zip(elementGroups, _CUSTOMIZATION_TYPE_TITLES):
            if elements:
                elements.insert(0, {'titleMode': True,
                 'titleText': _ms(text_styles.middleTitle(title))})

        self._list = list(itertools.chain(*elementGroups))
        return

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self._cart = None
        self._dispose()
        return

    def setSelected(self, itemIdx, selected):

        def action(cartItem, listItem):
            cartItem['isSelected'] = selected
            listItem['selected'] = selected

        self.__doActionOnItem(itemIdx, action)

    def setPrice(self, itemIdx, priceIdx):

        def action(cartItem, listItem):
            duration = DURATION.ALL[priceIdx]
            cartItem['duration'] = duration
            listItem['selectIndex'] = priceIdx
            listItem['price'] = cartItem['object'].getPrice(duration)

        self.__doActionOnItem(itemIdx, action)

    def _iterateOverItems(self):
        correction = 0
        for idx, item in enumerate(self._list):
            if item['titleMode']:
                correction += 1
            cartItem = self._cart.items[idx - correction]
            listItem = self._list[idx]
            yield (idx, listItem, cartItem)

    def __doActionOnItem(self, itemIdx, action):
        for idx, listItem, cartItem in self._iterateOverItems():
            if idx == itemIdx:
                action(cartItem, listItem)
                break

        self._cart.recalculateTotalPrice()
        for _, listItem, cartItem in self._iterateOverItems():
            listItem['isDuplicatePrice'] = cartItem['isDuplicate']

        self.refresh()
        self.selectionChanged()
