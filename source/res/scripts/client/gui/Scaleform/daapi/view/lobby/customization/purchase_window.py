# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/purchase_window.py
from CurrentVehicle import g_currentVehicle
from Event import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.meta.CustomizationBuyWindowMeta import CustomizationBuyWindowMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, icons, getItemPricesVO
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from shared import getTotalPurchaseInfo, AdditionalPurchaseGroups
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_CUSTOMIZATION_SEASON_TITLES = {AdditionalPurchaseGroups.STYLES_GROUP_ID: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_ACTIVESTYLE,
 SeasonType.WINTER: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_WINTER,
 SeasonType.SUMMER: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_SUMMER,
 SeasonType.DESERT: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_DESERT}
PURCHASE_GROUPS = (AdditionalPurchaseGroups.STYLES_GROUP_ID,
 SeasonType.SUMMER,
 SeasonType.WINTER,
 SeasonType.DESERT)

def _getColumnHeaderVO(idx, label, buttonWidth, align, showSeparator):
    return {'id': idx,
     'label': _ms(label),
     'iconSource': '',
     'buttonWidth': buttonWidth,
     'toolTip': '',
     'sortOrder': -1,
     'defaultSortDirection': 'ascending',
     'buttonHeight': 50,
     'showSeparator': showSeparator,
     'enabled': False,
     'textAlign': align}


class PurchaseWindow(CustomizationBuyWindowMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(PurchaseWindow, self).__init__(ctx)
        self._c11nView = None
        self._purchaseItems = []
        self._highlighterMode = None
        self._needRestart = False
        return

    def selectItem(self, itemIdx):
        """ ActionScript call for when an purchase item is checked.
        """
        self._c11nView.soundManager.playInstantSound(SOUNDS.SELECT)
        selectCount, inventoryCount = self.__searchDP.setSelected(itemIdx, True)
        self.__setBuyButtonState(selectCount, inventoryCount)

    def deselectItem(self, itemIdx):
        """ ActionScript call for when a purchase item is unchecked.
        """
        self._c11nView.soundManager.playInstantSound(SOUNDS.SELECT)
        selectCount, inventoryCount = self.__searchDP.setSelected(itemIdx, False)
        self.__setBuyButtonState(selectCount, inventoryCount)

    def onWindowClose(self):
        self.destroy()

    def buy(self):
        self._c11nView.buyAndExit(self._purchaseItems)
        self.destroy()

    def _populate(self):
        super(PurchaseWindow, self)._populate()
        if self.service.getHightlighter():
            self._needRestart = True
            self._highlighterMode = self.service.getSelectionMode()
            self.service.stopHighlighter()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._c11nView = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB).getView()
        self._purchaseItems = self._c11nView.getPurchaseItems()
        g_clientUpdateManager.addMoneyCallback(self.__setTotalData)
        self.__searchDP = PurchaseDataProvider(self._purchaseItems)
        self.__searchDP.setFlashObject(self.as_getPurchaseDPS())
        self.__searchDP.selectionChanged += self.__setTotalData
        self.as_setInitDataS({'btnCancelLabel': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNCANCEL,
         'buyDisabledTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY,
         'windowTitle': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_HEADER,
         'btnBuyLabel': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY})
        self.__setTotalData()

    def _dispose(self):
        if self._needRestart:
            self.service.startHighlighter(self._highlighterMode)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__searchDP.selectionChanged -= self.__setTotalData
        self.__searchDP.fini()
        super(PurchaseWindow, self)._dispose()

    def __setTotalData(self, *_):
        cart = getTotalPurchaseInfo(self._purchaseItems)
        totalPriceVO = getItemPricesVO(cart.totalPrice)
        state = g_currentVehicle.getViewState()
        shortage = self.itemsCache.items.stats.money.getShortage(cart.totalPrice.price)
        inFormationAlert = ''
        if not state.isCustomizationEnabled():
            inFormationAlert = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_FORMATION_ALERT))
        self.as_setTotalDataS({'totalLabel': text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TOTALCOST, selected=cart.numSelected, total=cart.numApplying)),
         'enoughMoney': getItemPricesVO(ItemPrice(shortage, shortage))[0],
         'inFormationAlert': inFormationAlert,
         'totalPrice': totalPriceVO[0]})

    def __setBuyButtonState(self, selectCount, inventoryCount):
        isEnabled = selectCount > 0
        if selectCount and inventoryCount == selectCount:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNAPPLY
        else:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY
        self.as_setBuyBtnStateS(isEnabled, label)

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            self.destroy()


class PurchaseDataProvider(SortableDAAPIDataProvider):

    def __init__(self, purchaseItems):
        super(PurchaseDataProvider, self).__init__()
        self._list = []
        self._purchaseItems = purchaseItems
        self._purchaseItemSets = []
        self.buildList(self._purchaseItems)
        self.selectionChanged = Event()
        self.numSelected = len(self._purchaseItems)
        self.numInventory = len([ item for item in purchaseItems if item.isFromInventory ])

    def updateCollection(self, purchaseItems):
        del self._list[:]
        self._purchaseItems = purchaseItems
        self.buildList(self._purchaseItems)
        self.numSelected = len(purchaseItems)
        self.numInventory = len([ item for item in purchaseItems if item.isFromInventory ])

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

    def buildList(self, purchaseItems):
        self.clear()
        elementGroups = {group:[] for group in PURCHASE_GROUPS}
        elementSets = {group:[] for group in PURCHASE_GROUPS}
        purchaseItemsCopy = self._purchaseItems[:]
        while purchaseItemsCopy:
            element = purchaseItemsCopy[0]
            if element.isDismantling:
                purchaseItemsCopy.pop(0)
                continue

            def filterItems(otherElement):
                correctType = otherElement.item.intCD == element.item.intCD
                correctSeason = otherElement.group == element.group
                correctAction = otherElement.isFromInventory == element.isFromInventory and otherElement.isDismantling == element.isDismantling
                return correctSeason and correctType and correctAction

            matchedItems = filter(filterItems, purchaseItemsCopy)
            for delItem in matchedItems:
                purchaseItemsCopy.remove(delItem)

            quantity = len(matchedItems)
            if quantity == 1:
                itemName = element.item.userName
            else:
                itemName = '{} x{}'.format(element.item.userName, quantity)
            priceItem = {'id': element.item.intCD,
             'selected': element.selected,
             'itemImg': buildCustomizationItemDataVO(element.item, None, True, False, False),
             'itemName': itemName,
             'titleMode': False,
             'compoundPrice': getItemPricesVO(element.price * quantity)[0],
             'isFromStorage': element.isFromInventory}
            group = element.group
            elementGroups[group].append(priceItem)
            elementSets[group].append(matchedItems)

        self._list = []
        self._purchaseItemSets = []
        for group in PURCHASE_GROUPS:
            items = elementGroups[group]
            sets = elementSets[group]
            if items:
                title = _CUSTOMIZATION_SEASON_TITLES[group]
                self._list.append({'titleMode': True,
                 'titleText': _ms(text_styles.middleTitle(title))})
                self._list.extend(items)
                self._purchaseItemSets.extend(sets)

        return

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self.destroy()

    def setSelected(self, itemIdx, selected):
        self.numSelected = 0
        self.numInventory = 0

        def action(cartItem, listItem):
            cartItem.selected = selected
            listItem['selected'] = selected

        self.__doActionOnItem(itemIdx, action)
        for _, _, cartItem in self._iterateOverItems():
            if cartItem.selected:
                self.numSelected += 1
                if cartItem.isFromInventory:
                    self.numInventory += 1

        return (self.numSelected, self.numInventory)

    def _iterateOverItems(self):
        correction = 0
        for idx, item in enumerate(self._list):
            if item['titleMode']:
                correction += 1
            cartItems = self._purchaseItemSets[idx - correction]
            listItem = self._list[idx]
            for cartItem in cartItems:
                yield (idx, listItem, cartItem)

    def __doActionOnItem(self, itemIdx, action):
        for idx, listItem, cartItem in self._iterateOverItems():
            if idx == itemIdx:
                action(cartItem, listItem)

        self.refresh()
        self.selectionChanged()
