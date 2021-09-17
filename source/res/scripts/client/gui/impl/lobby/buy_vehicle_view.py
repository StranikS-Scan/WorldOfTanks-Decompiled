# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/buy_vehicle_view.py
import logging
from collections import namedtuple
from functools import partial
import adisp
import nations
import constants
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl import backport
from gui.impl.pub.lobby_window import LobbyWindow
from gui.veh_post_progression.models.progression import PostProgressionCompletion
from items import UNDEFINED_ITEM_CD
from rent_common import parseRentID
from gui import SystemMessages
from gui.DialogsInterface import showI18nConfirmDialog
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shop import showBuyGoldForVehicleWebOverlay, showTradeOffOverlay, showPersonalTradeOffOverlay
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORE import STORE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.impl.pub import ViewImpl
from gui.impl.backport import BackportTooltipWindow, TooltipData, getIntegralFormat
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.buy_vehicle_view_model import BuyVehicleViewModel
from gui.impl.gen.view_models.views.buy_vehicle_view.commander_slot_model import CommanderSlotModel
from gui.shared import event_dispatcher, events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent, VehicleBuyEvent, OpenLinkEvent
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.gui_items.Tankman import CrewTypes
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import ZERO_MONEY
from gui.shared.gui_items.Vehicle import getTypeUserName, getSmallIconPath, getLevelSmallIconPath, getTypeSmallIconPath
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.formatters import updateActionInViewModel
from gui.shared.formatters.tankmen import getItemPricesViewModel
from gui.shared.formatters.text_styles import neutral
from gui.shared.money import Currency, Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.utils import decorators
from gui.shared.utils.vehicle_collector_helper import getCollectibleVehiclesInInventory
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter, VehicleTradeInProcessor, VehicleRestoreProcessor, VehiclePersonalTradeInProcessor, showVehicleReceivedResultMessages
from helpers import i18n, dependency, int2roman, func_utils
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IRentalsController, ITradeInController, IRestoreController, IBootcampController, IWalletController, IPersonalTradeInController, ISoundEventChecker
from skeletons.gui.shared import IItemsCache
from frameworks.wulf import WindowFlags, ViewStatus, ViewSettings
_logger = logging.getLogger(__name__)

class VehicleBuyActionTypes(CONST_CONTAINER):
    DEFAULT = 0
    BUY = 1
    RESTORE = 2
    RENT = 3


_TooltipExtraData = namedtuple('_TooltipExtraData', 'key, itemType')
_TANKMAN_KEYS = ('', 'creditsTankman', 'goldTankman')
_ACADEMY_SLOT = 2
_VP_SHOW_PREVIOUS_SCREEN_ON_SUCCESS_ALIASES = (VIEW_ALIAS.VEHICLE_PREVIEW,
 VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW,
 VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW,
 VIEW_ALIAS.LOBBY_STORE)
_COLLECTIBLE_VEHICLE_TUTORIAL = 'collectibleVehicle'

class BuyVehicleView(ViewImpl, EventSystemEntity):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rentals = dependency.descriptor(IRentalsController)
    __tradeIn = dependency.descriptor(ITradeInController)
    __personalTradeIn = dependency.descriptor(IPersonalTradeInController)
    __wallet = dependency.descriptor(IWalletController)
    __restore = dependency.descriptor(IRestoreController)
    __bootcamp = dependency.descriptor(IBootcampController)
    __soundEventChecker = dependency.descriptor(ISoundEventChecker)
    __RENT_NOT_SELECTED_IDX = -2
    __RENT_UNLIM_IDX = -1
    __CREW_NOT_SELECTED_IDX = -1
    __TRADE_OFF_NOT_SELECTED = -1

    def __init__(self, **kwargs):
        settings = ViewSettings(R.views.lobby.shop.buy_vehicle_view.BuyVehicleView())
        settings.model = BuyVehicleViewModel()
        super(BuyVehicleView, self).__init__(settings)
        self.__shop = self.__itemsCache.items.shop
        self.__stats = self.__itemsCache.items.stats
        ctx = kwargs.get('ctx')
        if ctx is not None:
            self.__nationID = ctx.get('nationID')
            self.__inNationID = ctx.get('itemID')
            self.__previousAlias = ctx.get('previousAlias')
            self.__actionType = ctx.get('actionType')
            self.__showOnlyCongrats = ctx.get('showOnlyCongrats')
            self.__congratsViewSettings = ctx.get('congratulationsViewSettings')
            self.__returnAlias = ctx.get('returnAlias')
            self.__returnCallback = ctx.get('returnCallback')
        else:
            self.__nationID = None
            self.__inNationID = None
            self.__previousAlias = ''
            self.__actionType = VehicleBuyActionTypes.DEFAULT
            self.__showOnlyCongrats = False
            self.__congratsViewSettings = {}
            self.__returnAlias = None
            self.__returnCallback = None
        self.__selectedCardIdx = 0 if not self.__bootcamp.isInBootcamp() else _ACADEMY_SLOT
        self.__isWithoutCommander = False
        self.__vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        self.__tradeOffVehicle = self.__tradeIn.getActiveTradeOffVehicle()
        self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()
        if self.__vehicle.isRestoreAvailable():
            self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX
            self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
        else:
            self.__selectedRentID = self.__RENT_UNLIM_IDX
            self.__selectedRentIdx = self.__RENT_UNLIM_IDX
        self.__isGoldAutoPurchaseEnabled = self.__wallet.isAvailable
        self.__isRentVisible = self.__vehicle.hasRentPackages and not self.__isTradeIn() and not self.__isPersonalTradeIn()
        self.__popoverIsAvailable = True
        self.__tradeInInProgress = False
        self.__purchaseInProgress = False
        self.__usePreviousAlias = False
        return

    @property
    def viewModel(self):
        return super(BuyVehicleView, self).getViewModel()

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

    def showCongratulations(self):
        self.__usePreviousAlias = True
        self.__processReturnCallback()
        event_dispatcher.hideVehiclePreview(back=False)
        if self.__isRenting():
            self.__onWindowClose()
        else:
            self.__showCongratulationsView()

    def _initialize(self, *args, **kwargs):
        super(BuyVehicleView, self)._initialize()
        self.__addListeners()
        isElite = self.__vehicle.isElite
        vehType = self.__vehicle.type.replace('-', '_')
        isRestore = self.__vehicle.isRestoreAvailable()
        if self.__showOnlyCongrats:
            self.viewModel.setIsContentHidden(True)
        with self.viewModel.transaction() as vm:
            vm.setIsRestore(isRestore)
            vm.setBgSource(R.images.gui.maps.icons.store.shop_2_background_arsenal())
            vm.setTankType('{}_elite'.format(vehType) if isElite else vehType)
            vehicleTooltip = i18n.makeString(getTypeUserName(self.__vehicle.type, isElite))
            noCrewLabelPath = R.strings.store.buyVehicleWindow.checkBox
            vm.setVehicleNameTooltip(vehicleTooltip)
            vm.setNation(nations.NAMES[self.__vehicle.nationID])
            vm.setNoCrewCheckboxLabel(noCrewLabelPath.restore.withoutCrew() if isRestore else noCrewLabelPath.buy.withoutCrew())
            vm.setTankLvl(int2roman(self.__vehicle.level))
            vm.setTankName(self.__vehicle.shortUserName)
            vm.setNeedDisclaimer(self.__vehicle.hasDisclaimer())
            vm.setCountCrew(len(self.__vehicle.crew))
            vm.setBuyVehicleIntCD(self.__vehicle.intCD)
            vm.setIsElite(isElite)
            if self.__vehicle.hasCrew:
                vm.setWithoutCommanderAltText(R.strings.store.buyVehicleWindow.crewInVehicle())
            equipmentBlock = vm.equipmentBlock
            equipmentBlock.setIsRentVisible(self.__isRentVisible)
            equipmentBlock.setTradeInIsEnabled(self.__isTradeIn())
            equipmentBlock.setPersonalTradeInIsEnabled(self.__isPersonalTradeIn())
            emtySlotAvailable = self.__itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0
            equipmentBlock.setEmtySlotAvailable(emtySlotAvailable)
            equipmentBlock.setIsRestore(isRestore)
            if self.__vehicle.hasRentPackages and (not isRestore or self.__actionType == VehicleBuyActionTypes.RENT) and self.__actionType != VehicleBuyActionTypes.BUY:
                self.__selectedRentIdx = 0
                self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
            self.__updateCommanderCards()
            self.__updateSlotPrice()
            self.__updateAmmoPrice()
            self.__updateTradeInInfo()
            self.__updateRentInfo()
            self.__updateBuyBtnLabel()
            totalPriceArray = equipmentBlock.totalPrice.getItems()
            self.__addVMsInActionPriceList(totalPriceArray, ItemPrice(price=Money(credits=0, gold=0), defPrice=Money(credits=0, gold=0)))
            self.__updateTotalPrice()

    def _finalize(self):
        self.__removeListeners()
        super(BuyVehicleView, self)._finalize()

    def __addListeners(self):
        self.addListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffVehicleSelected)
        g_clientUpdateManager.addMoneyCallback(self.__updateIsEnoughStatus)
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onInHangarClick += self.__onInHangar
        self.viewModel.onCheckboxWithoutCrewChanged += self.__onCheckboxWithoutCrewChanged
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onCommanderLvlChange += self.__onCommanderLvlChange
        self.viewModel.onBackClick += self.__onWindowClose
        self.viewModel.onDisclaimerClick += self.__onDisclaimerClick
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onSelectTradeOffVehicle += self.__onSelectTradeOffVehicle
        equipmentBlock.onCancelTradeOffVehicle += self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange += self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange += self.__onSelectedChange
        self.__restore.onRestoreChangeNotify += self.__onRestoreChange
        self.__itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged += self.__onActiveTradeInSaleVehicleChanged

    def __removeListeners(self):
        self.removeListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffVehicleSelected)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        self.viewModel.onDisclaimerClick -= self.__onDisclaimerClick
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onInHangarClick -= self.__onInHangar
        self.viewModel.onCheckboxWithoutCrewChanged -= self.__onCheckboxWithoutCrewChanged
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onCommanderLvlChange -= self.__onCommanderLvlChange
        self.viewModel.onBackClick -= self.__onWindowClose
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onSelectTradeOffVehicle -= self.__onSelectTradeOffVehicle
        equipmentBlock.onCancelTradeOffVehicle -= self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange -= self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange -= self.__onSelectedChange
        self.__restore.onRestoreChangeNotify -= self.__onRestoreChange
        self.__itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged -= self.__onActiveTradeInSaleVehicleChanged

    def __onItemCacheSyncCompleted(self, *_):
        if self.__purchaseInProgress or self.viewModel is None or self.viewModel.proxy is None:
            return
        else:
            self.__vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
            self.__shop = self.__itemsCache.items.shop
            self.__stats = self.__itemsCache.items.stats
            if self.viewModel.getIsRestore():
                self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
                self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX
            elif self.__vehicle.hasRentPackages and self.__vehicle.rentPackages:
                self.__selectedRentIdx = 0
                self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
            else:
                self.__selectedRentIdx = self.__RENT_UNLIM_IDX
                self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX
            self.__updateCommanderCards()
            self.__updateSlotPrice()
            self.__updateAmmoPrice()
            self.__updateTradeInInfo()
            self.__updateRentInfo()
            self.__updateTotalPrice()
            return

    def __onInHangar(self, *_):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.__startTutorial()
        self.__destroyWindow()
        self.fireEvent(events.CloseWindowEvent(events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, isAgree=True))

    def __onCheckboxWithoutCrewChanged(self, args):
        self.__isWithoutCommander = args['selected']
        with self.viewModel.transaction() as vm:
            cardVMs = vm.commanderLvlCards.getItems()
            for cVm in cardVMs:
                cVm.setSlotIsEnabled(not self.__isWithoutCommander)

            if not self.__isWithoutCommander:
                self.__updateIsEnoughStatus()
        self.__updateTotalPrice()

    def __onBuyBtnClick(self):
        if self.__tradeInInProgress:
            return
        if self.viewModel.getIsContentHidden():
            self.__onInHangar()
            return
        totalPrice = self.__getTotalItemPrice().price
        if self.__isAvailablePrice(totalPrice):
            availableGold = self.__stats.money.gold
            requiredGold = totalPrice.gold
            if availableGold < requiredGold:
                showBuyGoldForVehicleWebOverlay(requiredGold, self.__vehicle.intCD, self.getParentWindow())
                return
        self.__requestForMoneyObtain()

    def __onSelectedChange(self, *_):
        self.__updateTotalPrice()

    def __onCommanderLvlChange(self, args):
        cardModels = self.viewModel.commanderLvlCards.getItems()
        cardModels[self.__selectedCardIdx].setIsSelected(False)
        self.__selectedCardIdx = int(args['value'])
        cardModels[self.__selectedCardIdx].setIsSelected(True)
        self.__updateTotalPrice()

    def __onToggleRentAndTradeIn(self):
        self.__isRentVisible = not self.__isRentVisible
        self.__updateTradeOffVehicleIntCD()
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockVm:
            tradeInVisible = not self.__isRentVisible and self.__isTradeIn() and self.__tradeOffVehicle is None
            equipmentBlockVm.vehicleTradeInBtn.setIsVisible(tradeInVisible)
            equipmentBlockVm.vehicleBtn.setVisible(tradeInVisible)
            equipmentBlockVm.vehicleRentBtn.setIsVisible(self.__isRentVisible)
            equipmentBlockVm.setIsRentVisible(self.__isRentVisible)
            if self.__isRentVisible:
                equipmentBlockVm.setPopoverIsAvailable(False)
            else:
                equipmentBlockVm.setPopoverIsAvailable(self.__popoverIsAvailable)
            self.__updateSlotPrice()
            self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        return

    def __onSelectTradeOffVehicle(self, _=None):
        if self.__isPersonalTradeIn():
            showPersonalTradeOffOverlay(parent=self.getParentWindow())
        else:
            showTradeOffOverlay(self.__vehicle.level, self.getParentWindow())

    def __onWalletStatusChanged(self, *_):
        self.__isGoldAutoPurchaseEnabled &= self.__wallet.isAvailable
        self.__updateTotalPrice()

    def __onTradeOffVehicleSelected(self, _=None):
        self.__tradeOffVehicle = self.__tradeIn.getActiveTradeOffVehicle()
        if self.__tradeOffVehicle is not None:
            self.__updateTradeInInfo()
            self.__updateSlotPrice()
            self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        return

    def __onCancelTradeOffVehicle(self, _=None):
        self.__tradeOffVehicle = None
        self.__tradeIn.setActiveTradeOffVehicleCD(UNDEFINED_ITEM_CD)
        self.__updateTradeInInfo()
        self.__updateTotalPrice()
        self.__updateSlotPrice()
        self.__updateBuyBtnLabel()
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

    def __onActiveTradeInSaleVehicleChanged(self, *_):
        self.__updateTradeInInfo()
        self.__updateTotalPrice()
        self.__updateSlotPrice()
        self.__updateBuyBtnLabel()

    def __onRentTermSelected(self, event):
        itemIdx = event.ctx
        self.__selectedRentIdx = itemIdx
        if self.__selectedRentIdx == self.__RENT_UNLIM_IDX:
            if self.viewModel.getIsRestore():
                self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
                self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX
            else:
                self.__selectedRentID = self.__selectedRentIdx
        else:
            self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
        self.viewModel.hold()
        self.__updateRentInfo()
        self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        self.__updateSlotPrice()
        self.viewModel.commit()

    def __onWindowClose(self, *_):
        self.__destroyWindow()
        if self.__usePreviousAlias and self.__returnCallback:
            self.__returnCallback()
        self.fireEvent(events.CloseWindowEvent(events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, isAgree=False))

    def __destroyWindow(self):
        self.viewModel.congratulationAnim.setResetAnimTrigger(True)
        self.destroyWindow()

    def __processReturnCallback(self):
        returnCallback = None
        if not self.__bootcamp.isInBootcamp():
            if self.__previousAlias in _VP_SHOW_PREVIOUS_SCREEN_ON_SUCCESS_ALIASES:
                if self.__returnCallback:
                    returnCallback = self.__returnCallback
                elif self.__returnAlias == VIEW_ALIAS.LOBBY_RESEARCH and g_currentPreviewVehicle.isPresent():
                    returnCallback = partial(event_dispatcher.showResearchView, g_currentPreviewVehicle.item.intCD, exitEvent=events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': g_currentPreviewVehicle.item.nationName}))
                elif self.__returnAlias == VIEW_ALIAS.LOBBY_STORE:
                    returnCallback = partial(event_dispatcher.showShop)
                else:
                    event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(self.__returnAlias), {'isBackEvent': True})
                    returnCallback = partial(self.fireEvent, event, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__returnCallback = returnCallback
        return

    def __playSlotAnimation(self):
        if self.viewStatus != ViewStatus.LOADED:
            _logger.warning('Can not show slot animation! The view is not loaded anymore.')
            return
        self.viewModel.equipmentBlock.setIsSlotAnimPlaying(True)

    def __showCongratulationsView(self):
        if self.viewStatus != ViewStatus.LOADED:
            _logger.warning('Can not show congratulations! The view is not loaded anymore.')
            return
        else:
            self.viewModel.setIsContentHidden(True)
            with self.viewModel.congratulationAnim.transaction() as vm:
                vehicleType = '{}_elite'.format(self.__vehicle.type) if self.__vehicle.isElite else self.__vehicle.type
                image = func_utils.makeFlashPath(self.__vehicle.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_LARGE))
                defaultImage = RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_LARGE, 'empty_tank')
                settings = self.__congratsViewSettings
                if settings and 'bgSource' in settings:
                    self.viewModel.setBgSource(settings['bgSource'])
                if settings and 'backBtnEnabled' in settings:
                    vm.setNeedBackBtn(settings['backBtnEnabled'])
                if settings and 'backBtnLabel' in settings:
                    vm.setBackBtnLbl(settings['backBtnLabel'])
                vm.setIsElite(self.__vehicle.isElite)
                vm.setIsCollectible(self.__vehicle.isCollectible)
                vm.setVehicleType(vehicleType)
                vm.setLvl(int2roman(self.__vehicle.level))
                vm.setVName(self.__vehicle.userName)
                vm.setImage(image if image is not None else defaultImage)
                vm.setImageAlt(defaultImage)
                vm.setTitle(R.strings.store.congratulationAnim.restoreLabel() if self.viewModel.getIsRestore() else R.strings.store.congratulationAnim.buyingLabel())
                vm.setBtnLbl(R.strings.store.congratulationAnim.showPreviewBtnLabel())
            return

    @decorators.process('buyItem')
    def __requestForMoneyObtain(self):
        try:
            self.__soundEventChecker.lockPlayingSounds()
            yield self.__requestForMoneyObtainImpl()
        finally:
            self.__soundEventChecker.unlockPlayingSounds()

    @adisp.async
    @adisp.process
    def __requestForMoneyObtainImpl(self, callback):
        equipmentBlock = self.viewModel.equipmentBlock
        isTradeIn = self.__isTradeIn() and self.__tradeOffVehicle is not None and not self.__isRentVisible
        isPersonalTradeIn = self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None and not self.__isRentVisible
        isWithSlot = equipmentBlock.slot.getIsSelected()
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        if self.__isWithoutCommander:
            crewType = self.__CREW_NOT_SELECTED_IDX
        else:
            crewType = self.__selectedCardIdx
        result = None
        self.__purchaseInProgress = False
        if isTradeIn:
            vehicle = self.__tradeOffVehicle
            processor = VehicleTradeInProcessor(self.__vehicle, self.__tradeOffVehicle, isWithSlot, isWithAmmo, crewType)
        elif isPersonalTradeIn:
            vehicle = self.__personalTradeInSaleVehicle
            processor = VehiclePersonalTradeInProcessor(self.__vehicle, self.__personalTradeInSaleVehicle, isWithSlot, isWithAmmo, crewType)
        else:
            self.__purchaseInProgress = True
            processor, vehicle = (None, None)
        if processor is not None or vehicle is not None:
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
        if isWithSlot:
            result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success or self.isDisposed():
                self.__purchaseInProgress = False
                callback(result)
                return
        if not (isTradeIn or isPersonalTradeIn):
            emptySlotAvailable = self.__itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0
            if self.__isBuying():
                if self.viewModel.getIsRestore():
                    result = yield self.__getRestoreVehicleProcessor(crewType).request()
                else:
                    result = yield self.__getObtainVehicleProcessor(crewType).request()
                if not emptySlotAvailable and not isWithSlot and not self.isDisposed():
                    self.__playSlotAnimation()
            else:
                result = yield VehicleRenter(self.__vehicle, self.__selectedRentID, isWithAmmo, crewType).request()
            showVehicleReceivedResultMessages(result)
            self.__purchaseInProgress = False
        if result and result.success and not self.isDisposed():
            self.showCongratulations()
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
        if vehicle.postProgression.getCompletion() != PostProgressionCompletion.EMPTY:
            operations.append('pairModifications')
        if operations:
            operationsStr = [ backport.text(R.strings.dialogs.tradeInConfirmation.message.dyn(o)()) for o in operations ]
            addition = backport.text(R.strings.dialogs.tradeInConfirmation.message.addition(), operations=', '.join(operationsStr))
        ctx = {'vehName': neutral(vehicle.userName),
         'addition': addition}
        return (confirmationType, ctx)

    def __updateActionPriceArray(self, priceArray, itemPrice):
        for priceModel in priceArray:
            self.__updatePriceModel(priceModel, itemPrice)

    def __updatePriceModel(self, priceModel, itemPrice):
        numberFormat = self.gui.systemLocale.getNumberFormat
        statsMoney = self.__stats.money
        price = itemPrice.price
        defPrice = itemPrice.defPrice
        currencyType = priceModel.getType()
        currencyValue = price.get(currencyType)
        if currencyValue is not None:
            priceModel.setPrice(numberFormat(currencyValue))
            priceModel.setDefPrice(numberFormat(defPrice.get(currencyType, 0)))
        else:
            for currencyType in Currency.ALL:
                currencyValue = price.get(currencyType)
                if currencyValue:
                    priceModel.setType(currencyType)
                    priceModel.setPrice(numberFormat(currencyValue))
                    break

        priceModel.setAction(itemPrice.getActionPrc())
        if self.__isPurchaseCurrencyAvailable(currencyType):
            isEnough = True
        else:
            isEnough = statsMoney.get(currencyType) >= currencyValue
        priceModel.setIsEnough(isEnough)
        hasAction = itemPrice.getActionPrcAsMoney().get(currencyType) is not None
        priceModel.setIsWithAction(hasAction)
        if hasAction:
            updateActionInViewModel(currencyType, priceModel, itemPrice)
        priceModel.setIsBootcamp(self.__bootcamp.isInBootcamp())
        return

    def __updateSlotPrice(self):
        slotItemPrice = self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)
        with self.viewModel.equipmentBlock.slot.transaction() as slotVm:
            listArray = slotVm.actionPrices.getItems()
            isAvailable = self.__getSlotIsAvailable(slotItemPrice.price)
            slotVm.setIsDisabledTooltip(self.__selectedRentIdx >= 0 and self.__isRentVisible)
            slotVm.setIsEnabled(isAvailable)
            if not isAvailable:
                slotVm.setIsSelected(False)
            isInit = len(listArray) == 0
            if isInit:
                self.__addVMsInActionPriceList(listArray, slotItemPrice, not self.__isGoldAutoPurchaseEnabled, tooltipData=_TooltipExtraData('slotsPrices', ACTION_TOOLTIPS_TYPE.ECONOMICS))
            else:
                self.__updateActionPriceArray(listArray, slotItemPrice)

    def __updateAmmoPrice(self):
        ammoItemPrice = self.__getAmmoItemPrice()
        with self.viewModel.equipmentBlock.ammo.transaction() as ammoVm:
            isAvailable = self.__getAmmoIsAvailable(ammoItemPrice.price)
            ammoVm.setIsDisabledTooltip(self.__vehicle.isAmmoFull)
            ammoVm.setIsEnabled(isAvailable)
            if not isAvailable:
                ammoVm.setIsSelected(False)
            listArray = ammoVm.actionPrices.getItems()
            isInit = len(listArray) == 0
            if isInit:
                self.__addVMsInActionPriceList(listArray, ammoItemPrice)
            else:
                self.__updateActionPriceArray(listArray, ammoItemPrice)

    def __updateCommanderCards(self):
        commanderLvlsCost = self.__shop.getTankmanCostItemPrices()
        listArray = self.viewModel.commanderLvlCards.getItems()
        isInit = len(listArray) == 0
        countLvls = len(commanderLvlsCost)
        commanderLvlPercents = CrewTypes.CREW_AVAILABLE_SKILLS
        for idx in xrange(countLvls):
            commanderItemPrice = commanderLvlsCost[idx]
            commanderItemPrice *= len(self.__vehicle.crew)
            if isInit:
                commanderLvlModel = CommanderSlotModel()
                commanderLvlModel.setIdx(idx)
                commanderLvlModel.setPercents(commanderLvlPercents[idx])
                commanderLvlModel.setTitle(i18n.makeString(STORE.BUYVEHICLEWINDOW_SLOT_ENUM[idx]))
                commanderLvlModel.setIsBootcamp(self.__bootcamp.isInBootcamp())
                if not self.__vehicle.hasCrew:
                    commanderLvlModel.setIsSelected(idx == self.__selectedCardIdx)
            else:
                commanderLvlModel = listArray[idx]
            commanderLvlModel.setDiscount(commanderItemPrice.getActionPrc())
            isFree = commanderItemPrice.price <= ZERO_MONEY and commanderItemPrice.getActionPrc() == 0
            commanderLvlModel.setIsFree(isFree)
            if self.__vehicle.hasCrew:
                isEnabled = False
            elif self.__bootcamp.isInBootcamp():
                isEnabled = idx == _ACADEMY_SLOT
            elif not isFree:
                isEnabled = self.__isAvailablePrice(commanderItemPrice.price)
            else:
                isEnabled = True
            commanderLvlModel.setSlotIsEnabled(isEnabled and not self.__isWithoutCommander)
            commanderActionPriceArray = commanderLvlModel.actionPrice.getItems()
            if isInit:
                self.__addVMsInActionPriceList(commanderActionPriceArray, commanderItemPrice, not isEnabled, tooltipData=_TooltipExtraData(_TANKMAN_KEYS[idx], ACTION_TOOLTIPS_TYPE.ECONOMICS))
                listArray.addViewModel(commanderLvlModel)
            self.__updateActionPriceArray(commanderActionPriceArray, commanderItemPrice)

    def __updateTradeInInfo(self):
        self.__updateTradeOffVehicleIntCD()
        with self.viewModel.transaction() as vm:
            vm.equipmentBlock.setTradeOffWidgetEnabled(bool(self.__tradeIn.getTradeOffVehicles()))
            vm.equipmentBlock.setBuyVehicleIntCD(self.__vehicle.intCD)
            vm.equipmentBlock.setTradeInTooltip(TOOLTIPS_CONSTANTS.PERSONAL_TRADE_IN_INFO if self.__isPersonalTradeIn() else TOOLTIPS_CONSTANTS.TRADE_IN_INFO)
            with vm.equipmentBlock.vehicleTradeInBtn.transaction() as vehicleTradeInBtnVm:
                if self.__isTradeIn():
                    vehicleTradeInBtnVm.setIcon(R.images.gui.maps.icons.library.trade_in())
                    vehicleTradeInBtnVm.setLabel(R.strings.store.buyVehicleWindow.tradeInBtnLabel())
                isTradeIn = not self.__isRentVisible and self.__isTradeIn()
                vehicleTradeInBtnVm.setIsVisible(isTradeIn and self.__tradeOffVehicle is None)
            self.__updateTradeOffVehicleBtnData()
        return

    def __updateTradeOffVehicleIntCD(self):
        with self.viewModel.transaction() as vm:
            self.__tradeOffVehicle = self.__tradeIn.getActiveTradeOffVehicle()
            self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()
            if self.__isTradeIn() and self.__tradeOffVehicle is not None and not self.__isRentVisible:
                vm.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
            elif self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None and not self.__isRentVisible:
                vm.setTradeOffVehicleIntCD(self.__personalTradeInSaleVehicle.intCD)
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__personalTradeInSaleVehicle.intCD)
            else:
                vm.setTradeOffVehicleIntCD(self.__TRADE_OFF_NOT_SELECTED)
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__TRADE_OFF_NOT_SELECTED)
        return

    def __updateRentInfo(self):
        with self.viewModel.transaction() as vm:
            vm.setIsRentSelected(self.__selectedRentID >= 0)
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockVm:
            selectedRentDays = 0
            selectedRentSeason = 0
            if self.__selectedRentID >= 0:
                rentType, packageID = parseRentID(self.__selectedRentID)
                rentPackage = self.__vehicle.rentPackages[self.__selectedRentIdx]
                if rentType == constants.RentType.TIME_RENT:
                    selectedRentDays = packageID
                elif rentType in (constants.RentType.SEASON_RENT, constants.RentType.SEASON_CYCLE_RENT):
                    selectedRentSeason = rentPackage['seasonType']
            else:
                rentType = constants.RentType.NO_RENT
            equipmentBlockVm.setSelectedRentID(self.__selectedRentID)
            equipmentBlockVm.setSelectedRentType(rentType)
            equipmentBlockVm.setSelectedRentDays(selectedRentDays)
            equipmentBlockVm.setSelectedRentSeason(selectedRentSeason)
            with equipmentBlockVm.vehicleRentBtn.transaction() as vehicleRentBtnVm:
                if self.__vehicle.hasRentPackages:
                    vehicleRentBtnVm.setIcon(R.images.gui.maps.icons.library.rent_ico_big())
                rentBtnAvailable = self.__isToggleRentAndTradeInState() and self.__isRentVisible
                rentBtnAvailable |= not self.__isToggleRentAndTradeInState() and self.__vehicle.hasRentPackages
                vehicleRentBtnVm.setIsVisible(rentBtnAvailable)

    def __updateTradeOffVehicleBtnData(self):
        with self.viewModel.equipmentBlock.vehicleBtn.transaction() as vehicleBtnVm:
            tradeInSaleVehicle = None
            if self.__isTradeIn() and self.__tradeOffVehicle is not None:
                tradeInSaleVehicle = self.__tradeOffVehicle
            elif self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None:
                tradeInSaleVehicle = self.__personalTradeInSaleVehicle
            vehicleBtnVm.setVisible(not self.__isRentVisible and tradeInSaleVehicle is not None)
            if tradeInSaleVehicle is not None:
                vehicleBtnVm.setFlag(tradeInSaleVehicle.nationName)
                vehicleBtnVm.setVehType(getTypeSmallIconPath(tradeInSaleVehicle.type, tradeInSaleVehicle.isPremium))
                vehicleBtnVm.setVehLvl(getLevelSmallIconPath(tradeInSaleVehicle.level))
                vehicleBtnVm.setVehIcon(getSmallIconPath(tradeInSaleVehicle.name))
                vehicleBtnVm.setVehName(tradeInSaleVehicle.shortUserName)
        return

    def __updateIsEnoughStatus(self, *_):
        if not self.__vehicle.isRented:
            with self.viewModel.transaction() as vm:
                ammoPriceModel = vm.equipmentBlock.ammo.actionPrices.getItems()
                ammoPrice = self.__getAmmoItemPrice()
                self.__updateActionPriceArray(ammoPriceModel, self.__getAmmoItemPrice())
                slotPriceModel = vm.equipmentBlock.slot.actionPrices.getItems()
                slotItemPrice = self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)
                self.__updateActionPriceArray(slotPriceModel, slotItemPrice)
                equipmentBlock = vm.equipmentBlock
                equipmentBlock.ammo.setIsEnabled(self.__getAmmoIsAvailable(ammoPrice.price))
                equipmentBlock.slot.setIsEnabled(self.__getSlotIsAvailable(slotItemPrice.price))
                idx = 0
                commanderCards = vm.commanderLvlCards.getItems()
                for commanderCardModel in commanderCards:
                    commanderLvlsCost = self.__shop.getTankmanCostItemPrices()
                    commanderPriceModel = commanderCardModel.actionPrice.getItems()
                    commanderItemPrice = commanderLvlsCost[idx]
                    commanderItemPrice *= len(self.__vehicle.crew)
                    self.__updateActionPriceArray(commanderPriceModel, commanderItemPrice)
                    isEnabled = self.__isAvailablePrice(commanderItemPrice.price)
                    commanderCardModel.setSlotIsEnabled(isEnabled and not self.__isWithoutCommander)
                    idx += 1

            self.__updateTotalPrice()

    def __updateTotalPrice(self):
        totalPrice = self.__getTotalItemPrice()
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockVm:
            if self.__isTradeIn() or self.__isPersonalTradeIn():
                equipmentBlockVm.setConfirmGoldPrice(totalPrice.price.get(Currency.GOLD))
                popoverIsAvailable = totalPrice.price.get(Currency.GOLD) <= self.__stats.money.get(Currency.GOLD)
                if totalPrice.price.gold <= 0:
                    popoverIsAvailable = False
                self.__popoverIsAvailable = popoverIsAvailable
                equipmentBlockVm.setPopoverIsAvailable(popoverIsAvailable and not self.__isRentVisible)
            totalPriceArray = equipmentBlockVm.totalPrice.getItems()
            for model in totalPriceArray:
                currencyType = model.getType()
                currencyValue = int(totalPrice.price.get(currencyType, 0))
                currencyDefValue = int(totalPrice.defPrice.get(currencyType, 0))
                model.setPrice(self.gui.systemLocale.getNumberFormat(currencyValue))
                model.setDefPrice(getIntegralFormat(currencyDefValue))
                if not self.__isPurchaseCurrencyAvailable(currencyType):
                    model.setIsEnough(currencyValue <= self.__stats.money.get(currencyType))
                isAction = totalPrice.getActionPrcAsMoney().get(currencyType) is not None and currencyValue < currencyDefValue
                model.setShowOldValue(isAction)
                model.setIsWithAction(isAction and (self.__tradeOffVehicle is None or not self.__isValidTradeOffSelected()) and self.__vehicle.intCD not in self.__personalTradeIn.getBuyVehicleCDs())
                model.setIsBootcamp(self.__bootcamp.isInBootcamp())
                if isAction:
                    updateActionInViewModel(currencyType, model, totalPrice)

            self.__updateBuyBtnStatus(totalPrice)
        return

    def __updateBuyBtnStatus(self, totalPrice):
        totalPriceMoney = totalPrice.price
        statsMoney = self.__stats.money
        isEnabled = True
        for currency in Currency.ALL:
            if not self.__isPurchaseCurrencyAvailable(currency):
                isEnabled &= totalPriceMoney.get(currency) <= statsMoney.get(currency)

        if self.__isTradeIn() and self.__tradeOffVehicle is not None:
            isEnabled &= self.__isValidTradeOffSelected() and self.__tradeOffVehicle.isReadyToTradeOff
        if self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None:
            isEnabled &= self.__isValidPersonalTradeInSelected() and self.__personalTradeInSaleVehicle.isReadyPersonalTradeInSale
        self.viewModel.equipmentBlock.setBuyBtnIsEnabled(isEnabled)
        return

    def __updateBuyBtnLabel(self):
        if self.__selectedRentIdx == self.__RENT_NOT_SELECTED_IDX:
            label = R.strings.store.buyVehicleWindow.restore()
        elif not self.__isRentVisible and (self.__isTradeIn() and self.__tradeOffVehicle is not None or self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None):
            label = R.strings.store.buyVehicleWindow.exchange()
        elif self.__selectedRentID >= 0:
            label = R.strings.store.buyVehicleWindow.rentBtn()
        else:
            label = R.strings.store.buyVehicleWindow.buyBtn()
        self.viewModel.equipmentBlock.setBuyBtnLabel(label)
        return

    def __getAmmoItemPrice(self):
        ammoPrice = ITEM_PRICE_EMPTY
        for shell in self.__vehicle.gun.defaultAmmo:
            ammoPrice += shell.buyPrices.itemPrice * shell.count

        return ammoPrice

    def __getAmmoIsAvailable(self, ammoPrice):
        return not self.__vehicle.isAmmoFull and self.__isAvailablePrice(ammoPrice)

    def __getSlotIsAvailable(self, slotPrice):
        isSlotForRent = self.__selectedRentIdx >= 0 and self.__isRentVisible
        isSlotForTradeIn = self.__isTradeIn() and self.__tradeOffVehicle is not None and not self.__isRentVisible
        return not isSlotForRent and not isSlotForTradeIn and self.__isAvailablePrice(slotPrice)

    def __getTotalItemPrice(self):
        price = defPrice = ZERO_MONEY
        if self.__isTradeIn() and self.__tradeOffVehicle is not None and not self.__isRentVisible:
            tradeInPrice = self.__tradeIn.getTradeInPrice(self.__vehicle)
            price = tradeInPrice.price
            defPrice = tradeInPrice.defPrice
        elif self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None and not self.__isRentVisible:
            tradeInPrice = self.__personalTradeIn.getPersonalTradeInPrice(self.__vehicle)
            price = tradeInPrice.price
            defPrice = tradeInPrice.defPrice
        elif self.__selectedRentIdx >= 0 and self.__isRentVisible:
            price += self.__vehicle.rentPackages[self.__selectedRentIdx]['rentPrice']
        elif self.viewModel.getIsRestore():
            price += self.__vehicle.restorePrice
        else:
            price += self.__vehicle.buyPrices.itemPrice.price
            defPrice += self.__vehicle.buyPrices.itemPrice.defPrice
        if not self.__isWithoutCommander:
            commanderCardsPrices = self.__shop.getTankmanCostItemPrices()
            commanderItemPrice = commanderCardsPrices[self.__selectedCardIdx]
            commanderItemPrice *= len(self.__vehicle.crew)
            price += commanderItemPrice.price
        if self.viewModel.equipmentBlock.slot.getIsSelected() and not (self.__selectedRentIdx >= 0 and self.__isRentVisible):
            vehSlots = self.__stats.vehicleSlots
            price += self.__shop.getVehicleSlotsItemPrice(vehSlots).price
        if self.viewModel.equipmentBlock.ammo.getIsSelected():
            price += self.__getAmmoItemPrice().price
        if defPrice is ZERO_MONEY:
            defPrice = price
        return ItemPrice(price=price, defPrice=defPrice)

    def __getObtainVehicleProcessor(self, crewType):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleBuyer(self.__vehicle, isWithSlot, isWithAmmo, crewType)

    def __getRestoreVehicleProcessor(self, crewType):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleRestoreProcessor(self.__vehicle, isWithSlot, isWithAmmo, crewType)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return
        else:
            if tooltipId in (TOOLTIPS_CONSTANTS.TRADE_IN_INFO, TOOLTIPS_CONSTANTS.TRADE_IN_INFO_NOT_AVAILABLE, TOOLTIPS_CONSTANTS.PERSONAL_TRADE_IN_INFO):
                args = (self.__tradeIn.getAllowedVehicleLevels(self.__vehicle.level),)
            elif tooltipId == TOOLTIPS_CONSTANTS.TRADE_IN_STATE_NOT_AVAILABLE:
                if self.__previousAlias in (VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW, VIEW_ALIAS.LOBBY_STORE):
                    veh = self.__personalTradeInSaleVehicle
                else:
                    veh = self.__tradeOffVehicle
                args = (veh,)
            elif tooltipId == TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_TRADEOFF:
                args = (self.__tradeOffVehicle.intCD,)
            elif tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                args = (event.getArgument('tooltipType'),
                 event.getArgument('key'),
                 (event.getArgument('newCredits'), event.getArgument('newGold'), event.getArgument('newCrystal')),
                 (event.getArgument('oldCredits'), event.getArgument('oldGold'), event.getArgument('oldCrystal')),
                 event.getArgument('isBuying'))
            else:
                args = None
            return TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=args)

    def __addVMsInActionPriceList(self, listArray, itemPrice, fontNotEnoughIsEnabled=True, tooltipData=None):
        actionPriceModels = getItemPricesViewModel(self.__stats.money, itemPrice, isBootcamp=self.__bootcamp.isInBootcamp())[0]
        for model in actionPriceModels:
            if tooltipData is not None:
                model.setKey(tooltipData.key)
                model.setTooltipType(tooltipData.itemType)
            listArray.addViewModel(model)
            if self.__isPurchaseCurrencyAvailable(model.getType()):
                model.setFontNotEnoughIsEnabled(fontNotEnoughIsEnabled)

        return

    def __isAvailablePrice(self, money):
        isPurchaseCurrencyAvailable = money.isDefined()
        statsMoney = self.__stats.money
        for currency in Currency.ALL:
            currencyValue = money.get(currency)
            if currencyValue and currencyValue > statsMoney.get(currency):
                isPurchaseCurrencyAvailable &= self.__isPurchaseCurrencyAvailable(currency)

        return self.__stats.money >= money or isPurchaseCurrencyAvailable

    def __isPurchaseCurrencyAvailable(self, currencyType):
        return currencyType == Currency.GOLD and self.__isGoldAutoPurchaseEnabled

    def __isTradeIn(self):
        isBuyingAllowed = not self.__vehicle.isDisabledForBuy and not self.__vehicle.isHidden
        return bool(self.__tradeIn.isEnabled() and self.__vehicle.canTradeIn and isBuyingAllowed)

    def __isPersonalTradeIn(self):
        return self.__vehicle.canPersonalTradeInBuy and not self.__vehicle.isDisabledForBuy

    def __isToggleRentAndTradeInState(self):
        return False if not self.__vehicle else self.__isTradeIn() and self.__vehicle.hasRentPackages

    def __isValidTradeOffSelected(self):
        tradeOffVehicles = self.__tradeIn.getTradeOffVehicles(self.__vehicle.level)
        return tradeOffVehicles is not None and self.__tradeOffVehicle.intCD in tradeOffVehicles

    def __isValidPersonalTradeInSelected(self):
        tradeInSaleVehicles = self.__personalTradeIn.getSaleVehicleCDs()
        return tradeInSaleVehicles is not None and self.__personalTradeInSaleVehicle.intCD in tradeInSaleVehicles

    def __isRenting(self):
        return not self.__isBuying()

    def __isBuying(self):
        return self.__selectedRentIdx in (self.__RENT_UNLIM_IDX, self.__RENT_NOT_SELECTED_IDX) or not self.__isRentVisible

    def __startTutorial(self):
        if not self.__vehicle.isCollectible:
            return
        collectibleVehicles = set(getCollectibleVehiclesInInventory().keys())
        if len(collectibleVehicles) == 1 and self.__vehicle.intCD in collectibleVehicles:
            event_dispatcher.runSalesChain(_COLLECTIBLE_VEHICLE_TUTORIAL)


class BuyVehicleWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, **kwargs):
        flags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(BuyVehicleWindow, self).__init__(flags, content=BuyVehicleView(**kwargs))

    def showCongratulations(self):
        self.content.showCongratulations()
