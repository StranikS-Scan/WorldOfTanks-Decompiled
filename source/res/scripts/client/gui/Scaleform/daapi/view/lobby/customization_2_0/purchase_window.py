# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization_2_0/purchase_window.py
import copy
from Event import Event
from adisp import process
from debug_utils import LOG_ERROR
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.customization_2_0.shared import getDialogReplaceElements
from gui.Scaleform.daapi.view.meta.CustomizationBuyWindowMeta import CustomizationBuyWindowMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.CUSTOMIZATION import CUSTOMIZATION
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip, getAbsoluteUrl
from helpers.i18n import makeString as _ms
from gui import makeHtmlString
from gui.customization_2_0 import g_customizationController, data_aggregator
from gui.customization_2_0.data_aggregator import DURATION
from gui.customization_2_0.shared import formatPriceCredits, formatPriceGold, getSalePriceString

class PurchaseWindow(CustomizationBuyWindowMeta):

    def __init__(self, ctx=None):
        super(PurchaseWindow, self).__init__()

    def selectItem(self, itemIdx):
        self.__searchDP.setSelected(itemIdx, True)

    def deselectItem(self, itemIdx):
        self.__searchDP.setSelected(itemIdx, False)

    def changePriceItem(self, itemIdx, price):
        self.__searchDP.setPrice(itemIdx, price)

    def onWindowClose(self):
        self.destroy()

    @process
    def buy(self):
        isContinue = True
        isShowReplaceDialog = False
        replaceElements = [[], [], []]
        selectedItems = []
        for item in self.__searchDP.collection:
            if item['titleMode']:
                continue
            if item['selected']:
                installedItem = g_customizationController.carousel.slots.getInstalledItem(item['slotIdx'], item['cType'])
                if installedItem.duration > 0:
                    isShowReplaceDialog = True
                    availableItem = g_customizationController.carousel.slots.getItemById(item['cType'], installedItem.getID())
                    replaceElements[item['cType']].append(text_styles.main(availableItem.getName()))
                if item['isDuplicatePrice']:
                    item['price'] = 0
            selectedItems.append(item)

        if isShowReplaceDialog:
            isContinue = yield DialogsInterface.showDialog(getDialogReplaceElements(replaceElements))
        if isContinue:
            g_customizationController.carousel.slots.cart.buyItems(copy.deepcopy(selectedItems))

    def _dispose(self):
        self.__searchDP.selectionChanged -= self.__setTotalData
        self.__searchDP.fini()
        if g_customizationController.carousel is not None:
            g_customizationController.carousel.slots.cart.purchaseProcessed -= self.destroy
            g_customizationController.carousel.slots.cart.availableMoneyUpdated -= self.__setTotalData
            for item in g_customizationController.carousel.slots.cart.items:
                item['isSelected'] = True
                item['duration'] = item['initialDuration']

        super(PurchaseWindow, self)._dispose()
        return

    def _populate(self):
        super(PurchaseWindow, self)._populate()
        g_customizationController.carousel.slots.cart.purchaseProcessed += self.destroy
        g_customizationController.carousel.slots.cart.availableMoneyUpdated += self.__setTotalData
        self.__totalPrice = {'gold': g_customizationController.carousel.slots.cart.totalPriceGold,
         'credits': g_customizationController.carousel.slots.cart.totalPriceCredits}
        self.__searchDP = PurchaseDataProvider(g_customizationController.carousel.slots.cart.items, self.__totalPrice)
        self.__searchDP.setFlashObject(self.as_getPurchaseDPS())
        self.__searchDP.selectionChanged += self.__setTotalData
        self.as_setInitDataS({'windowTitle': CUSTOMIZATION.WINDOW_PURCHASE_HEADER,
         'imgGold': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1,
         'imgCredits': RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1,
         'btnBuyLabel': CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY,
         'btnCancelLabel': CUSTOMIZATION.WINDOW_PURCHASE_BTNCANCEL,
         'buyDisabledTooltip': TOOLTIPS.CUSTOMIZATION_BUYDISABLED_BODY,
         'defaultSortIndex': 0,
         'tableHeader': [self.__packHeaderColumnData('itemName', text_styles.main(CUSTOMIZATION.WINDOW_PURCHASE_TABLEHEADER_ITEMS), 250), self.__packHeaderColumnData('lblBonus', text_styles.main(CUSTOMIZATION.WINDOW_PURCHASE_TABLEHEADER_BONUS), 110), self.__packHeaderColumnData('lblPrice', text_styles.main(CUSTOMIZATION.WINDOW_PURCHASE_TABLEHEADER_COST), 150)]})
        self.__setTotalData()

    def __setTotalData(self):
        notEnoughGoldTooltip = notEnoughCreditsTooltip = ''
        enoughGold = g_itemsCache.items.stats.gold >= self.__totalPrice['gold']
        enoughCredits = g_itemsCache.items.stats.credits >= self.__totalPrice['credits']
        buyEnabled = bool(self.__totalPrice['credits'] + self.__totalPrice['gold']) and enoughGold and enoughCredits
        if not enoughGold:
            diff = text_styles.gold(self.__totalPrice['gold'] - g_itemsCache.items.stats.gold)
            notEnoughGoldTooltip = makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.gold())))
        if not enoughCredits:
            diff = text_styles.credits(self.__totalPrice['credits'] - g_itemsCache.items.stats.credits)
            notEnoughCreditsTooltip = makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.credits())))
        self.as_setTotalDataS({'credits': formatPriceCredits(self.__totalPrice['credits']),
         'gold': formatPriceGold(self.__totalPrice['gold']),
         'totalLabel': text_styles.highTitle(_ms(CUSTOMIZATION.WINDOW_PURCHASE_TOTALCOST, selected=len(self.__searchDP.getSelected()), total=len(self.__searchDP.getTotal()))),
         'buyEnabled': buyEnabled,
         'enoughGold': enoughGold,
         'enoughCredits': enoughCredits,
         'notEnoughGoldTooltip': notEnoughGoldTooltip,
         'notEnoughCreditsTooltip': notEnoughCreditsTooltip})

    @staticmethod
    def __packHeaderColumnData(idx, label, buttonWidth, tooltip='', icon='', sortOrder=-1, showSeparator=True):
        return {'id': idx,
         'label': _ms(label),
         'iconSource': icon,
         'buttonWidth': buttonWidth,
         'toolTip': tooltip,
         'sortOrder': sortOrder,
         'defaultSortDirection': 'ascending',
         'buttonHeight': 50,
         'showSeparator': showSeparator,
         'enabled': False}


class PurchaseDataProvider(SortableDAAPIDataProvider):

    def __init__(self, cartItems, totalPrice):
        super(PurchaseDataProvider, self).__init__()
        self._listMapping = {}
        self._list = []
        self.__cartItems = cartItems
        self.__mapping = {}
        self.__selectedID = None
        self.__totalPrice = totalPrice
        self.__setList(cartItems)
        self.selectionChanged = Event()
        return

    @property
    def collection(self):
        return self._list

    def buildList(self, cartItems):
        self.clear()
        self.__setList(cartItems)

    def emptyItem(self):
        return None

    def getSelected(self):
        return filter(lambda item: item['selected'], self.getTotal())

    def getTotal(self):
        return filter(lambda item: not item['titleMode'], self._list)

    def clear(self):
        self._list = None
        self._listMapping.clear()
        self.__mapping.clear()
        self.__selectedID = None
        return

    def fini(self):
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        return self.__mapping[self.__selectedID] if self.__selectedID in self.__mapping else -1

    def setSelectedID(self, idx):
        self.__selectedID = idx

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def setSelected(self, itemIdx, selected):

        def action(cartItem):
            cartItem['isSelected'] = selected

        self.__actionOnItem(itemIdx, action)

    def setPrice(self, itemIdx, priceIdx):

        def action(cartItem):
            cartItem['duration'] = DURATION.ALL[priceIdx]

        self.__actionOnItem(itemIdx, action)

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(PurchaseDataProvider, self).pySortOn(fields, order)

    def __setList(self, cartItems):
        self._list = []
        emblemItems = []
        camouflageItems = []
        inscriptionItems = []
        for item in cartItems:
            dpItem = {'id': item['itemID'],
             'slotIdx': item['idx'],
             'selected': item['isSelected'],
             'cType': item['type'],
             'itemName': item['name'],
             'imgBonus': item['bonusIcon'],
             'price': item['object'].getPrice(item['duration']),
             'lblBonus': text_styles.stats('+{0}%{1}'.format(item['bonusValue'], item['isConditional'])),
             'titleMode': False,
             'DDPrice': self.__getDropdownPriceVO(item),
             'selectIndex': DURATION.ALL.index(item['duration']),
             'isDuplicatePrice': item['isDuplicate'],
             'duplicatePriceText': icons.info() + _ms(CUSTOMIZATION.BUYWINDOW_BUYTIME_COPY),
             'duplicatePriceTooltip': makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_BUYWINDOW_COPY_HEADER), _ms(TOOLTIPS.CUSTOMIZATION_BUYWINDOW_COPY_BODY))}
            if item['type'] == data_aggregator.CUSTOMIZATION_TYPE.CAMOUFLAGE:
                camouflageItems.append(dpItem)
            if item['type'] == data_aggregator.CUSTOMIZATION_TYPE.EMBLEM:
                emblemItems.append(dpItem)
            if item['type'] == data_aggregator.CUSTOMIZATION_TYPE.INSCRIPTION:
                inscriptionItems.append(dpItem)

        if camouflageItems:
            camouflageItems.insert(0, self.__getTitle(CUSTOMIZATION.BUYWINDOW_TITLE_CAMOUFLAGE))
        if inscriptionItems:
            inscriptionItems.insert(0, self.__getTitle(CUSTOMIZATION.BUYWINDOW_TITLE_INSCRIPTION))
        if emblemItems:
            emblemItems.insert(0, self.__getTitle(CUSTOMIZATION.BUYWINDOW_TITLE_EMBLEM))
        self._list = camouflageItems + emblemItems + inscriptionItems

    def __getDropdownPriceVO(self, item):
        dropdownPriceVO = []
        for duration, text in [(DURATION.PERMANENT, CUSTOMIZATION.BUYWINDOW_BUYTIME_EVER), (DURATION.MONTH, CUSTOMIZATION.BUYWINDOW_BUYTIME_THIRTYDAYS), (DURATION.WEEK, CUSTOMIZATION.BUYWINDOW_BUYTIME_SEVENDAYS)]:
            if duration == DURATION.PERMANENT:
                textStyle = text_styles.gold
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2
            else:
                textStyle = text_styles.credits
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2
            dropdownItem = {'labelPrice': text_styles.main(_ms(text)),
             'label': makeHtmlString('html_templates:lobby/customization', 'DDString', {'text': textStyle(item['object'].getPrice(duration)),
                       'icon': getAbsoluteUrl(icon)})}
            salePrice = self.__getSalePrice(item, duration)
            if salePrice is not None:
                dropdownItem['salePrice'] = salePrice
                dropdownItem['isSale'] = True
            dropdownPriceVO.append(dropdownItem)

        return dropdownPriceVO

    def __actionOnItem(self, itemIdx, action=None):
        correction = 0
        for item in self._list:
            if item['titleMode']:
                correction += 1
                continue
            if self._list.index(item) == itemIdx:
                if action is not None:
                    action(self.__cartItems[itemIdx - correction])
                cart = g_customizationController.carousel.slots.cart
                cart.markDuplicates()
                cart.recalculateTotalPrice()
                self.__totalPrice['gold'] = cart.totalPriceGold
                self.__totalPrice['credits'] = cart.totalPriceCredits
                self.buildList(self.__cartItems)
                self.refresh()
                self.selectionChanged()
                return

        return

    def __getTitle(self, title):
        return {'titleMode': True,
         'titleText': _ms(text_styles.middleTitle(title))}

    def __getSalePrice(self, item, duration):
        if item['object'].isSale(duration):
            return getSalePriceString(item['type'], item['object'], duration)
        else:
            return None
            return None
