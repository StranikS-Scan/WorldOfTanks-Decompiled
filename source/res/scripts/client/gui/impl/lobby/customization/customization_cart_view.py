# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_cart_view.py
from collections import namedtuple
import logging
import GUI
from frameworks.wulf import ViewFlags, ViewSettings
from adisp import process
from CurrentVehicle import g_currentVehicle
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.customization.cart_model import CartModel
from gui.impl.gen.view_models.views.lobby.customization.cart_slot_model import CartSlotModel
from gui.impl.gen.view_models.views.lobby.customization.cart_season_model import CartSeasonModel
from gui.ingame_shop import showBuyGoldForCustomization
from gui.customization.processors.cart import SeparateItemsProcessor, StyleItemsProcessor
from gui.customization.processors.cart import ProcessorSelector, ItemsType
from gui.customization.shared import SEASON_TYPE_TO_NAME, SEASONS_ORDER, MoneyForPurchase, getTotalPurchaseInfo
from gui.customization.shared import containsVehicleBound, getPurchaseMoneyState, isTransactionValid
from gui.customization.shared import CartExchangeCreditsInfoItem
from gui.Scaleform.genConsts.CUSTOMIZATION_DIALOGS import CUSTOMIZATION_DIALOGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsMultiItemsMeta
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.money import Currency
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import SeasonType
from helpers import dependency, uniprof
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from tutorial.hints_manager import HINT_SHOWN_STATUS
_logger = logging.getLogger(__name__)
_SelectItemData = namedtuple('_SelectItemData', ('season',
 'quantity',
 'purchaseIndices',
 'idx',
 'intCD'))

class CustomizationCartView(ViewImpl):
    __slots__ = ('__c11nView', '__ctx', '__purchaseItems', '__isStyle', '__counters', '__items', '__blur', '__moneyState', '__isProlongStyleRent')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CartModel()
        super(CustomizationCartView, self).__init__(settings)
        self.__ctx = None
        self.__purchaseItems = []
        self.__isStyle = False
        self.__items = {}
        self.__counters = {season:[0, 0] for season in SeasonType.COMMON_SEASONS}
        self.__moneyState = MoneyForPurchase.NOT_ENOUGH
        self.__blur = GUI.WGUIBackgroundBlur()
        if ctx is not None:
            self.__c11nView = ctx.get('c11nView', None)
            self.__isProlongStyleRent = ctx.get('prolongStyleRent', False)
        else:
            self.__c11nView = None
            self.__isProlongStyleRent = False
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            itemID = event.getArgument('id')
            if itemID in self.__items:
                intCD = self.__items[itemID].intCD
            else:
                _logger.error('Invalid itemID is received: %r', itemID)
                return None
            window = BackportTooltipWindow(self.__getTooltpData(intCD, event.getArgument('tooltip'), event.getArgument('showInventoryBlock')), self.getParentWindow())
            window.load()
            return window
        else:
            return super(CustomizationCartView, self).createToolTip(event)

    @property
    def viewModel(self):
        return super(CustomizationCartView, self).getViewModel()

    @uniprof.regionDecorator(label='customization_cart.loading', scope='enter')
    def _onLoading(self):
        super(CustomizationCartView, self)._onLoading()
        self.__ctx = self.__service.getCtx()
        purchaseItems = self.__ctx.getPurchaseItems()
        processorSelector = ProcessorSelector(_getProcessorsMap())
        result = processorSelector.process(purchaseItems)
        if result is None:
            _logger.error("Can't process purchase items")
            return
        else:
            self.__purchaseItems = result.items
            self.__isStyle = result.itemsType == ItemsType.STYLE
            itemDescriptors = result.descriptors
            autoRentHintStatus = self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.CUSTOMIZATION_AUTOPROLONGATION_HINT)
            autoRentHintShown = autoRentHintStatus is not None and autoRentHintStatus == HINT_SHOWN_STATUS
            for season in SeasonType.COMMON_SEASONS:
                for idx, item in enumerate(itemDescriptors[season]):
                    self.__items[item.identificator] = _SelectItemData(season, item.quantity, item.purchaseIndices, idx, item.intCD)
                    if not self.__isStyle:
                        self.__counters[season][int(item.isFromInventory)] += item.quantity

            with self.getViewModel().transaction() as model:
                model.setIsStyle(self.__isStyle)
                model.setIsProlongStyleRent(self.__isProlongStyleRent)
                if self.__isProlongStyleRent or not autoRentHintShown:
                    model.setShowProlongHint(True)
                if self.__isStyle:
                    item = self.__purchaseItems[0].item
                    model.setStyleTypeName(item.userType)
                    model.setStyleName(item.userName)
                    if item.isRentable:
                        model.setHasAutoRent(True)
                        model.setIsAutoRentSelected(self.__ctx.autoRentEnabled())
                seasons = model.seasons
                for seasonType in SEASONS_ORDER:
                    seasonName = SEASON_TYPE_TO_NAME.get(seasonType)
                    seasonModel = CartSeasonModel()
                    seasonModel.setName(seasonName)
                    if not self.__isStyle:
                        purchase, inventory = self.__counters[seasonType]
                        count = purchase + inventory
                        seasonModel.setCount(count)
                    self.__fillItemsListModel(seasonModel.items, itemDescriptors[seasonType])
                    seasons.addViewModel(seasonModel)

                seasons.invalidate()
                self.__setBonuses(seasons.getItems())
                self.__setTotalData(model)
            return

    @uniprof.regionDecorator(label='customization_cart.loading', scope='exit')
    def _onLoaded(self, *args, **kwargs):
        self.__blur.enable = True

    def _initialize(self, *args, **kwargs):
        super(CustomizationCartView, self)._initialize(*args, **kwargs)
        if self.__c11nView is not None:
            self.__c11nView.changeVisible(False)
        self.__addListeners()
        return

    def _finalize(self):
        super(CustomizationCartView, self)._finalize()
        self.__removeListeners()
        if self.__c11nView is not None:
            if self.__isProlongStyleRent:
                self.__c11nView.onCloseWindow(force=True)
            else:
                self.__c11nView.changeVisible(True)
            self.__c11nView = None
        self.__blur.enable = False
        self.__ctx = None
        self.__items.clear()
        del self.__purchaseItems[:]
        self.__counters.clear()
        return

    def __updateMoney(self, *_):
        with self.getViewModel().transaction() as model:
            self.__setTotalData(model)

    def __setTotalData(self, model):
        cart = getTotalPurchaseInfo(self.__purchaseItems)
        price = cart.totalPrice.price
        self.__moneyState = getPurchaseMoneyState(price)
        validTransaction = isTransactionValid(self.__moneyState, price)
        money = self.__itemsCache.items.stats.money
        shortage = money.getShortage(price)
        inGameShopOn = Currency.GOLD in shortage.getCurrency() and isIngameShopEnabled()
        purchasedCnt = 1 if self.__isStyle else 0
        purchasedCnt += sum([ self.__counters[season][0] for season in SeasonType.COMMON_SEASONS ])
        inventoryCnt = sum([ self.__counters[season][1] for season in SeasonType.COMMON_SEASONS ])
        isAnySelected = purchasedCnt + inventoryCnt > 0
        if self.__isStyle:
            item = self.__purchaseItems[0].item
            model.setIsRentable(item.isRentable)
            if item.isRentable:
                model.setRentCount(item.rentCount)
        model.totalPrice.assign(cart.totalPrice)
        model.setIsEnoughMoney(validTransaction)
        model.setIsShopEnabled(inGameShopOn)
        model.setPurchasedCount(purchasedCnt)
        model.setIsAnySelected(isAnySelected)

    def __addListeners(self):
        model = self.viewModel
        model.onSelectItem += self.__onSelectItem
        model.onSelectAutoRent += self.__onSelectAutoRent
        model.onBuyAction += self.__onBuy
        model.onTutorialClose += self.__onTutorialClose
        g_clientUpdateManager.addMoneyCallback(self.__updateMoney)
        g_currentVehicle.onChanged += self.__onVehicleChanged

    def __removeListeners(self):
        model = self.viewModel
        model.onSelectItem -= self.__onSelectItem
        model.onSelectAutoRent -= self.__onSelectAutoRent
        model.onBuyAction -= self.__onBuy
        model.onTutorialClose -= self.__onTutorialClose
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onVehicleChanged

    def __onSelectItem(self, args=None):
        itemId = args.get('id')
        selected = args.get('selected')
        fromStorage = args.get('isFromStorage')
        itemData = self.__items[itemId]
        season = itemData.season
        self.__counters[season][int(fromStorage)] += itemData.quantity if selected else -itemData.quantity
        for idx in itemData.purchaseIndices:
            self.__purchaseItems[idx].selected = selected

        seasonInd = SEASONS_ORDER.index(season)
        with self.getViewModel().transaction() as model:
            self.__setTotalData(model)
            seasonModel = model.seasons.getItem(seasonInd)
            purchase, inventory = self.__counters[season]
            seasonModel.setCount(purchase + inventory)
            itemModel = seasonModel.items.getItem(itemData.idx)
            itemModel.setSelected(selected)
            self.__setBonuses(model.seasons.getItems())

    def __getTooltpData(self, intCD, tooltip, showInventoryBlock):
        return createTooltipData(isSpecial=True, specialAlias=tooltip, specialArgs=(intCD, showInventoryBlock))

    @process
    def __onBuy(self):
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
            DialogsInterface.showI18nConfirmDialog(CUSTOMIZATION_DIALOGS.CUSTOMIZATION_INSTALL_BOUND_BASKET_NOTIFICATION, self.__onBuyConfirmed)
            return
        self.__onBuyConfirmed(True)

    def __onTutorialClose(self):
        self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.CUSTOMIZATION_AUTOPROLONGATION_HINT: HINT_SHOWN_STATUS})

    def __onBuyConfirmed(self, isOk):
        if isOk:
            self.__ctx.applyItems(self.__purchaseItems)
            self.destroyWindow()

    def __onSelectAutoRent(self, _=None):
        self.__ctx.changeAutoRent()
        self.viewModel.setIsAutoRentSelected(self.__ctx.autoRentEnabled())

    def __setBonuses(self, seasonsModelItems):
        seasonsMap = dict(((season.getName(), season) for season in seasonsModelItems))
        if self.__isStyle:
            item = self.__purchaseItems[0].item
            for season in SeasonType.COMMON_SEASONS:
                outfit = item.getOutfit(season)
                if outfit:
                    container = outfit.hull
                    camouflage = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItem()
                    seasonModel = seasonsMap[SEASON_TYPE_TO_NAME.get(season)]
                    bonusValue = self.__getCamoBonusValue(camouflage)
                    seasonModel.setBonusValue(bonusValue)
                    seasonModel.setBonusType(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE] if bonusValue else '')

        else:
            for item in self.__purchaseItems:
                if item.areaID == Area.HULL and item.item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE and item.group in SEASON_TYPE_TO_NAME:
                    seasonModel = seasonsMap[SEASON_TYPE_TO_NAME.get(item.group)]
                    bonusValue = self.__getCamoBonusValue(item.item) if item.selected else ''
                    seasonModel.setBonusValue(bonusValue)
                    seasonModel.setBonusType(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE] if bonusValue else '')

    @staticmethod
    def __fillItemsListModel(listModel, items):
        listModel.reserve(len(items))
        for item in items:
            listModel.addViewModel(item.getUIData())

        listModel.invalidate()

    def __getCamoBonusValue(self, item):
        if item and item.bonus:
            vehicle = g_currentVehicle.item
            return item.bonus.getFormattedValue(vehicle)

    def __onVehicleChanged(self):
        self.__isProlongStyleRent = False
        self.destroyWindow()


class _BaseUIDataPacker(object):

    def __call__(self, desc):
        model = CartSlotModel()
        model.setQuantity(desc.quantity)
        model.setId(desc.identificator)
        return model


class _ItemUIDataPacker(_BaseUIDataPacker):

    def __call__(self, desc):
        model = super(_ItemUIDataPacker, self).__call__(desc)
        item = desc.item
        component = desc.component
        model.setIsWide(item.isWide())
        model.setIsDim(item.isDim())
        model.setIsHistorical(item.isHistorical())
        model.price.assign(item.getBuyPrice())
        if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            model.setFormFactor(item.formfactor)
        if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and component:
            model.setIcon(item.numberIconUrl(component.number))
        else:
            model.setIcon(item.iconUrl)
        if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
            model.setShowUnsupportedAlert(not isRendererPipelineDeferred())
        else:
            model.setShowUnsupportedAlert(False)
        isSpecial = item.isVehicleBound and (item.buyCount > 0 or item.inventoryCount > 0) or item.isLimited and item.buyCount > 0
        model.setIsSpecial(isSpecial)
        return model


class _StubUIDataPacker(_BaseUIDataPacker):

    def __call__(self, desc):
        model = super(_StubUIDataPacker, self).__call__(desc)
        model.setLocked(True)
        model.setIsFromStorage(False)
        model.setTooltipId(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM)
        return model


class _SeparateUIDataPacker(_ItemUIDataPacker):

    def __call__(self, desc):
        model = super(_SeparateUIDataPacker, self).__call__(desc)
        model.setSelected(desc.selected)
        model.setTooltipId(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)
        model.setIsFromStorage(desc.isFromInventory)
        return model


class _StyleUIDataPacker(_ItemUIDataPacker):

    def __call__(self, desc):
        model = super(_StyleUIDataPacker, self).__call__(desc)
        model.setLocked(True)
        model.setTooltipId(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON)
        model.setIsFromStorage(False)
        return model


def _getProcessorsMap():
    return {ItemsType.DEFAULT: SeparateItemsProcessor(_SeparateUIDataPacker(), _StubUIDataPacker()),
     ItemsType.STYLE: StyleItemsProcessor(_StyleUIDataPacker(), _StubUIDataPacker())}
