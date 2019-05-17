# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/purchase_window.py
from collections import namedtuple
import GUI
from adisp import process
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta, ExchangeCreditsMultiItemsMeta, InfoItemBase
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import containsVehicleBound
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.CustomizationBuyWindowMeta import CustomizationBuyWindowMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.CUSTOMIZATION_DIALOGS import CUSTOMIZATION_DIALOGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.ingame_shop import showBuyGoldForCustomization
from gui.shared.formatters import text_styles, icons, getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.money import Currency
from gui.shared import event_dispatcher
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from shared import getTotalPurchaseInfo, AdditionalPurchaseGroups, getPurchaseMoneyState, MoneyForPurchase, isTransactionValid
_CUSTOMIZATION_SEASON_TITLES = {SeasonType.WINTER: backport.text(R.strings.vehicle_customization.buyWindow.title.winter()),
 SeasonType.SUMMER: backport.text(R.strings.vehicle_customization.buyWindow.title.summer()),
 SeasonType.DESERT: backport.text(R.strings.vehicle_customization.buyWindow.title.desert())}
_CUSTOMIZATION_TUTORIAL_CHAPTER = 'c11nProlong'
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
        self.__moneyState = MoneyForPurchase.NOT_ENOUGH
        self.__blur = GUI.WGUIBackgroundBlur()
        self.__prolongStyleRent = (ctx or {}).get('prolongStyleRent', False)
        return

    def selectItem(self, itemId, fromStorage):
        self.__selectItem(itemId, fromStorage, True)

    def deselectItem(self, itemId, fromStorage):
        self.__selectItem(itemId, fromStorage, False)

    @process
    def buy(self):
        if self.__moneyState is MoneyForPurchase.NOT_ENOUGH:
            if isIngameShopEnabled():
                cart = getTotalPurchaseInfo(self.__purchaseItems)
                totalPriceGold = cart.totalPrice.price.get(Currency.GOLD, 0)
                showBuyGoldForCustomization(totalPriceGold)
            return
        if self.__moneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            if self.__isStyle:
                item = self.__purchaseItems[0].item
                meta = ExchangeCreditsSingleItemMeta(item.intCD)
            else:
                itemsCDs = [ purchaseItem.item.intCD for purchaseItem in self.__purchaseItems ]
                meta = ExchangeCreditsMultiItemsMeta(itemsCDs, CartInfoItem())
            yield DialogsInterface.showDialog(meta)
            return
        if containsVehicleBound(self.__purchaseItems):
            DialogsInterface.showI18nConfirmDialog(CUSTOMIZATION_DIALOGS.CUSTOMIZATION_INSTALL_BOUND_BASKET_NOTIFICATION, self.onBuyConfirmed)
            return
        self.onBuyConfirmed(True)

    def onBuyConfirmed(self, isOk):
        if isOk:
            self.__ctx.applyItems(self.__purchaseItems)
            self.close()

    def onWindowClose(self):
        self.close()

    def close(self):
        if self.__prolongStyleRent:
            self.__c11nView.onCloseWindow(force=True)
        else:
            self.__c11nView.changeVisible(True)
            self.destroy()

    def _populate(self):
        super(PurchaseWindow, self)._populate()
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
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
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

    def __getCamoBonus(self, item):
        vehicle = g_currentVehicle.item
        bonusSeparator = '&nbsp;&nbsp;'
        if item and item.bonus:
            bonus = item.bonus.getFormattedValue(vehicle)
            return bonusSeparator + text_styles.bonusAppliedText(_ms(VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_BONUSCAMO, bonus=bonus))

    def __setTitlesData(self):
        haveAutoprolongation = False
        autoprolongationSelected = False
        seasonTitlesText = {season:_ms(_CUSTOMIZATION_SEASON_TITLES[season]) for season in SeasonType.COMMON_SEASONS}
        seasonCountersText = {season:'' for season in SeasonType.COMMON_SEASONS}
        seasonCountersSmallText = {season:'' for season in SeasonType.COMMON_SEASONS}
        seasonBonusText = {season:'' for season in SeasonType.COMMON_SEASONS}
        if self.__isStyle:
            item = self.__purchaseItems[0].item
            titleTemplate = _ms(TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_STYLE_HEADER, group=item.userType, value=item.userName)
            bigTitleTemplate = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_MULTILINE, group=item.userType, value=text_styles.heroTitle(item.userName))
            for season in SeasonType.COMMON_SEASONS:
                outfit = item.getOutfit(season)
                if outfit:
                    container = outfit.hull
                    camo = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItem()
                    seasonBonusText[season] = self.__getCamoBonus(camo)

            if item.isRentable:
                haveAutoprolongation = True
                autoprolongationSelected = self.__ctx.autoRentEnabled()
        else:
            totalCount = 0
            for season in SeasonType.COMMON_SEASONS:
                purchase, inventory = self.__counters[season]
                count = purchase + inventory
                totalCount += count
                seasonCountersText[season] = (text_styles.unavailable(' ({})') if count == 0 else ' ({})').format(count)
                seasonCountersSmallText[season] = (text_styles.critical(' ({})') if count == 0 else ' ({})').format(count)

        titleTemplate = backport.text(R.strings.vehicle_customization.customization.buyWindow.title())
        bigTitleTemplate = text_styles.grandTitle(titleTemplate)
        for item in self.__purchaseItems:
            if item.areaID == Area.HULL and item.item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE and item.selected:
                seasonBonusText[item.item.season] = self.__getCamoBonus(item.item)

        titleText = text_styles.promoTitle(bigTitleTemplate)
        titleTextSmall = text_styles.promoTitle(titleTemplate)
        self.as_setInitDataS({'windowTitle': VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_HEADER,
         'isStyle': self.__isStyle,
         'titleText': titleText,
         'titleTextSmall': titleTextSmall,
         'haveAutoprolongation': haveAutoprolongation,
         'autoprolongationSelected': autoprolongationSelected,
         'prolongStyleRent': self.__prolongStyleRent})
        titles = self.__getSeasonTitle(seasonTitlesText, seasonCountersText, seasonBonusText)
        titlesSmall = self.__getSeasonTitle(seasonTitlesText, seasonCountersSmallText, seasonBonusText)
        self.as_setTitlesS({'summerTitle': text_styles.highTitle(titles[SeasonType.SUMMER]),
         'winterTitle': text_styles.highTitle(titles[SeasonType.WINTER]),
         'desertTitle': text_styles.highTitle(titles[SeasonType.DESERT]),
         'summerSmallTitle': text_styles.middleTitle(titlesSmall[SeasonType.SUMMER]),
         'winterSmallTitle': text_styles.middleTitle(titlesSmall[SeasonType.WINTER]),
         'desertSmallTitle': text_styles.middleTitle(titlesSmall[SeasonType.DESERT])})

    def __getSeasonTitle(self, text, count, bonus):
        return {season:text[season] + count[season] + bonus[season] for season in SeasonType.COMMON_SEASONS}

    def __setTotalData(self, *_):
        cart = getTotalPurchaseInfo(self.__purchaseItems)
        totalPriceVO = getItemPricesVO(cart.totalPrice)
        state = g_currentVehicle.getViewState()
        inFormationAlert = ''
        if not state.isCustomizationEnabled():
            inFormationAlert = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_FORMATION_ALERT))
        price = cart.totalPrice.price
        money = self.itemsCache.items.stats.money
        shortage = money.getShortage(price)
        self.__moneyState = getPurchaseMoneyState(price)
        inGameShopOn = Currency.GOLD in shortage.getCurrency() and isIngameShopEnabled()
        validTransaction = isTransactionValid(self.__moneyState, price)
        rentalInfoText = ''
        if self.__isStyle:
            item = self.__purchaseItems[0].item
            if item.isRentable:
                rentCount = item.rentCount
                rentalInfoText = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CAROUSEL_RENTALBATTLES, battlesNum=rentCount))
        self.as_setTotalDataS({'totalLabel': text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_TOTALCOST, selected=cart.numSelected, total=cart.numApplying)),
         'enoughMoney': validTransaction,
         'inFormationAlert': inFormationAlert,
         'totalPrice': totalPriceVO[0],
         'prolongationCondition': rentalInfoText})
        self.__setBuyButtonState(validTransaction, inGameShopOn)

    def __setBuyButtonState(self, validTransaction, inGameShopOn):
        purchase = 1 if self.__isStyle else 0
        purchase += sum([ self.__counters[season][0] for season in SeasonType.COMMON_SEASONS ])
        inventory = sum([ self.__counters[season][1] for season in SeasonType.COMMON_SEASONS ])
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY
        if purchase > 0:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY
        else:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNAPPLY
        isAnySelected = purchase + inventory > 0
        if not isAnySelected:
            label = ''
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTSELECTEDITEMS
        self.as_setBuyBtnStateS(validTransaction and isAnySelected, label, tooltip, inGameShopOn)

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            self.destroy()

    def updateAutoProlongation(self):
        self.__ctx.changeAutoRent()

    def onAutoProlongationCheckboxAdded(self):
        if self.__prolongStyleRent:
            event_dispatcher.runSalesChain(_CUSTOMIZATION_TUTORIAL_CHAPTER)


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

    def __init__(self, item, purchaseIdx=0, quantity=1, component=None):
        self.intCD = item.intCD
        self.identificator = self.intCD
        self.itemData = self._buildCustomizationItemData(item, component)
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
    def _buildCustomizationItemData(item, component=None):
        if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
            showUnsupportedAlert = not isRendererPipelineDeferred()
        else:
            showUnsupportedAlert = False
        customIcon = None
        if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and component:
            customIcon = item.numberIcon(component.number)
        return buildCustomizationItemDataVO(item, None, True, False, True, showUnsupportedAlert=showUnsupportedAlert, addExtraName=False, customIcon=customIcon)


class _StubItemPurchaseDescription(_BasePurchaseDescription):
    __slots__ = ('isFromInventory',)
    _StubItem = namedtuple('_StubItem', ('intCD',))

    def __init__(self):
        super(_StubItemPurchaseDescription, self).__init__(self._StubItem(-1), quantity=0)
        self.isFromInventory = False

    def getVO(self):
        itemVO = super(_StubItemPurchaseDescription, self).getVO()
        itemVO.update({'itemImg': self.itemData,
         'isLock': True,
         'tooltip': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM})
        return itemVO

    @staticmethod
    def _buildCustomizationItemData(item, component=None):
        itemData = {'intCD': 0,
         'isPlaceHolder': True}
        return itemData


class _SeparateItemPurchaseDescription(_BasePurchaseDescription):
    __slots__ = ('intCD', 'identificator', 'selected', 'itemData', 'compoundPrice', 'quantity', 'isFromInventory', 'purchaseIndices')

    def __init__(self, purchaseItem, purchaseIdx):
        super(_SeparateItemPurchaseDescription, self).__init__(purchaseItem.item, purchaseIdx, component=purchaseItem.component)
        self.identificator = self.__generateID(purchaseItem)
        self.selected = purchaseItem.selected
        self.compoundPrice = purchaseItem.price
        self.isFromInventory = purchaseItem.isFromInventory

    def getVO(self):
        itemVO = super(_SeparateItemPurchaseDescription, self).getVO()
        itemVO.update({'compoundPrice': getItemPricesVO(self.compoundPrice)[0],
         'isFromStorage': self.isFromInventory,
         'selected': self.selected,
         'tooltip': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE})
        return itemVO

    def __generateID(self, item):
        return hash((self.intCD, item.group, item.isFromInventory))


class _StyleItemPurchaseDescription(_BasePurchaseDescription):

    def getVO(self):
        itemVO = super(_StyleItemPurchaseDescription, self).getVO()
        itemVO.update({'isFromStorage': False,
         'isLock': True,
         'tooltip': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON})
        return itemVO


class _SeasonPurchaseInfo(object):
    _ORDERED_KEYS = (GUI_ITEM_TYPE.ATTACHMENT,
     GUI_ITEM_TYPE.SEQUENCE,
     GUI_ITEM_TYPE.PROJECTION_DECAL,
     GUI_ITEM_TYPE.INSCRIPTION,
     GUI_ITEM_TYPE.PERSONAL_NUMBER,
     GUI_ITEM_TYPE.MODIFICATION,
     GUI_ITEM_TYPE.PAINT,
     GUI_ITEM_TYPE.CAMOUFLAGE,
     GUI_ITEM_TYPE.EMBLEM,
     GUI_ITEM_TYPE.STYLE)

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
            bucket.sort(key=self.__keyFunc)
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
        return (not item.isFromInventory, item.intCD)


class _StyleItemsProcessor(_ItemsProcessor):

    def _preProcess(self, items):
        return items[0]

    def _process(self, style):
        itemsInfo = {}
        for season in SeasonType.COMMON_SEASONS:
            showStyleInsteadItems = True
            outfit = style.item.getOutfit(season)
            seasonInfo = itemsInfo.setdefault(season, _SeasonPurchaseInfo())
            for item in outfit.items():
                if not item.isHiddenInUI():
                    showStyleInsteadItems = False
                    itemDescription = _StyleItemPurchaseDescription(item)
                    seasonInfo.add(itemDescription, item.itemTypeID)

            if showStyleInsteadItems:
                styleDescription = _StyleItemPurchaseDescription(style.item)
                seasonInfo.add(styleDescription, GUI_ITEM_TYPE.STYLE)

        return itemsInfo
