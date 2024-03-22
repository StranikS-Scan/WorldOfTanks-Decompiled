# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/buy_vehicle_view.py
import logging
from collections import namedtuple
from functools import partial
from typing import TYPE_CHECKING
import BigWorld
import Settings
import adisp
import constants
from CurrentVehicle import g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, ViewEvent
from gui import SystemMessages
from gui.DialogsInterface import showI18nConfirmDialog
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel, CurrencyType, CurrencySize
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_option_model import BuyVehicleOptionModel, OptionState
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_view_model import BuyVehicleViewModel
from gui.impl.gen_utils import INVALID_RES_ID
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import event_dispatcher, events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent, VehicleBuyEvent, OpenLinkEvent
from gui.shared.formatters.text_styles import neutral
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY, ItemPrice, ITEM_PRICE_ZERO
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter, VehicleTradeInProcessor, VehicleRestoreProcessor, showVehicleReceivedResultMessages
from gui.shared.money import Currency, Money, ZERO_MONEY
from gui.shared.utils import decorators
from gui.shared.utils.vehicle_collector_helper import getCollectibleVehiclesInInventory
from gui.shop import showBuyGoldForVehicleWebOverlay, showTradeOffOverlay
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from rent_common import parseRentID
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IRentalsController, ITradeInController, IRestoreController, IWalletController, ISoundEventChecker
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from uilogging.shop.loggers import ShopBuyVehicleMetricsLogger
from uilogging.shop.logging_constants import ShopLogItemStates
if TYPE_CHECKING:
    from typing import Optional, List
    from gui.shared.money import CURRENCY_TYPE
    from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_price_model import BuyVehiclePriceModel
_logger = logging.getLogger(__name__)

def getItemPriceCurrencies(itemPrice):
    result = []
    if itemPrice.price.credits > 0:
        result.append(Currency.CREDITS)
    if itemPrice.price.gold > 0:
        result.append(Currency.GOLD)
    return result


class VehicleBuyActionTypes(CONST_CONTAINER):
    DEFAULT = 0
    BUY = 1
    RESTORE = 2
    RENT = 3


class VehicleOptions(CONST_CONTAINER):
    AMMO = 'ammo'
    SLOT = 'slot'
    CREW = 'crew'
    __FOR_SAVE = (CREW,)
    __ORDER = (AMMO, SLOT, CREW)
    __SECTION_KEY = Settings.KEY_BUY_VEHICLE_VIEW_PREFERENCES

    def __init__(self, defaultKeys=()):
        self.__ensureDataSectionExists()
        self.__defaultKeys = defaultKeys
        self.read()

    def __contains__(self, value):
        return value in {k for k in self.ALL() if getattr(self, k)}

    def __getitem__(self, idx):
        return getattr(self, self.ALL()[idx])

    def write(self, key, value):
        setattr(self, self._prepareValue(key), value)
        self.save()

    def toggle(self, value):
        value = self._prepareValue(value)
        setattr(self, value, not getattr(self, value))
        self.save()

    def read(self):
        ds = self.getDataSection()
        for key in self.ALL():
            default = key in self.__defaultKeys
            setattr(self, key, ds.readBool(key, default) if key in self.__FOR_SAVE else default)

    def save(self):
        ds = self.getDataSection()
        for key in self.__FOR_SAVE:
            ds.writeBool(key, getattr(self, key))

    def getDataSection(self):
        return Settings.g_instance.userPrefs[self.__SECTION_KEY]

    def _prepareValue(self, value):
        if isinstance(value, int):
            value = self.__ORDER[value]
        elif not isinstance(value, str):
            raise SoftException('Value must be int or str')
        elif value not in self.ALL():
            raise SoftException('Value must be in {}'.format(self.ALL()))
        return value

    def __ensureDataSectionExists(self):
        up = Settings.g_instance.userPrefs
        if not up.has_key(self.__SECTION_KEY):
            up.write(self.__SECTION_KEY, '')


_TooltipExtraData = namedtuple('_TooltipExtraData', 'key, itemType')
_RentPopoverData = namedtuple('_RentPopoverData', ('vehicleIntCD', 'selectedRentTerm'))
_TradeInPopoverData = namedtuple('_TradeInPopoverData', ('confirmGoldPrice', 'tradeOffVehicleIntCD'))
_VP_SHOW_PREVIOUS_SCREEN_ON_SUCCESS_ALIASES = (VIEW_ALIAS.VEHICLE_PREVIEW, VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, VIEW_ALIAS.LOBBY_STORE)
_COLLECTIBLE_VEHICLE_TUTORIAL = 'collectibleVehicle'

class BuyVehicleView(ViewImpl, EventSystemEntity, IPrbListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rentals = dependency.descriptor(IRentalsController)
    __tradeIn = dependency.descriptor(ITradeInController)
    __wallet = dependency.descriptor(IWalletController)
    __restore = dependency.descriptor(IRestoreController)
    __soundEventChecker = dependency.descriptor(ISoundEventChecker)
    __CREW_NOT_SELECTED_IDX = -1
    __slots__ = ('__moneyBalanceWidget', '__shop', '__stats', '__nationID', '__inNationID', '__previousAlias', '__actionType', '__returnAlias', '__returnCallback', '__selectedCardIdx', '__vehicle', '__uiMetricsLogger', '__tradeInVehicleToSell', '__selectedRentID', '__selectedRentIdx', '__isGoldAutoPurchaseEnabled', '__tradeInInProgress', '__purchaseInProgress', '__usePreviousAlias', '__tradeInProgress', '__selectedOptions', '__crewPrice', '__hasFreePremiumCrew', '__tooltipPriceData', '__confirmGoldPrice')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.hangar.BuyVehicleView(), flags=ViewFlags.VIEW, model=BuyVehicleViewModel(), args=args, kwargs=kwargs)
        super(BuyVehicleView, self).__init__(settings, *args, **kwargs)
        self.__shop = self.__itemsCache.items.shop
        self.__stats = self.__itemsCache.items.stats
        ctx = kwargs.get('ctx') or {}
        self.__nationID = ctx.get('nationID')
        self.__inNationID = ctx.get('itemID')
        self.__previousAlias = ctx.get('previousAlias')
        self.__actionType = ctx.get('actionType', VehicleBuyActionTypes.DEFAULT)
        self.__returnAlias = ctx.get('returnAlias')
        self.__returnCallback = ctx.get('returnCallback')
        self.__selectedCardIdx = 0
        self.__vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        self.__uiMetricsLogger = ShopBuyVehicleMetricsLogger(str(self.__vehicle.intCD))
        self.__tradeInVehicleToSell = self.__tradeIn.getSelectedVehicleToSell()
        isRestore = self.__vehicle.isRestoreAvailable()
        if self.__vehicle.hasRentPackages and (not isRestore or self.__actionType == VehicleBuyActionTypes.RENT) and (self.__actionType != VehicleBuyActionTypes.BUY or self.__vehicle.isDisabledForBuy):
            self.__selectedRentIdx = 0
            self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
        elif isRestore:
            self.__selectedRentID = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
            self.__selectedRentIdx = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
        else:
            self.__selectedRentID = BuyVehicleViewModel.BUYING_RENT_IDX
            self.__selectedRentIdx = BuyVehicleViewModel.BUYING_RENT_IDX
        self.__isGoldAutoPurchaseEnabled = self.__wallet.isAvailable
        self.__confirmGoldPrice = 0
        self.__tradeInInProgress = False
        self.__hasFreePremiumCrew = False
        self.__purchaseInProgress = False
        self.__usePreviousAlias = False
        self.__tradeInProgress = False
        self.__selectedOptions = VehicleOptions(defaultKeys=(VehicleOptions.CREW,))
        self.__crewPrice = ITEM_PRICE_ZERO
        self.__moneyBalanceWidget = MoneyBalance(layoutID=R.views.dialogs.widgets.MoneyBalance())
        self.__tooltipPriceData = {}

    @property
    def viewModel(self):
        return super(BuyVehicleView, self).getViewModel()

    @property
    def isWithSlot(self):
        return VehicleOptions.SLOT in self.__selectedOptions

    @property
    def isWithAmmo(self):
        return VehicleOptions.AMMO in self.__selectedOptions

    @property
    def isWithCrew(self):
        return VehicleOptions.CREW in self.__selectedOptions

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            return window
        else:
            return super(BuyVehicleView, self).createToolTip(event)

    def createPopOverContent(self, event):
        alias = event.getArgument('alias')
        args = None
        if alias == BuyVehicleViewModel.RENTAL_TERM_SELECTION_POPOVER:
            args = _RentPopoverData(self.__vehicle.intCD, self.__selectedRentID)
        elif alias == BuyVehicleViewModel.VEHICLE_SELL_CONFIRMATION_POPOVER and self.__tradeInVehicleToSell:
            args = _TradeInPopoverData(self.__confirmGoldPrice, self.__tradeInVehicleToSell.intCD)
        return BackportPopOverContent(createPopOverData(alias, args))

    def _finalize(self):
        self.__uiMetricsLogger.reset()
        super(BuyVehicleView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(BuyVehicleView, self)._onLoading(*args, **kwargs)
        self.setChildView(self.__moneyBalanceWidget.layoutID, self.__moneyBalanceWidget)
        self.__updateFreePremiumCrew()
        with self.viewModel.transaction() as vm:
            fillVehicleModel(vm.vehicle, self.__vehicle, (VEHICLE_TAGS.PREMIUM,))
            if self.__tradeInVehicleToSell:
                fillVehicleModel(vm.tradeInVehicleToSell, self.__tradeInVehicleToSell)
            else:
                vm.tradeInVehicleToSell.setVehicleCD(BuyVehicleViewModel.VEHICLE_NOT_SELECTED_CD)
            vm.setIsRestore(self.__isRestore)
            vm.setHasDisclaimer(self.__vehicle.hasDisclaimer())
            self.__fillInfo()

    def _onLoaded(self, *args, **kwargs):
        super(BuyVehicleView, self)._onLoaded(*args, **kwargs)
        if self.__returnAlias == VIEW_ALIAS.LOBBY_STORE:
            self.__uiMetricsLogger.onViewOpen()

    def _getEvents(self):
        return ((self.viewModel.onOptionClick, self.__onOptionClick),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.viewModel.onCloseBtnClick, self.__onWindowClose),
         (self.viewModel.onBuyBtnClick, self.__onBuyBtnClick),
         (self.viewModel.onBackClick, self.__onWindowClose),
         (self.viewModel.onDisclaimerClick, self.__onDisclaimerClick),
         (self.viewModel.onSelectTradeInVehicleToSell, self.__onSelectTradeInVehicleToSell),
         (self.viewModel.onClearTradeInVehicleToSell, self.__onClearTradeInVehicleToSell),
         (self.__restore.onRestoreChangeNotify, self.__onRestoreChange),
         (self.__itemsCache.onSyncCompleted, self.__onItemCacheSyncCompleted),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def _getListeners(self):
        return ((ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY), (ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY), (VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeInVehicleToSellSelected, EVENT_BUS_SCOPE.DEFAULT))

    def __onItemCacheSyncCompleted(self, *_):
        if self.__purchaseInProgress or self.viewModel is None or self.viewModel.proxy is None:
            return
        else:
            self.__vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
            self.__shop = self.__itemsCache.items.shop
            self.__stats = self.__itemsCache.items.stats
            if self.__isRestore:
                self.__selectedRentIdx = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
                self.__selectedRentID = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
            elif self.__vehicle.hasRentPackages and self.__vehicle.rentPackages:
                self.__selectedRentIdx = 0
                self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
            else:
                self.__selectedRentIdx = BuyVehicleViewModel.BUYING_RENT_IDX
                self.__selectedRentID = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
            with self.viewModel.transaction():
                self.__fillInfo()
            return

    @adisp.adisp_process
    def __showVehicleInHangar(self, *_):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.__startTutorial()
        self.__destroyWindow()
        g_eventBus.handleEvent(events.CloseWindowEvent(events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, isAgree=True))
        if self.prbEntity.getQueueType() == QUEUE_TYPE.MAPS_TRAINING:
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    def __onBuyBtnClick(self):
        self.__uiMetricsLogger.clearItemStates()
        totalPrice = self.__getTotalItemPrice().price
        if self.__returnAlias == VIEW_ALIAS.LOBBY_STORE:
            self.__uiMetricsLogger.logVehiclePurchaseButtonClicked()
        if self.__isAvailablePrice(totalPrice):
            availableGold = self.__stats.money.gold
            requiredGold = totalPrice.gold
            if availableGold < requiredGold:
                showBuyGoldForVehicleWebOverlay(requiredGold, self.__vehicle.intCD, self.getParentWindow())
                return
        self.__requestForMoneyObtain()

    def __onSelectTradeInVehicleToSell(self, _=None):
        if self.__vehicle is not None:
            self.__tradeIn.selectVehicleToBuy(self.__vehicle.intCD)
        showTradeOffOverlay(self.getParentWindow())
        return

    def __onWalletStatusChanged(self, *_):
        self.__isGoldAutoPurchaseEnabled &= self.__wallet.isAvailable
        with self.viewModel.transaction():
            self.__fillTotalPrice()

    def __onTradeInVehicleToSellSelected(self, _=None):
        oldVeh = self.__tradeInVehicleToSell
        self.__tradeInVehicleToSell = self.__tradeIn.getSelectedVehicleToSell()
        if self.__tradeInVehicleToSell is not None:
            with self.viewModel.transaction():
                self.__fillTradeInInfo()
                self.__fillOptions()
                self.__fillTotalPrice()
        elif oldVeh is not None and not self.__tradeInProgress:
            self.__destroyWindow()
        return

    def __onClearTradeInVehicleToSell(self, _=None):
        self.__tradeInVehicleToSell = None
        self.__tradeIn.selectVehicleToSell(UNDEFINED_ITEM_CD)
        with self.viewModel.transaction():
            self.__fillTradeInInfo()
            self.__fillTotalPrice()
            self.__fillOptions()
        return

    def __onDisclaimerClick(self):
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, self.__vehicle.getDisclaimerUrl()))

    def __onTradeInConfirmed(self, *_):
        self.__requestForMoneyObtain()

    def __onRestoreChange(self, _):
        vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        if vehicle and not vehicle.isRestoreAvailable():
            self.__onWindowClose()
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.VEHICLE_RESTORE_FINISHED, vehicleName=vehicle.userName)

    def __onRentTermSelected(self, event):
        itemIdx = event.ctx
        self.__selectedRentIdx = itemIdx
        if self.__selectedRentIdx == BuyVehicleViewModel.BUYING_RENT_IDX:
            if self.__isRestore:
                self.__selectedRentIdx = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
                self.__selectedRentID = BuyVehicleViewModel.RENT_NOT_SELECTED_IDX
            else:
                self.__selectedRentID = self.__selectedRentIdx
        else:
            self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
        with self.viewModel.transaction():
            self.__fillRentInfo()
            self.__fillTotalPrice()
            self.__fillOptions()
            self.__fillTitle()

    def __onSuccess(self):
        self.__usePreviousAlias = True
        self.__processReturnCallback()
        event_dispatcher.hideVehiclePreview(back=False)
        if self.__isRenting():
            self.__onWindowClose()
        else:
            self.__showVehicleInHangar()

    def __onWindowClose(self, *_):
        self.__startTutorial()
        self.__destroyWindow()
        if self.__returnAlias == VIEW_ALIAS.LOBBY_STORE:
            self.__uiMetricsLogger.onViewClosed()
        if self.__usePreviousAlias and self.__returnCallback:
            self.__returnCallback()
        g_eventBus.handleEvent(events.CloseWindowEvent(events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, isAgree=False))

    def __destroyWindow(self):
        self.destroyWindow()

    def __processReturnCallback(self):
        returnCallback = None
        if self.__previousAlias in _VP_SHOW_PREVIOUS_SCREEN_ON_SUCCESS_ALIASES:
            if self.__returnCallback:
                returnCallback = self.__returnCallback
            elif self.__returnAlias == VIEW_ALIAS.LOBBY_RESEARCH and g_currentPreviewVehicle.isPresent():
                returnCallback = partial(event_dispatcher.showResearchView, g_currentPreviewVehicle.item.intCD, exitEvent=events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': g_currentPreviewVehicle.item.nationName}))
            elif self.__returnAlias == VIEW_ALIAS.LOBBY_STORE:
                returnCallback = partial(event_dispatcher.showShop)
            else:
                event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(self.__returnAlias), {'isBackEvent': True})
                returnCallback = partial(g_eventBus.handleEvent, event, scope=EVENT_BUS_SCOPE.LOBBY)
        elif self.__usePreviousAlias and self.__previousAlias is None and self.__returnAlias == VIEW_ALIAS.LOBBY_STORE and self.__returnCallback:
            returnCallback = self.__returnCallback
        self.__returnCallback = returnCallback
        return

    @decorators.adisp_process('buyItem')
    def __requestForMoneyObtain(self):
        try:
            self.__soundEventChecker.lockPlayingSounds()
            self.__tradeInProgress = True
            yield self.__requestForMoneyObtainImpl()
        finally:
            self.__soundEventChecker.unlockPlayingSounds()
            self.__tradeInProgress = False

    @adisp.adisp_async
    @adisp.adisp_process
    def __requestForMoneyObtainImpl(self, callback):
        isTradeIn = self.__isTradeIn and self.__tradeInVehicleToSell is not None and not self.__isRentVisible
        crewType = self.__selectedCardIdx if self.isWithCrew else self.__CREW_NOT_SELECTED_IDX
        result = None
        self.__purchaseInProgress = True
        processor, vehicle = (None, None)
        if isTradeIn:
            self.__purchaseInProgress = False
            vehicle = self.__tradeInVehicleToSell
            processor = VehicleTradeInProcessor(self.__vehicle, self.__tradeInVehicleToSell, self.isWithSlot, self.isWithAmmo, crewType)
        if processor or vehicle:
            confirmationType, ctx = self.__getTradeInCTX(vehicle)
            self.__tradeInInProgress = True
            result = yield showI18nConfirmDialog(confirmationType, meta=I18nConfirmDialogMeta(confirmationType, ctx, ctx), focusedID=DIALOG_BUTTON_ID.SUBMIT)
            if not result or self.isDisposed():
                self.__tradeInInProgress = False
                callback(result)
                return
            result = yield processor.request()
            showVehicleReceivedResultMessages(result)
            if self.isDisposed():
                callback(result)
                return
            self.__tradeInInProgress = False
            if not result.success:
                self.__onWindowClose()
                callback(result)
                return
        if self.isWithSlot:
            result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success or self.isDisposed():
                self.__purchaseInProgress = False
                callback(result)
                return
        if not isTradeIn:
            if self.__isBuying():
                if self.__isRestore:
                    result = yield self.__getRestoreVehicleProcessor(crewType).request()
                else:
                    result = yield self.__getObtainVehicleProcessor(crewType).request()
            else:
                result = yield VehicleRenter(self.__vehicle, self.__selectedRentID, self.isWithAmmo, crewType).request()
            showVehicleReceivedResultMessages(result)
            self.__purchaseInProgress = False
        if result and result.success and not self.isDisposed():
            self.__onSuccess()
        callback(result)
        return

    def __getTradeInCTX(self, vehicle):
        confirmationType = 'tradeInConfirmation'
        addition = ''
        operations = []
        if vehicle.hasCrew:
            operations.append('crew')
        if vehicle.hasShells:
            operations.append('shells')
        if vehicle.hasConsumables:
            operations.append('equipments')
        if vehicle.hasOptionalDevices:
            operations.append('optionalDevices')
        if vehicle.postProgressionAvailability(unlockOnly=True).result:
            operations.append('pairModifications')
        if operations:
            operationsStr = [ backport.text(R.strings.dialogs.tradeInConfirmation.message.dyn(o)()) for o in operations ]
            addition = backport.text(R.strings.dialogs.tradeInConfirmation.message.addition(), operations=', '.join(operationsStr))
        ctx = {'vehName': neutral(vehicle.userName),
         'addition': addition}
        return (confirmationType, ctx)

    def __fillTradeInInfo(self):
        self.__tradeInVehicleToSell = self.__tradeIn.getSelectedVehicleToSell()
        self.viewModel.setHasTradeInWidget(self.__hasTradeInWidget)
        self.viewModel.setHasTradeInVehiclesToSelect(self.__vehicle.intCD in self.__tradeIn.getVehiclesToBuy(False))
        if self.__tradeInVehicleToSell:
            fillVehicleModel(self.viewModel.tradeInVehicleToSell, self.__tradeInVehicleToSell)
        else:
            self.viewModel.tradeInVehicleToSell.setVehicleCD(BuyVehicleViewModel.VEHICLE_NOT_SELECTED_CD)

    def __fillRentInfo(self):
        textDir = R.strings.hangar.buyVehicleWindow
        label, labelKwargs = textDir.buyBtn(), {}
        if self.__selectedRentID >= 0:
            rentType, packageID = parseRentID(self.__selectedRentID)
            rentPackage = self.__vehicle.rentPackages[self.__selectedRentIdx]
            if rentType == constants.RentType.TIME_RENT:
                label = textDir.dyn('rentBtnLabel{}Days'.format(packageID))()
                if label == INVALID_RES_ID:
                    label = textDir.rentBtnLabelAny()
                    labelKwargs['days'] = packageID
            elif rentType in (constants.RentType.SEASON_RENT, constants.RentType.SEASON_CYCLE_RENT):
                seasonType = rentPackage['seasonType']
                isSeason = rentType == constants.RentType.SEASON_RENT
                seasonTextDir = textDir.rentBtnLabelSeason
                if seasonType == constants.GameSeasonType.EPIC:
                    label = seasonTextDir.epicSeason() if isSeason else seasonTextDir.epicCycle()
                if seasonType == constants.GameSeasonType.RANKED:
                    label = seasonTextDir.rankedSeason() if isSeason else seasonTextDir.rankedCycle()
        elif self.__selectedRentID == BuyVehicleViewModel.BUYING_RENT_IDX:
            label = textDir.termSlotUnlim()
        elif self.__selectedRentID == BuyVehicleViewModel.RENT_NOT_SELECTED_IDX:
            label = textDir.restore()
        self.viewModel.setRentButtonLabel(backport.text(label, **labelKwargs))
        self.viewModel.setIsRentAvailable(self.__isRentVisible)

    def __updateIsEnoughStatus(self, *_):
        if self.__vehicle.isRented:
            return
        with self.viewModel.transaction():
            self.__fillOptions()
            self.__fillTotalPrice()

    def __fillTotalPrice(self):
        totalPrice = self.__getTotalItemPrice()
        if self.__isTradeIn:
            self.__confirmGoldPrice = totalPrice.price.get(Currency.GOLD)
            popoverIsAvailable = 0 <= totalPrice.price.get(Currency.GOLD) <= self.__stats.money.get(Currency.GOLD)
            self.viewModel.setHasTradeInGoldConfirmation(popoverIsAvailable and not self.__isRentVisible)
        self.__fillPriceModel(self.viewModel.totals, totalPrice, 'totals')
        self.__updateBuyBtnData(totalPrice)

    def __updateBuyBtnData(self, totalPrice):
        totalPriceMoney = totalPrice.price
        statsMoney = self.__stats.money
        isEnabled = True
        self.viewModel.buyButtonTooltip.setTooltipId('')
        self.viewModel.buyButtonTooltip.setHeader('')
        self.viewModel.buyButtonTooltip.setBody('')
        for currency in Currency.ALL:
            if not self.__isPurchaseCurrencyAvailable(currency):
                isEnabled &= totalPriceMoney.get(currency) <= statsMoney.get(currency)

        if self.__isTradeIn and self.__tradeInVehicleToSell is not None:
            isValidTradeOff = self.__isValidTradeOffSelected() and self.__tradeInVehicleToSell.isReadyToTradeOff
            if not isValidTradeOff:
                isEnabled = False
                self.viewModel.buyButtonTooltip.setTooltipId(BuyVehicleViewModel.TRADE_IN_STATE_NOT_AVAILABLE_TOOLTIP)
        slotIsOptional = self.__isTradeIn and self.__tradeInVehicleToSell is not None or self.__selectedRentID > 0
        if not self.__hasFreeSlots() and not self.isWithSlot and not slotIsOptional:
            isEnabled = False
            textDir = R.strings.tooltips.contentBuyView.slotCheckbox.notEnoughSlots
            self.viewModel.buyButtonTooltip.setHeader(backport.text(textDir.header()))
            self.viewModel.buyButtonTooltip.setBody(backport.text(textDir.body()))
        self.viewModel.setIsBuyButtonEnabled(isEnabled)
        self.__fillBuyButtonLabel()
        return

    def __fillBuyButtonLabel(self):
        textDir = R.strings.hangar.buyVehicleWindow
        label = textDir.buyBtn()
        if self.__isRestore and not self.__isRenting():
            label = textDir.restore()
        elif self.__hasTradeInWidget and self.__tradeInVehicleToSell:
            label = textDir.exchange()
        elif self.__isRenting():
            label = textDir.rentBtn()
        self.viewModel.setBuyButtonLabel(backport.text(label))

    def __fillTitle(self):
        textDir = R.strings.hangar.buyVehicleWindow
        label = textDir.title()
        if self.__isRenting():
            label = textDir.rent.title()
        elif self.__isRestore:
            label = textDir.title_restore()
        self.viewModel.setTitle(backport.text(label))

    def __getAmmoItemPrice(self):
        ammoPrice = ITEM_PRICE_EMPTY
        for shell in self.__vehicle.gun.defaultAmmo:
            ammoPrice += shell.buyPrices.itemPrice * shell.count

        return ammoPrice

    def __getAmmoIsAvailable(self, ammoPrice):
        return not self.__vehicle.isAmmoFull and self.__isAvailablePrice(ammoPrice)

    def __hasFreeSlots(self):
        return self.__itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0

    def __getSlotIsAvailable(self, slotPrice):
        isSlotForRent = self.__selectedRentIdx >= 0 and self.__isRentVisible
        isSlotForTradeIn = self.__isTradeIn and self.__tradeInVehicleToSell is not None and not self.__isRentVisible
        return not isSlotForRent and not isSlotForTradeIn and self.__isAvailablePrice(slotPrice)

    def __getCrewIsAvailable(self):
        return not (self.__hasFreePremiumCrew or self.__vehicle.hasCrew)

    def __getTotalItemPrice(self):
        price, defPrice = self.__getVehiclePrice()
        totals = ItemPrice(price=price, defPrice=price if defPrice is ZERO_MONEY else defPrice)
        if self.isWithCrew:
            totals += self.__crewPrice
        else:
            self.__uiMetricsLogger.addItemState(ShopLogItemStates.WITHOUT_CREW.value)
        if self.isWithSlot and not (self.__selectedRentIdx >= 0 and self.__isRentVisible):
            vehSlots = self.__stats.vehicleSlots
            totals += self.__shop.getVehicleSlotsItemPrice(vehSlots)
            self.__uiMetricsLogger.addItemState(ShopLogItemStates.WITH_SLOT.value)
        if self.isWithAmmo:
            totals += self.__getAmmoItemPrice()
            self.__uiMetricsLogger.addItemState(ShopLogItemStates.WITH_AMMO.value)
        return totals

    def __getVehiclePrice(self):
        price = defPrice = ZERO_MONEY
        if self.__isTradeIn and self.__tradeInVehicleToSell is not None and not self.__isRentVisible:
            tradeInPrice = self.__tradeIn.getTradeInPrice(self.__vehicle)
            price = tradeInPrice.price
            defPrice = tradeInPrice.defPrice
        elif self.__selectedRentIdx >= 0 and self.__isRentVisible:
            price += self.__vehicle.rentPackages[self.__selectedRentIdx]['rentPrice']
        elif self.__isRestore:
            price += self.__vehicle.restorePrice
        else:
            price += self.__vehicle.buyPrices.itemPrice.price
            defPrice += self.__vehicle.buyPrices.itemPrice.defPrice
        return (price, defPrice)

    def __getObtainVehicleProcessor(self, crewType):
        return VehicleBuyer(self.__vehicle, self.isWithSlot, self.isWithAmmo, crewType)

    def __getRestoreVehicleProcessor(self, crewType):
        return VehicleRestoreProcessor(self.__vehicle, self.isWithSlot, self.isWithAmmo, crewType)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return
        else:
            if tooltipId == BuyVehicleViewModel.TRADE_IN_STATE_NOT_AVAILABLE_TOOLTIP:
                veh = self.__tradeInVehicleToSell
                args = (veh,)
            elif tooltipId == BuyVehicleViewModel.SELECTED_VEHICLE_TRADEOFF_TOOLTIP:
                args = (self.__tradeInVehicleToSell.intCD,)
            elif tooltipId == BuyVehicleViewModel.ACTION_PRICE_TOOLTIP:
                tooltipKey = event.getArgument('tooltipKey')
                currency = event.getArgument('currency')
                if tooltipKey in self.__tooltipPriceData:
                    itemPrice = self.__tooltipPriceData[tooltipKey]
                    price = Money.makeFrom(currency, itemPrice.price.get(currency))
                    defPrice = Money.makeFrom(currency, itemPrice.defPrice.get(currency))
                    args = (None,
                     None,
                     price.toMoneyTuple(),
                     defPrice.toMoneyTuple(),
                     True,
                     False,
                     None,
                     True)
                else:
                    return
            else:
                args = None
            return createTooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=args)

    def __isAvailablePrice(self, money, reservedMoney=ZERO_MONEY):
        isPurchaseCurrencyAvailable = money.isDefined()
        statsMoney = self.__stats.money
        for currency in Currency.ALL:
            currencyValue = money.get(currency)
            if currencyValue and currencyValue > statsMoney.get(currency, 0) - reservedMoney.get(currency, 0):
                isPurchaseCurrencyAvailable &= self.__isPurchaseCurrencyAvailable(currency)

        return statsMoney - reservedMoney >= money or isPurchaseCurrencyAvailable

    def __isPurchaseCurrencyAvailable(self, currencyType):
        return currencyType == Currency.GOLD and self.__isGoldAutoPurchaseEnabled

    @property
    def __isTradeIn(self):
        return bool(self.__tradeIn.isEnabled() and self.__vehicle.canTradeIn)

    @property
    def __hasTradeInWidget(self):
        return not self.__isRentVisible and self.__isTradeIn

    @property
    def __isRentVisible(self):
        return self.__vehicle.hasRentPackages and not self.__isTradeIn

    @property
    def __isRestore(self):
        return self.__vehicle.isRestoreAvailable()

    def __isToggleRentAndTradeInState(self):
        return False if not self.__vehicle else self.__isTradeIn and self.__vehicle.hasRentPackages

    def __isValidTradeOffSelected(self):
        return self.__tradeIn.validatePossibleVehicleToBuy(self.__vehicle)

    def __isRenting(self):
        return not self.__isBuying()

    def __isBuying(self):
        buyingIndexes = (BuyVehicleViewModel.BUYING_RENT_IDX, BuyVehicleViewModel.RENT_NOT_SELECTED_IDX)
        return self.__selectedRentIdx in buyingIndexes or not self.__isRentVisible

    def __startTutorial(self):
        if not self.__vehicle.isCollectible:
            return
        collectibleVehicles = set(getCollectibleVehiclesInInventory().keys())
        if len(collectibleVehicles) == 1 and self.__vehicle.intCD in collectibleVehicles:
            event_dispatcher.runSalesChain(_COLLECTIBLE_VEHICLE_TUTORIAL)

    def __updateFreePremiumCrew(self):
        self.__hasFreePremiumCrew = BigWorld.player().freePremiumCrew.get(self.__vehicle.level, 0) > 0

    def __onClientUpdated(self, diff, *_):
        if 'freePremiumCrew' in diff:
            self.__updateFreePremiumCrew()
            with self.viewModel.transaction():
                self.__fillOptions()

    @args2params(int)
    def __onOptionClick(self, index):
        self.__selectedOptions.toggle(index)
        with self.viewModel.transaction():
            self.__fillOptions()
            self.__fillTotalPrice()

    def __fillInfo(self):
        self.__fillTradeInInfo()
        self.__fillOptions()
        self.__fillTotalPrice()
        self.__fillRentInfo()
        self.__fillTitle()

    def __fillOptions(self):
        options = self.viewModel.getOptions()
        options.clear()
        options.invalidate()
        options.addViewModel(self.__createAmmoOptionModel())
        options.addViewModel(self.__createSlotOptionModel())
        forceCrewSelected = self.__hasFreePremiumCrew and not self.__vehicle.hasCrew
        if forceCrewSelected:
            self.__selectedOptions.write(VehicleOptions.CREW, True)
        else:
            options.addViewModel(self.__createCrewOptionModel())

    def __createAmmoOptionModel(self):
        ammoPrice = self.__getAmmoItemPrice()
        isAmmoFull = self.__vehicle.isAmmoFull
        isAvailable = self.__getAmmoIsAvailable(ammoPrice.price)
        return self.__createOptionModel(VehicleOptions.AMMO, ammoPrice, R.images.gui.maps.icons.hangar.buyVehicle.ammo(), backport.text(R.strings.hangar.buyVehicleWindow.equipment.ammo()), customState=None if isAvailable else OptionState.DISABLED, tooltipBody=backport.text(R.strings.dialogs.buyVehicleWindow.fullAmmo()) if isAmmoFull else None)

    def __createSlotOptionModel(self):
        slotItemPrice = self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)
        isAvailable = self.__getSlotIsAvailable(slotItemPrice.price)
        kwargs = {'customState': None}
        if isAvailable and not self.__hasFreeSlots() and self.__tradeInVehicleToSell is None and not self.isWithSlot:
            kwargs['customState'] = OptionState.WARNING
            kwargs['tooltipHeader'] = backport.text(R.strings.tooltips.contentBuyView.slotCheckbox.notEnoughSlots.header())
            kwargs['tooltipBody'] = backport.text(R.strings.tooltips.contentBuyView.slotCheckbox.notEnoughSlots.body())
        elif not isAvailable:
            kwargs['customState'] = OptionState.DISABLED
            if self.__selectedRentIdx >= 0 and self.__isRentVisible:
                kwargs['tooltipBody'] = backport.text(R.strings.dialogs.buyVehicleWindow.freeRentSlot())
        return self.__createOptionModel(VehicleOptions.SLOT, slotItemPrice, R.images.gui.maps.icons.hangar.buyVehicle.slot(), backport.text(R.strings.hangar.buyVehicleWindow.equipment.slot()), **kwargs)

    def __createCrewOptionModel(self):
        crewSize = len(self.__vehicle.crew)
        tooltipHeader = backport.text(R.strings.hangar.buyVehicleWindow.crewTooltip.header())
        tooltipBody = backport.text(R.strings.hangar.buyVehicleWindow.crewTooltip.body(), count=crewSize)
        if self.__vehicle.hasCrew:
            tooltipHeader = None
            tooltipBody = backport.text(R.strings.hangar.buyVehicleWindow.crewInVehicle())
        return self.__createOptionModel(VehicleOptions.CREW, self.__crewPrice, R.images.gui.maps.icons.hangar.buyVehicle.crew(), backport.text(R.strings.hangar.buyVehicleWindow.recruitCrewLbl(), count=crewSize), customState=None if self.__getCrewIsAvailable() else OptionState.DISABLED, tooltipBody=tooltipBody, tooltipHeader=tooltipHeader)

    def __createOptionModel(self, index, itemPrice, icon, title, customState=None, tooltipHeader=None, tooltipBody=None, isPriceVisible=True):
        isSelected = index in self.__selectedOptions
        option = BuyVehicleOptionModel()
        option.setIcon(icon)
        option.setTitle(title)
        option.setIsPriceVisible(isPriceVisible)
        if tooltipHeader:
            option.tooltip.setHeader(tooltipHeader)
        if tooltipBody:
            option.tooltip.setBody(tooltipBody)
        self.__fillPriceModel(option.price, itemPrice, str(index))
        if customState:
            option.setOptionState(customState)
        else:
            option.setOptionState(OptionState.SELECTED if isSelected else OptionState.DEFAULT)
        if customState == OptionState.DISABLED and isSelected:
            self.__selectedOptions.write(index, False)
        return option

    def __fillPriceModel(self, priceModel, itemPrice, tooltipKey):
        self.__tooltipPriceData[tooltipKey] = itemPrice
        priceModelList = priceModel.getPrice()
        priceModelList.clear()
        priceModelList.invalidate()
        priceModel.setTooltipKey(tooltipKey)
        moneyStats = self.__stats.money
        for currency in getItemPriceCurrencies(itemPrice):
            currencyValue = int(itemPrice.price.get(currency, 0))
            isEnough = moneyStats.get(currency) >= currencyValue or self.__isPurchaseCurrencyAvailable(currency)
            priceModel = CurrencyViewModel()
            priceModel.setType(CurrencyType(currency))
            priceModel.setValue(currencyValue)
            priceModel.setSize(CurrencySize.BIG)
            hasAction = itemPrice.price.get(currency) != itemPrice.defPrice.get(currency)
            priceModel.setIsDiscount(hasAction)
            priceModel.setIsEnough(isEnough)
            priceModelList.addViewModel(priceModel)


class BuyVehicleWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, **kwargs):
        flags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(BuyVehicleWindow, self).__init__(flags, content=BuyVehicleView(**kwargs))
