# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_bin/customization_bin_subview.py
import logging
from collections import defaultdict
from typing import Optional, Iterable
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from adisp import adisp_process
from constants import NC_MESSAGE_PRIORITY
from frameworks.wulf import ViewSettings
from gui import DialogsInterface, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsMultiItemsMeta, ExchangeCreditsSingleItemMeta
from gui.Scaleform.genConsts.SEASONS_CONSTANTS import SEASONS_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.SystemMessages import CURRENCY_TO_SM_TYPE, SM_TYPE
from gui.customization.constants import CustomizationModes, CustomizationModeSource
from gui.customization.processors.cart import ItemsType, ProcessorSelector
from gui.customization.shared import MoneyForPurchase, SEASONS_BIN_VIEW_ORDER, SEASONS_ORDER, SEASON_TYPE_TO_NAME, containsVehicleBound, getPurchaseMoneyState, getTotalPurchaseInfo, C11nId, SEASON_NAME_TO_TYPE
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.views.lobby.customization.cart_season_model import CartSeasonModel
from gui.impl.gen.view_models.views.lobby.customization.customization_bin_subview_model import CustomizationBinSubviewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.customization.customization_bill_data_packer import processBillDataPurchaseItems, isVehicleEmpty
from gui.impl.lobby.customization.customization_bin.bin_helpers import CartExchangeCreditsInfoItem, SelectItemData, getProcessorsMap
from gui.impl.lobby.customization.shared import ITEM_TYPE_TO_SLOT_TYPE
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import tryToShowReplaceExistingStyleDialog
from gui.shared.formatters import formatPrice, formatPurchaseItems
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.money import Currency
from gui.shop import showBuyGoldForCustomization
from helpers import dependency, int2roman
from items.components.c11n_constants import SeasonType
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from th_async import th_async, th_await
from tutorial.hints_manager import HINT_SHOWN_STATUS
from vehicle_outfit.outfit import Area
_logger = logging.getLogger(__name__)

class CustomizationBinSubview(ViewImpl):
    __slots__ = ('__c11nView', '__ctx', '__purchaseItems', '__mode', '__counters', '__items', '__moneyState', '__slotIds', '__uninstalledItems')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, ctx=None):
        settings = ViewSettings(R.views.lobby.customization.CustomizationBinSubview())
        settings.model = CustomizationBinSubviewModel()
        self.__ctx = None
        self.__purchaseItems = []
        self.__mode = ItemsType.DEFAULT
        self.__items = {}
        self.__uninstalledItems = {}
        self.__slotIds = defaultdict(list)
        self.__counters = {season:[0, 0] for season in SeasonType.COMMON_SEASONS}
        self.__moneyState = MoneyForPurchase.NOT_ENOUGH
        if ctx is not None:
            self.__c11nView = ctx.get('c11nView', None)
        else:
            self.__c11nView = None
        super(CustomizationBinSubview, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CustomizationBinSubview, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltip')
            if tooltipId == TOOLTIPS_CONSTANTS.PRICE_DISCOUNT:
                args = (event.getArgument('price'), event.getArgument('defPrice'), event.getArgument('currencyType'))
            else:
                itemID = int(event.getArgument('itemID'))
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
            return super(CustomizationBinSubview, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(CustomizationBinSubview, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def __addListeners(self):
        self.__ctx.events.onItemsBought += self.__onItemsBought
        self.__ctx.events.onSeasonChanged += self.__onSeasonChanged

    def _onLoading(self):
        super(CustomizationBinSubview, self)._onLoading()
        self.__ctx = self.__service.getCtx()

    def _finalize(self):
        super(CustomizationBinSubview, self)._finalize()
        self.__removeListeners()
        self.__ctx = None
        del self.__purchaseItems[:]
        self.__items.clear()
        self.__counters.clear()
        self.__slotIds.clear()
        return

    def __removeListeners(self):
        self.__ctx.events.onItemsBought -= self.__onItemsBought
        self.__ctx.events.onSeasonChanged -= self.__onSeasonChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _getEvents(self):
        return ((self.viewModel.onCloseAction, self.__onWindowClose), (self.viewModel.onTutorialClose, self.__onTutorialClose), (self.viewModel.onSelectItem, self.__onSelectItem))

    def __onSeasonChanged(self, seasonType):
        self.viewModel.setSelectedSeason(SEASON_TYPE_TO_NAME[seasonType])

    @replaceNoneKwargsModel
    def updateModel(self, model=None, updatePurchaseItems=True):
        if updatePurchaseItems:
            purchaseItems = self.__ctx.mode.getPurchaseItems()
            purchaseItems = processBillDataPurchaseItems(self.__ctx, purchaseItems)
        else:
            purchaseItems = self.__purchaseItems
        if not purchaseItems:
            seasons = model.getSeasons()
            seasons.clear()
            seasons.invalidate()
            return
        else:
            processorSelector = ProcessorSelector(getProcessorsMap())
            result = processorSelector.process(purchaseItems)
            if result is None:
                _logger.error("Can't process purchase items")
                return
            self.__purchaseItems = result.items
            self.__mode = result.itemsType
            itemDescriptors = result.descriptors
            self.__filterAndUpdateItemDescriptors(itemDescriptors)
            self.__setItemsNCounters(itemDescriptors)
            self.__setItemsData(model, itemDescriptors)
            self.__onSeasonChanged(self.__ctx.season)
            return

    def __onWindowClose(self):
        parentView = self.getParentView()
        if parentView:
            parentView.updateIsBinSubViewActive(False)
            self.__ctx.c11nCameraManager.moveToCustomizationCamera()

    def __filterAndUpdateItemDescriptors(self, itemDescriptors):
        itemDescriptors[SeasonType.ALL] = []
        if self.__ctx.mode.modeId in CustomizationModes.ALL_STYLES:
            itemCDsForAllSeasons = set((item.intCD for item in itemDescriptors[SeasonType.SUMMER]))
            itemDescriptors[SeasonType.ALL] = []
            for seasonType in (SeasonType.WINTER, SeasonType.DESERT):
                seasonItemCDs = set((item.intCD for item in itemDescriptors[seasonType] if item.item.itemTypeID == GUI_ITEM_TYPE.STYLE))
                itemCDsForAllSeasons = itemCDsForAllSeasons & seasonItemCDs

            itemDescriptors[SeasonType.ALL] = [ item for item in itemDescriptors[SeasonType.SUMMER] if item.intCD in itemCDsForAllSeasons ]
            for seasonType in SEASONS_ORDER:
                itemDescriptors[seasonType] = [ item for item in itemDescriptors[seasonType] if item.intCD not in itemCDsForAllSeasons ]

    def __processItemBySeason(self, selected, itemID, intCD, season, component):
        if season == SEASONS_CONSTANTS.ALL and self.__ctx.mode.modeId in CustomizationModes.ALL_STYLES:
            item = self.__service.getItemByCD(intCD)
            isStyle = item.itemTypeID == GUI_ITEM_TYPE.STYLE
            if isStyle and self.__ctx.mode.modeId == CustomizationModes.EDITABLE_STYLE:
                self.__ctx.changeMode(self.__ctx.prevModeId)
            self.__processStyle(selected, intCD)
            if isStyle and item.isEditable:
                if selected:
                    self.__ctx.editStyle(intCD, source=CustomizationModeSource.CAROUSEL)
            self.updateModel(updatePurchaseItems=False)
        else:
            self.__processItem(selected, itemID, intCD, season, component)

    def __processItem(self, selected, itemID, intCD, season, component):
        season = SEASON_NAME_TO_TYPE[season]
        for slotId in self.__slotIds[itemID]:
            if selected:
                self.__ctx.mode.installItem(intCD, slotId, season, component)
            self.__ctx.mode.removeItem(slotId, season)

    def __processStyle(self, selected, intCD):
        if selected:
            styleSlot = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
            self.__ctx.mode.installItem(intCD, styleSlot)
        else:
            self.__ctx.mode.removeStyle(intCD)

    @args2params(int, bool, str)
    def __onSelectItem(self, itemID, selected, season):
        self.__slotIds.clear()
        itemData = self.__items[itemID]
        itemIntCD = itemData.intCD
        self.__refreshPurchaseItems(itemData.purchaseIndices, selected)
        self.__refreshStrictlyDependantItems(itemData, selected)
        if self.__ctx.mode.modeId not in CustomizationModes.STYLED:
            self.updateModel(updatePurchaseItems=False)
        self.__setSlotIds(itemID, itemData.purchaseIndices)
        self.__processItemBySeason(selected, itemID, itemIntCD, season, itemData.component)
        if season != SEASONS_CONSTANTS.ALL:
            seasonType = SEASON_NAME_TO_TYPE[season]
            if self.__ctx.season != seasonType:
                self.__ctx.changeSeason(seasonType)

    def __setSlotIds(self, itemID, indices):
        for idx in indices:
            pItem = self.__purchaseItems[idx]
            slotType = ITEM_TYPE_TO_SLOT_TYPE[pItem.item.itemTypeID]
            slotId = C11nId(pItem.areaID, slotType, pItem.regionIdx)
            if slotId not in self.__slotIds.get(itemID, []):
                self.__slotIds[itemID].append(slotId)

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

    def __refreshStrictlyDependantItems(self, targetItemData, selected):
        dependants = targetItemData.dependents
        targetSeason = targetItemData.season
        if dependants:
            for itemData in self.__items.values():
                if itemData.season == targetSeason and itemData.intCD in dependants:
                    self.__refreshPurchaseItems(itemData.purchaseIndices, selected)

        elif targetItemData.dependentOn:
            if selected:
                for itemData in self.__items.values():
                    if itemData.season == targetSeason and itemData.intCD == targetItemData.dependentOn:
                        self.__refreshPurchaseItems(itemData.purchaseIndices, selected)
                        break

    def __getSeasonModel(self, seasonType, seasons):
        if seasonType not in SEASON_TYPE_TO_NAME:
            _logger.error('Season type is not valid: %d', seasonType)
            return None
        else:
            name = SEASON_TYPE_TO_NAME[seasonType]
            for season in seasons:
                if season.getName() == name:
                    return season

            _logger.error('CartSeasonsModel does not have field %s', name)
            return None

    def __setItemsNCounters(self, itemDescriptors):
        self.__items = {}
        self.__counters = {season:[0, 0] for season in SeasonType.REGULAR}
        for season in SeasonType.REGULAR:
            for idx, item in enumerate(itemDescriptors[season]):
                self.__items[item.identificator] = SelectItemData(season, item.quantity, item.purchaseIndices, idx, item.intCD, item.dependents, item.dependentOn, item.component)
                if self.__mode == ItemsType.DEFAULT:
                    self.__counters[season][int(item.isFromInventory)] += item.quantity * item.selected

    def __setItemsData(self, model, itemDescriptors):
        seasons = model.getSeasons()
        seasons.clear()
        for seasonType in SEASONS_BIN_VIEW_ORDER:
            seasonModel = CartSeasonModel()
            if seasonModel is not None:
                seasonModel.setName(SEASON_TYPE_TO_NAME[seasonType])
                seasonModel.items.clearItems()
                if self.__mode == ItemsType.DEFAULT:
                    purchase, inventory = self.__counters[seasonType]
                    count = purchase + inventory
                    seasonModel.setCount(count)
                self.__fillItemsListModel(seasonModel.items, itemDescriptors[seasonType])
                seasons.addViewModel(seasonModel)

        seasons.invalidate()
        self.__setBonuses(seasons)
        return

    def __setBonuses(self, seasons):
        if self.__mode in (ItemsType.STYLE, ItemsType.EDITABLE_STYLE):
            item = first((pitem.item for pitem in self.__purchaseItems if pitem.item.itemTypeID == GUI_ITEM_TYPE.STYLE))
            vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            outfit = item.getOutfit(SeasonType.SUMMER, vehicleCD=vehicleCD)
            if outfit:
                container = outfit.hull
                camoIntCD = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
                camouflage = self.__service.getItemByCD(camoIntCD) if camoIntCD else None
                seasonModel = self.__getSeasonModel(SeasonType.ALL, seasons)
                if seasonModel is not None:
                    bonusValue = self.__getCamoBonusValue(camouflage)
                    seasonModel.setBonusValue(bonusValue)
                    seasonModel.setBonusType(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE] if bonusValue else '')
        else:
            for item in self.__purchaseItems:
                if item.areaID == Area.HULL and item.item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE and item.group in SEASON_TYPE_TO_NAME:
                    seasonModel = self.__getSeasonModel(item.group, seasons)
                    if seasonModel is not None:
                        bonusValue = self.__getCamoBonusValue(item.item) if item.selected else ''
                        seasonModel.setBonusValue(bonusValue)
                        seasonModel.setBonusType(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE] if bonusValue else '')

        return

    def __getCamoBonusValue(self, item):
        if item and item.bonus:
            vehicle = g_currentVehicle.item
            return item.bonus.getFormattedValue(vehicle)

    @th_async
    def processBuy(self):
        cart = getTotalPurchaseInfo(self.__purchaseItems)
        price = cart.totalPrice.price
        self.__moneyState = getPurchaseMoneyState(price)
        positive = yield th_await(tryToShowReplaceExistingStyleDialog(self))
        if not positive:
            return
        isWalletAvailable = self.__wallet.isAvailable
        if isWalletAvailable and self.__moneyState is MoneyForPurchase.NOT_ENOUGH:
            cart = getTotalPurchaseInfo(self.__purchaseItems)
            totalPriceGold = cart.totalPrice.price.get(Currency.GOLD, 0)
            showBuyGoldForCustomization(totalPriceGold)
            return
        if isWalletAvailable and self.__moneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            self.__showExchangeDialog()
            return
        if containsVehicleBound(self.__purchaseItems):
            builder = ResSimpleDialogBuilder()
            builder.setPreset(DialogPresets.CUSTOMIZATION_INSTALL_BOUND)
            builder.setMessagesAndButtons(R.strings.dialogs.customization.buy_install_bound)
            isOk = yield th_await(dialogs.showSimple(builder.build(self)))
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
            yield self.__c11nView.applyItems(self.__purchaseItems, force=True)
            self.destroyWindow()

    def __fillItemsListModel(self, listModel, items):
        listModel.reserve(len(items))
        isStyledMode = self.__ctx.mode.modeId in CustomizationModes.STYLED
        for item in items:
            itemModel = item.getUIData()
            if isStyledMode:
                itemModel.setIsDisabled(item.item.itemTypeID != GUI_ITEM_TYPE.STYLE)
                purchaseItems = self.__ctx.mode.getPurchaseItems()
                itemModel.setIsSelected(itemModel.getIsSelected() and bool(purchaseItems))
            listModel.addViewModel(itemModel)

        listModel.invalidate()

    def __onItemsBought(self, originalOutfits, purchaseItems, results, isAutoRentChanged=False):
        if results:
            if not self.__checkPurchaseSuccess(results):
                _logger.error('Failed to purchase customization outfits.')
                return
            cart = getTotalPurchaseInfo(purchaseItems)
            if cart.totalPrice != ITEM_PRICE_EMPTY and not isVehicleEmpty():
                currency = cart.totalPrice.getCurrency(byWeight=True)
                msgText = self.__getPurchaseMessage(cart, purchaseItems)
                msgType = CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.PurchaseForGold)
                priority = NC_MESSAGE_PRIORITY.DEFAULT if currency != Currency.CREDITS else None
            else:
                modifiedOutfits = self.__ctx.mode.getModifiedOutfits()
                msgText = self.__getModifyMessage(originalOutfits, modifiedOutfits, isAutoRentChanged)
                msgType = SM_TYPE.Information
                priority = None
            if msgText is not None:
                SystemMessages.pushMessage(text=msgText, type=msgType, priority=priority)
        return

    def __checkPurchaseSuccess(self, results):
        success = True
        for result in results:
            success &= result.success
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

        return success

    def __getPurchaseMessage(self, cart, purchaseItems):
        msgKey = R.strings.messenger.serviceChannelMessages.sysMsg.customization
        money = formatPrice(cart.totalPrice.price, useStyle=True)
        if cart.boughtCount == 1:
            pItem = findFirst(lambda i: not i.isFromInventory and i.selected, purchaseItems)
            if pItem is None:
                _logger.error('Failed to construct customization purchase system message. Missing purchase item.')
                return
            item = pItem.item
            isStyle = item.itemTypeID == GUI_ITEM_TYPE.STYLE
            if isStyle and item.isProgression:
                msgKey = msgKey.buyProgressionStyle()
                msgCtx = {'name': item.userName,
                 'level': int2roman(self.__ctx.mode.getStyleProgressionLevel()),
                 'money': money}
            else:
                msgKey = msgKey.buyOne()
                itemTypeName = backport.text(R.strings.item_types.customization.style()) if isStyle else item.userType
                msgCtx = {'itemType': itemTypeName,
                 'itemName': item.userName,
                 'money': money}
        else:
            msgKey = msgKey.buyMany()
            msgCtx = {'items': formatPurchaseItems(purchaseItems),
             'money': money}
        return backport.text(msgKey, **msgCtx)

    def __getModifyMessage(self, originalOutfits, modifiedOutfits, isAutoRentChanged):
        forwardDiffs = False
        backwardDiffs = False
        for season in SeasonType.COMMON_SEASONS:
            originalOutfit = originalOutfits[season]
            modifiedOutfit = modifiedOutfits[season]
            forwardDiffs |= not originalOutfit.diff(modifiedOutfit).isEmpty()
            backwardDiffs |= not modifiedOutfit.diff(originalOutfit).isEmpty()

        originalProgression = originalOutfits[SeasonType.SUMMER].progressionLevel
        modifiedProgression = modifiedOutfits[SeasonType.SUMMER].progressionLevel
        isStyleProgressionLevelChanged = originalProgression != modifiedProgression
        hasModifications = forwardDiffs or isStyleProgressionLevelChanged
        hasRemovalsOnly = not hasModifications and backwardDiffs
        msgKey = R.strings.messenger.serviceChannelMessages.sysMsg.customization
        if hasModifications:
            msgText = backport.text(msgKey.change())
        elif hasRemovalsOnly:
            msgText = backport.text(msgKey.remove())
        elif isAutoRentChanged:
            msgText = None
        else:
            _logger.error('Failed to construct customization purchase system message. Missing outfits diff.')
            msgText = None
        return msgText
