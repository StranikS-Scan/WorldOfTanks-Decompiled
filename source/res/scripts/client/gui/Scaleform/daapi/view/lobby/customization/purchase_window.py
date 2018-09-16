# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/purchase_window.py
from collections import namedtuple
import GUI
from adisp import process
from CurrentVehicle import g_currentVehicle
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta, ExchangeCreditsMultiItemsMeta, InfoItemBase
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.meta.CustomizationBuyWindowMeta import CustomizationBuyWindowMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, icons, getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from shared import getTotalPurchaseInfo, AdditionalPurchaseGroups
_CUSTOMIZATION_SEASON_TITLES = {SeasonType.WINTER: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_WINTER,
 SeasonType.SUMMER: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_SUMMER,
 SeasonType.DESERT: VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_DESERT}
_SelectItemData = namedtuple('_SelectItemData', ('season', 'quantity', 'purchaseIndices'))

class CartInfoItem(InfoItemBase):

    @property
    def itemTypeName(self):
        pass

    @property
    def userName(self):
        pass

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.CUSTOMIZATION

    def getExtraIconInfo(self):
        return None

    def getGUIEmblemID(self):
        pass


class _MoneyForPurchase(object):
    NOT_ENOUGH = 0
    ENOUGH_WITH_EXCHANGE = 1
    ENOUGH = 2


class PurchaseWindow(CustomizationBuyWindowMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(PurchaseWindow, self).__init__(ctx)
        self.__ctx = None
        self.__c11nView = None
        self.__purchaseItems = []
        self.__isStyle = False
        self.__items = {}
        self.__counters = {season:[0, 0] for season in SeasonType.COMMON_SEASONS}
        self.__moneyState = _MoneyForPurchase.NOT_ENOUGH
        self.__blur = GUI.WGUIBackgroundBlur()
        return

    def selectItem(self, itemId, fromStorage):
        self.__selectItem(itemId, fromStorage, True)

    def deselectItem(self, itemId, fromStorage):
        self.__selectItem(itemId, fromStorage, False)

    @process
    def buy(self):
        if self.__moneyState is _MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            if self.__isStyle:
                item = self.__purchaseItems[0].item
                meta = ExchangeCreditsSingleItemMeta(item.intCD)
            else:
                itemsCDs = [ purchaseItem.item.intCD for purchaseItem in self.__purchaseItems ]
                meta = ExchangeCreditsMultiItemsMeta(itemsCDs, CartInfoItem())
            yield DialogsInterface.showDialog(meta)
            return
        self.__ctx.applyItems(self.__purchaseItems)
        self.close()

    def onWindowClose(self):
        self.close()

    def close(self):
        self.__c11nView.changeVisible(True)
        self.destroy()

    def _populate(self):
        super(PurchaseWindow, self)._populate()
        self.service.suspendHighlighter()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__c11nView = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB).getView()
        self.__ctx = self.service.getCtx()
        purchaseItems = self.__ctx.getPurchaseItems()
        g_clientUpdateManager.addMoneyCallback(self.__setTotalData)
        self.__isStyle, self.__purchaseItems, processor = _ProcessorSelector.selectFor(purchaseItems)
        processor.process(self.__purchaseItems)
        itemDescriptors = processor.itemsDescriptors
        if not self.__isStyle:
            for season in SeasonType.COMMON_SEASONS:
                for item in itemDescriptors[season]:
                    self.__items[item.identificator] = _SelectItemData(season, item.quantity, item.purchaseIndices)
                    self.__counters[season][int(item.isFromInventory)] += item.quantity

        self.as_setDataS({'summerData': [ item.getVO() for item in itemDescriptors[SeasonType.SUMMER] ],
         'winterData': [ item.getVO() for item in itemDescriptors[SeasonType.WINTER] ],
         'desertData': [ item.getVO() for item in itemDescriptors[SeasonType.DESERT] ]})
        self.__setTitlesData()
        self.__setTotalData()
        self.__blur.enable = True
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.MENY_HIDE, ctx={'hide': True}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.MENY_HIDE, ctx={'hide': False}), EVENT_BUS_SCOPE.LOBBY)
        self.service.resumeHighlighter()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__ctx = None
        self.__c11nView = None
        self.__blur.enable = False
        super(PurchaseWindow, self)._dispose()
        return

    def __selectItem(self, itemId, fromStorage, select):
        itemData = self.__items[itemId]
        self.__counters[itemData.season][int(fromStorage)] += itemData.quantity if select else -itemData.quantity
        for idx in itemData.purchaseIndices:
            self.__purchaseItems[idx].selected = select

        self.__setTotalData()
        self.__setTitlesData()

    def __setTitlesData(self):
        seasonTitlesText = {season:_ms(_CUSTOMIZATION_SEASON_TITLES[season]) for season in SeasonType.COMMON_SEASONS}
        if self.__isStyle:
            item = self.__ctx.getPurchaseItems()[0].item
            titleTemplate = '{} {}'.format(item.userType, item.userName)
            bigTitleTemplate = '{}\n{}'.format(item.userType, text_styles.heroTitle(item.userName))
        else:
            totalCount = 0
            for season in SeasonType.COMMON_SEASONS:
                purchase, inventory = self.__counters[season]
                count = purchase + inventory
                totalCount += count
                seasonTitlesText[season] += (text_styles.unavailable(' ({})') if count == 0 else ' ({})').format(count)

            titleTemplate = '{} ({})'.format(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYWINDOW_TITLE), totalCount)
            bigTitleTemplate = text_styles.grandTitle(titleTemplate)
        titleText = text_styles.promoTitle(bigTitleTemplate)
        titleTextSmall = text_styles.promoTitle(titleTemplate)
        self.as_setInitDataS({'buyDisabledTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY,
         'windowTitle': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_HEADER,
         'isStyle': self.__isStyle,
         'titleText': titleText,
         'titleTextSmall': titleTextSmall})
        self.as_setTitlesS({'summerTitle': seasonTitlesText[SeasonType.SUMMER],
         'winterTitle': seasonTitlesText[SeasonType.WINTER],
         'desertTitle': seasonTitlesText[SeasonType.DESERT]})

    def __setTotalData(self, *_):
        cart = getTotalPurchaseInfo(self.__purchaseItems)
        totalPriceVO = getItemPricesVO(cart.totalPrice)
        state = g_currentVehicle.getViewState()
        inFormationAlert = ''
        if not state.isCustomizationEnabled():
            inFormationAlert = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_FORMATION_ALERT))
        price = cart.totalPrice.price
        money = self.itemsCache.items.stats.money
        exchangeRate = self.itemsCache.items.shop.exchangeRate
        shortage = money.getShortage(price)
        if not shortage:
            self.__moneyState = _MoneyForPurchase.ENOUGH
        else:
            money = money - price + shortage
            price = shortage
            money = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate, default=0)
            shortage = money.getShortage(price)
            if not shortage:
                self.__moneyState = _MoneyForPurchase.ENOUGH_WITH_EXCHANGE
            else:
                self.__moneyState = _MoneyForPurchase.NOT_ENOUGH
        self.as_setTotalDataS({'totalLabel': text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TOTALCOST, selected=cart.numSelected, total=cart.numApplying)),
         'enoughMoney': self.__moneyState is not _MoneyForPurchase.NOT_ENOUGH,
         'inFormationAlert': inFormationAlert,
         'totalPrice': totalPriceVO[0]})
        self.__setBuyButtonState()

    def __setBuyButtonState(self):
        purchase = 1 if self.__isStyle else 0
        purchase += sum([ self.__counters[season][0] for season in SeasonType.COMMON_SEASONS ])
        inventory = sum([ self.__counters[season][1] for season in SeasonType.COMMON_SEASONS ])
        if purchase > 0:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY
        else:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNAPPLY
        isEnabled = self.__moneyState is not _MoneyForPurchase.NOT_ENOUGH
        isAnySelected = purchase + inventory > 0
        if not isAnySelected:
            label = ''
        self.as_setBuyBtnStateS(isEnabled and isAnySelected, label)

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            self.destroy()


class _ProcessorSelector(object):

    @staticmethod
    def selectFor(items):
        itemsToProcess = _ProcessorSelector.__preprocess(items)
        isStyle = _ProcessorSelector.__isStyle(itemsToProcess)
        processor = _StyleItemsProcessor() if isStyle else _SeparateItemsProcessor()
        return (isStyle, itemsToProcess, processor)

    @staticmethod
    def __isStyle(items):
        return len(items) == 1 and items[0].group == AdditionalPurchaseGroups.STYLES_GROUP_ID

    @staticmethod
    def __preprocess(items):
        return [ item for item in items if not item.isDismantling ]


class _BasePurchaseDescription(object):
    __slots__ = ('intCD', 'identificator', 'itemData', 'quantity', 'purchaseIndices')

    def __init__(self, item, purchaseIdx=0, quantity=1):
        self.intCD = item.intCD
        self.identificator = self.intCD
        self.itemData = self._buildCustomizationItemData(item)
        self.quantity = quantity
        self.purchaseIndices = [purchaseIdx]

    def getVO(self):
        itemVO = {'id': self.identificator,
         'itemImg': self.itemData,
         'quantity': self.quantity}
        return itemVO

    def addPurchaseIndices(self, indices):
        self.quantity += 1
        self.purchaseIndices.extend(indices)

    @staticmethod
    def _buildCustomizationItemData(item):
        return buildCustomizationItemDataVO(item, None, True, False, True, addExtraName=False)


class _StubItemPurchaseDescription(_BasePurchaseDescription):
    __slots__ = ('isFromInventory',)
    _StubItem = namedtuple('_StubItem', ('intCD',))

    def __init__(self):
        super(_StubItemPurchaseDescription, self).__init__(self._StubItem(-1), quantity=0)
        self.isFromInventory = False

    def getVO(self):
        itemVO = super(_StubItemPurchaseDescription, self).getVO()
        itemVO.update({'itemImg': self.itemData,
         'isLock': True})
        return itemVO

    @staticmethod
    def _buildCustomizationItemData(item):
        itemData = {'intCD': 0,
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL,
         'isGhost': True}
        return itemData


class _SeparateItemPurchaseDescription(_BasePurchaseDescription):
    __slots__ = ('intCD', 'identificator', 'selected', 'itemData', 'compoundPrice', 'quantity', 'isFromInventory', 'purchaseIndices')

    def __init__(self, purchaseItem, purchaseIdx):
        super(_SeparateItemPurchaseDescription, self).__init__(purchaseItem.item, purchaseIdx)
        self.identificator = self.__generateID(purchaseItem)
        self.selected = purchaseItem.selected
        self.compoundPrice = purchaseItem.price
        self.isFromInventory = purchaseItem.isFromInventory

    def getVO(self):
        itemVO = super(_SeparateItemPurchaseDescription, self).getVO()
        itemVO.update({'compoundPrice': getItemPricesVO(self.compoundPrice)[0],
         'isFromStorage': self.isFromInventory,
         'selected': self.selected})
        return itemVO

    def __generateID(self, item):
        return hash((self.intCD, item.group, item.isFromInventory))


class _StyleItemPurchaseDescription(_BasePurchaseDescription):

    def getVO(self):
        itemVO = super(_StyleItemPurchaseDescription, self).getVO()
        itemVO.update({'isFromStorage': False,
         'isLock': True})
        return itemVO


class _SeasonPurchaseInfo(object):
    _ORDERED_KEYS = (GUI_ITEM_TYPE.INSCRIPTION,
     GUI_ITEM_TYPE.MODIFICATION,
     GUI_ITEM_TYPE.PAINT,
     GUI_ITEM_TYPE.CAMOUFLAGE,
     GUI_ITEM_TYPE.EMBLEM)

    def __init__(self, keyFunc=None):
        self.__buckets = {key:{} for key in self._ORDERED_KEYS}
        self.__keyFunc = keyFunc or self.__defaultKeyFunc

    def add(self, purchaseItemInfo, typeID):
        if typeID in self._ORDERED_KEYS:
            bucket = self.__buckets[typeID]
            key = self.__keyFunc(purchaseItemInfo)
            if key in bucket:
                bucket[key].addPurchaseIndices(purchaseItemInfo.purchaseIndices)
            else:
                bucket[key] = purchaseItemInfo

    def flatten(self):
        items = []
        for key in self._ORDERED_KEYS:
            bucket = self.__buckets[key].values()
            bucket.sort(key=self.__defaultKeyFunc)
            items.extend(bucket)

        return items

    @staticmethod
    def __defaultKeyFunc(item):
        return item.intCD


class _ItemsProcessor(object):

    @property
    def itemsDescriptors(self):
        return self.__itemsDescriptors

    def __init__(self):
        self.__itemsDescriptors = {season:[] for season in SeasonType.COMMON_SEASONS}

    def getItemsDescriptors(self):
        return self.__itemsDescriptors

    def process(self, items):
        items = self._preProcess(items)
        itemsInfo = self._process(items)
        self._postProcess(itemsInfo)

    def _preProcess(self, items):
        return items

    def _process(self, items):
        raise NotImplementedError

    def _postProcess(self, itemsInfo):
        for season in SeasonType.COMMON_SEASONS:
            if season in itemsInfo:
                items = itemsInfo[season].flatten()
            else:
                items = [_StubItemPurchaseDescription()]
            self.__itemsDescriptors[season] = items


class _SeparateItemsProcessor(_ItemsProcessor):

    def _process(self, items):
        itemsInfo = {}
        for idx, item in enumerate(items):
            itemDescription = _SeparateItemPurchaseDescription(item, idx)
            seasonInfo = itemsInfo.setdefault(item.group, _SeasonPurchaseInfo(self._getKey))
            seasonInfo.add(itemDescription, item.item.itemTypeID)

        return itemsInfo

    @staticmethod
    def _getKey(item):
        return (item.intCD, item.isFromInventory)


class _StyleItemsProcessor(_ItemsProcessor):

    def _preProcess(self, items):
        return items[0]

    def _process(self, style):
        itemsInfo = {}
        for season in SeasonType.COMMON_SEASONS:
            outfit = style.item.getOutfit(season)
            seasonInfo = itemsInfo.setdefault(season, _SeasonPurchaseInfo())
            for item in outfit.items():
                itemDescription = _StyleItemPurchaseDescription(item)
                seasonInfo.add(itemDescription, item.itemTypeID)

        return itemsInfo
