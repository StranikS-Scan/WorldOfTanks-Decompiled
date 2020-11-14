# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_cart/customization_cart_view.py
from collections import namedtuple
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from adisp import process as adisp_process
from async import async, await
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import WindowFlags
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.customization.constants import CustomizationModes
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_model import CartModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_slot_model import CartSlotModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_season_model import CartSeasonModel
from gui.shop import showBuyGoldForCustomization
from gui.customization.processors.cart import SeparateItemsProcessor, StyleItemsProcessor, EditableStyleItemsProcessor
from gui.customization.processors.cart import ProcessorSelector, ItemsType
from gui.customization.shared import SEASON_TYPE_TO_NAME, SEASONS_ORDER, MoneyForPurchase, getTotalPurchaseInfo
from gui.customization.shared import containsVehicleBound, getPurchaseMoneyState, isTransactionValid
from gui.customization.shared import CartExchangeCreditsInfoItem
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsMultiItemsMeta
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.event_dispatcher import tryToShowReplaceExistingStyleDialog
from gui.shared.gui_items.customization import CustomizationTooltipContext
from shared_utils import first
from vehicle_outfit.outfit import Area
from gui.shared.money import Currency
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import SeasonType
from helpers import dependency, uniprof
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from tutorial.hints_manager import HINT_SHOWN_STATUS
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_seasons_model import CartSeasonsModel
_logger = logging.getLogger(__name__)
_SelectItemData = namedtuple('_SelectItemData', ('season',
 'quantity',
 'purchaseIndices',
 'idx',
 'intCD'))

def _getSeasonModel(seasonType, seasons):
    if seasonType not in SEASON_TYPE_TO_NAME:
        _logger.error('Season type is not valid: %d', seasonType)
        return
    else:
        name = SEASON_TYPE_TO_NAME[seasonType]
        season = getattr(seasons, name, None)
        if season is None:
            _logger.error('CartSeasonsModel does not have field %s', name)
        return season


class CustomizationCartView(ViewImpl):
    __slots__ = ('__c11nView', '__ctx', '__purchaseItems', '__mode', '__counters', '__items', '__blur', '__moneyState', '__isProlongStyleRent')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CartModel()
        super(CustomizationCartView, self).__init__(settings)
        self.__ctx = None
        self.__purchaseItems = []
        self.__mode = ItemsType.DEFAULT
        self.__items = {}
        self.__counters = {season:[0, 0] for season in SeasonType.COMMON_SEASONS}
        self.__moneyState = MoneyForPurchase.NOT_ENOUGH
        self.__blur = CachedBlur()
        if ctx is not None:
            self.__c11nView = ctx.get('c11nView', None)
            self.__isProlongStyleRent = ctx.get('prolongStyleRent', False)
        else:
            self.__c11nView = None
            self.__isProlongStyleRent = False
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltip')
            if tooltipId == TOOLTIPS_CONSTANTS.PRICE_DISCOUNT:
                args = (event.getArgument('price'), event.getArgument('defPrice'), event.getArgument('currencyType'))
            else:
                itemID = event.getArgument('id')
                if itemID in self.__items:
                    intCD = self.__items[itemID].intCD
                else:
                    _logger.error('Invalid itemID is received: %r', itemID)
                    return None
                args = CustomizationTooltipContext(itemCD=intCD, showInventoryBlock=event.getArgument('showInventoryBlock'), level=int(event.getArgument('progressionLevel')))
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
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
        purchaseItems = self.__ctx.mode.getPurchaseItems()
        processorSelector = ProcessorSelector(_getProcessorsMap())
        result = processorSelector.process(purchaseItems)
        if result is None:
            _logger.error("Can't process purchase items")
            return
        else:
            self.__purchaseItems = result.items
            self.__mode = result.itemsType
            itemDescriptors = result.descriptors
            autoRentHintStatus = self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_AUTOPROLONGATION_HINT)
            autoRentHintShown = autoRentHintStatus is not None and autoRentHintStatus == HINT_SHOWN_STATUS
            self.__setItemsNCounters(itemDescriptors)
            with self.getViewModel().transaction() as model:
                style = model.style
                isStyle = self.__mode in (ItemsType.STYLE, ItemsType.EDITABLE_STYLE)
                if self.__mode == ItemsType.EDITABLE_STYLE:
                    isEdited = any((pItem.isEdited for pItem in purchaseItems))
                    style.setIsEditable(isEdited)
                style.setIsStyle(isStyle)
                style.setIsProlongStyleRent(self.__isProlongStyleRent)
                if self.__isProlongStyleRent or not autoRentHintShown:
                    model.tutorial.setShowProlongHint(True)
                if isStyle:
                    item = self.__purchaseItems[0].item
                    style.setStyleTypeName(item.userTypeID)
                    style.setStyleName(item.userName)
                    rent = model.rent
                    if item.isRentable:
                        rent.setHasAutoRent(True)
                        rent.setIsAutoRentSelected(self.__ctx.mode.isAutoRentEnabled())
                self.__setItemsData(model, itemDescriptors)
            return

    @uniprof.regionDecorator(label='customization_cart.loading', scope='exit')
    def _onLoaded(self, *args, **kwargs):
        self.__blur.enable()

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
                if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE and g_currentVehicle.item is not None:
                    self.__ctx.changeMode(CustomizationModes.STYLED)
                self.__c11nView.changeVisible(True)
            self.__c11nView = None
        self.__blur.fini()
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
        isAnySelected = cart.numSelected > 0
        rent = model.rent
        if self.__mode in (ItemsType.STYLE, ItemsType.EDITABLE_STYLE):
            item = self.__purchaseItems[0].item
            rent.setIsRentable(item.isRentable)
            if item.isRentable:
                rent.setRentCount(item.rentCount)
        purchase = model.purchase
        purchase.totalPrice.assign(cart.totalPrice)
        purchase.setIsEnoughMoney(validTransaction)
        purchase.setIsGoldPrice(Currency.GOLD in shortage.getCurrency())
        purchase.setPurchasedCount(cart.numBought)
        model.setIsAnySelected(isAnySelected)
        model.setIsRendererPipelineDeferred(isRendererPipelineDeferred())

    def __addListeners(self):
        model = self.viewModel
        model.onCloseAction += self.__onWindowClose
        model.seasons.onSelectItem += self.__onSelectItem
        model.rent.onSelectAutoRent += self.__onSelectAutoRent
        model.purchase.onBuyAction += self.__onBuy
        model.tutorial.onTutorialClose += self.__onTutorialClose
        g_clientUpdateManager.addMoneyCallback(self.__updateMoney)
        g_currentVehicle.onChanged += self.__onVehicleChanged

    def __removeListeners(self):
        model = self.viewModel
        model.onCloseAction += self.__onWindowClose
        model.seasons.onSelectItem -= self.__onSelectItem
        model.rent.onSelectAutoRent -= self.__onSelectAutoRent
        model.purchase.onBuyAction -= self.__onBuy
        model.tutorial.onTutorialClose -= self.__onTutorialClose
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onVehicleChanged

    def __onWindowClose(self):
        if self.__hasOpenedChildWindow():
            return
        self.destroyWindow()

    def __onSelectItem(self, args=None):
        itemId = args.get('id')
        selected = args.get('selected')
        itemData = self.__items[itemId]
        self.__refreshPurchaseItems(itemData.purchaseIndices, selected)
        with self.getViewModel().transaction() as model:
            processorSelector = ProcessorSelector(_getProcessorsMap())
            result = processorSelector.process(self.__purchaseItems)
            self.__purchaseItems = result.items
            self.__mode = result.itemsType
            itemDescriptors = result.descriptors
            self.__setItemsNCounters(itemDescriptors)
            self.__setItemsData(model, itemDescriptors)

    def __refreshPurchaseItems(self, indices, selected):
        for idx in indices:
            pItem = self.__purchaseItems[idx]
            pItem.selected = selected
            if selected != pItem.isFromInventory:
                for anotherPItem in self.__purchaseItems:
                    if anotherPItem.item.intCD == pItem.item.intCD and anotherPItem.selected != pItem.selected and anotherPItem.isFromInventory != pItem.isFromInventory:
                        pItem.isFromInventory = anotherPItem.isFromInventory
                        anotherPItem.isFromInventory = not anotherPItem.isFromInventory
                        break

    def __setItemsNCounters(self, itemDescriptors):
        self.__items = {}
        self.__counters = {season:[0, 0] for season in SeasonType.COMMON_SEASONS}
        for season in SeasonType.COMMON_SEASONS:
            for idx, item in enumerate(itemDescriptors[season]):
                self.__items[item.identificator] = _SelectItemData(season, item.quantity, item.purchaseIndices, idx, item.intCD)
                if self.__mode == ItemsType.DEFAULT:
                    self.__counters[season][int(item.isFromInventory)] += item.quantity * item.selected

    def __setItemsData(self, model, itemDescriptors):
        seasons = model.seasons
        for seasonType in SEASONS_ORDER:
            seasonModel = _getSeasonModel(seasonType, seasons)
            if seasonModel is not None:
                seasonModel.setName(SEASON_TYPE_TO_NAME[seasonType])
                seasonModel.items.clearItems()
                if self.__mode == ItemsType.DEFAULT:
                    purchase, inventory = self.__counters[seasonType]
                    count = purchase + inventory
                    seasonModel.setCount(count)
                self.__fillItemsListModel(seasonModel.items, itemDescriptors[seasonType])

        self.__setBonuses(seasons)
        self.__setTotalData(model)
        return

    @async
    def __onBuy(self):
        positive = yield await(tryToShowReplaceExistingStyleDialog(self))
        if not positive:
            return
        if self.__moneyState is MoneyForPurchase.NOT_ENOUGH:
            cart = getTotalPurchaseInfo(self.__purchaseItems)
            totalPriceGold = cart.totalPrice.price.get(Currency.GOLD, 0)
            showBuyGoldForCustomization(totalPriceGold)
            return
        if self.__moneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            self.__showExchangeDialog()
            return
        if containsVehicleBound(self.__purchaseItems):
            builder = ResSimpleDialogBuilder()
            builder.setPreset(DialogPresets.CUSTOMIZATION_INSTALL_BOUND)
            builder.setMessagesAndButtons(R.strings.dialogs.customization.buy_install_bound)
            isOk = yield await(dialogs.showSimple(builder.build(self)))
            self.__onBuyConfirmed(isOk)
            return
        self.__onBuyConfirmed(True)

    @adisp_process
    def __showExchangeDialog(self):
        if self.__mode in (ItemsType.STYLE, ItemsType.EDITABLE_STYLE):
            item = self.__purchaseItems[0].item
            meta = ExchangeCreditsSingleItemMeta(item.intCD)
        else:
            itemsCDs = [ purchaseItem.item.intCD for purchaseItem in self.__purchaseItems ]
            meta = ExchangeCreditsMultiItemsMeta(itemsCDs, CartExchangeCreditsInfoItem())
        yield DialogsInterface.showDialog(meta)

    def __onTutorialClose(self):
        self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_AUTOPROLONGATION_HINT: HINT_SHOWN_STATUS})

    @adisp_process
    def __onBuyConfirmed(self, isOk):
        if isOk:
            yield self.__ctx.applyItems(self.__purchaseItems)
            self.destroyWindow()

    def __onSelectAutoRent(self, _=None):
        self.__ctx.mode.changeAutoRent()
        self.viewModel.rent.setIsAutoRentSelected(self.__ctx.mode.isAutoRentEnabled())

    def __setBonuses(self, seasons):
        if self.__mode in (ItemsType.STYLE, ItemsType.EDITABLE_STYLE):
            item = first((pitem.item for pitem in self.__purchaseItems if pitem.item.itemTypeID == GUI_ITEM_TYPE.STYLE))
            vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            for seasonType in SeasonType.COMMON_SEASONS:
                outfit = item.getOutfit(seasonType, vehicleCD=vehicleCD)
                if outfit:
                    container = outfit.hull
                    camoIntCD = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
                    camouflage = self.__service.getItemByCD(camoIntCD) if camoIntCD else None
                    seasonModel = _getSeasonModel(seasonType, seasons)
                    if seasonModel is not None:
                        bonusValue = self.__getCamoBonusValue(camouflage)
                        seasonModel.setBonusValue(bonusValue)
                        seasonModel.setBonusType(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE] if bonusValue else '')

        else:
            for item in self.__purchaseItems:
                if item.areaID == Area.HULL and item.item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE and item.group in SEASON_TYPE_TO_NAME:
                    seasonModel = _getSeasonModel(item.group, seasons)
                    if seasonModel is not None:
                        bonusValue = self.__getCamoBonusValue(item.item) if item.selected else ''
                        seasonModel.setBonusValue(bonusValue)
                        seasonModel.setBonusType(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE] if bonusValue else '')

        return

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

    def __hasOpenedChildWindow(self):

        def predicate(window):
            isTooltip = window.windowFlags & WindowFlags.WINDOW_TYPE_MASK == WindowFlags.TOOLTIP
            return window.parent == self.getParentWindow() and not isTooltip

        return self.__guiLoader.windowsManager.findWindows(predicate)


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
        if item.isProgressive and component:
            progressionLevel = component.progressionLevel
            if progressionLevel == 0:
                progressionLevel = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            model.setIcon(item.iconUrlByProgressionLevel(progressionLevel))
            model.setProgressionLevel(progressionLevel)
        elif item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and component:
            model.setIcon(item.numberIconUrl(component.number))
        else:
            model.setIcon(item.iconUrl)
        if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
            model.setShowUnsupportedAlert(not isRendererPipelineDeferred())
        else:
            model.setShowUnsupportedAlert(False)
        isSpecial = item.isVehicleBound and (item.buyCount > 0 or item.inventoryCount > 0) and not item.isProgressionAutoBound or item.isLimited and item.buyCount > 0
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
        model.setIsStyle(True)
        model.setTooltipId(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON)
        model.setIsFromStorage(False)
        return model


class _EditableStyleItemUIDataPacker(_SeparateUIDataPacker):

    def __call__(self, desc):
        model = super(_EditableStyleItemUIDataPacker, self).__call__(desc)
        isUnremovable = desc.locked
        model.setLocked(isUnremovable)
        model.setIsStyle(isUnremovable)
        model.setIsEdited(desc.isEdited)
        model.setTooltipId(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON if desc.locked else TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)
        return model


def _getProcessorsMap():
    return {ItemsType.DEFAULT: SeparateItemsProcessor(_SeparateUIDataPacker(), _StubUIDataPacker()),
     ItemsType.STYLE: StyleItemsProcessor(_StyleUIDataPacker(), _StubUIDataPacker()),
     ItemsType.EDITABLE_STYLE: EditableStyleItemsProcessor(_EditableStyleItemUIDataPacker(), _StubUIDataPacker())}
