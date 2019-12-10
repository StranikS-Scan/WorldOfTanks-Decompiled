# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/purchase_window.py
from collections import namedtuple
import logging
import GUI
from adisp import process
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui import DialogsInterface
from gui.customization.processors.cart import SeparateItemsProcessor, StyleItemsProcessor
from gui.customization.processors.cart import ProcessorSelector, ItemsType
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta, ExchangeCreditsMultiItemsMeta
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
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
from gui.customization.shared import MoneyForPurchase, getTotalPurchaseInfo, containsVehicleBound
from gui.customization.shared import getPurchaseMoneyState, isTransactionValid, CartExchangeCreditsInfoItem
_logger = logging.getLogger(__name__)
_CUSTOMIZATION_SEASON_TITLES = {SeasonType.WINTER: backport.text(R.strings.vehicle_customization.buyWindow.title.winter()),
 SeasonType.SUMMER: backport.text(R.strings.vehicle_customization.buyWindow.title.summer()),
 SeasonType.DESERT: backport.text(R.strings.vehicle_customization.buyWindow.title.desert())}
_CUSTOMIZATION_TUTORIAL_CHAPTER = 'c11nProlong'
_SelectItemData = namedtuple('_SelectItemData', ('season', 'quantity', 'purchaseIndices'))

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
                meta = ExchangeCreditsMultiItemsMeta(itemsCDs, CartExchangeCreditsInfoItem())
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
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.__c11nView = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB).getView()
        self.__ctx = self.service.getCtx()
        purchaseItems = self.__ctx.getPurchaseItems()
        g_clientUpdateManager.addMoneyCallback(self.__setTotalData)
        processorSelector = ProcessorSelector(_getProcessorsMap())
        result = processorSelector.process(purchaseItems)
        if result is None:
            _logger.error("Can't process purchase items")
            return
        else:
            self.__purchaseItems = result.items
            self.__isStyle = result.itemsType == ItemsType.STYLE
            itemDescriptors = result.descriptors
            if not self.__isStyle:
                for season in SeasonType.COMMON_SEASONS:
                    for item in itemDescriptors[season]:
                        self.__items[item.identificator] = _SelectItemData(season, item.quantity, item.purchaseIndices)
                        self.__counters[season][int(item.isFromInventory)] += item.quantity

            self.as_setDataS({'summerData': [ item.getUIData() for item in itemDescriptors[SeasonType.SUMMER] ],
             'winterData': [ item.getUIData() for item in itemDescriptors[SeasonType.WINTER] ],
             'desertData': [ item.getUIData() for item in itemDescriptors[SeasonType.DESERT] ]})
            self.__setTitlesData()
            self.__setTotalData()
            self.__blur.enable = True
            self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
            return

    def _dispose(self):
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
        self.service.resumeHighlighter()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_currentVehicle.onChanged -= self.__onVehicleChanged
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
            return bonusSeparator + text_styles.bonusAppliedText(_ms(VEHICLE_CUSTOMIZATION.BUYWINDOW_TITLE_BONUS_CAMOUFLAGE, bonus=bonus))

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
                seasonBonusText[item.group] = self.__getCamoBonus(item.item)

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
        self.__setBuyButtonState(validTransaction, inGameShopOn, cart.numBought, cart.numSelected)

    def __setBuyButtonState(self, validTransaction, inGameShopOn, boughtNumber, selectedNumber):
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY
        if boughtNumber > 0:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNBUY
        else:
            label = VEHICLE_CUSTOMIZATION.WINDOW_PURCHASE_BTNAPPLY
        isAnySelected = selectedNumber > 0
        if not isAnySelected:
            label = ''
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTSELECTEDITEMS
        self.as_setBuyBtnStateS(validTransaction and isAnySelected, label, tooltip, inGameShopOn)

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            self.destroy()

    def __onVehicleChanged(self):
        self.__prolongStyleRent = False
        self.close()

    def updateAutoProlongation(self):
        self.__ctx.changeAutoRent()

    def onAutoProlongationCheckboxAdded(self):
        if self.__prolongStyleRent:
            event_dispatcher.runSalesChain(_CUSTOMIZATION_TUTORIAL_CHAPTER)


class _BaseUIDataPacker(object):

    def __call__(self, desc):
        itemData = self._buildCustomizationItemData(desc.item, desc.component)
        return {'id': desc.identificator,
         'itemImg': itemData,
         'quantity': desc.quantity}

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


class _StubUIDataPacker(_BaseUIDataPacker):

    def __call__(self, desc):
        itemVO = super(_StubUIDataPacker, self).__call__(desc)
        itemVO.update({'isLock': True,
         'tooltip': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM})
        return itemVO

    @staticmethod
    def _buildCustomizationItemData(item, component=None):
        return {'intCD': 0,
         'isPlaceHolder': True}


class _SeparateUIDataPacker(_BaseUIDataPacker):

    def __call__(self, desc):
        itemVO = super(_SeparateUIDataPacker, self).__call__(desc)
        itemVO.update({'compoundPrice': getItemPricesVO(desc.compoundPrice)[0],
         'isFromStorage': desc.isFromInventory,
         'selected': desc.selected,
         'tooltip': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE})
        return itemVO


class _StyleUIDataPacker(_BaseUIDataPacker):

    def __call__(self, desc):
        itemVO = super(_StyleUIDataPacker, self).__call__(desc)
        itemVO.update({'isFromStorage': False,
         'isLock': True,
         'tooltip': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON})
        return itemVO


def _getProcessorsMap():
    return {ItemsType.DEFAULT: SeparateItemsProcessor(_SeparateUIDataPacker(), _StubUIDataPacker()),
     ItemsType.STYLE: StyleItemsProcessor(_StyleUIDataPacker(), _StubUIDataPacker())}
