# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/buy_vehicle_view.py
import logging
from functools import partial
import typing
import adisp
import constants
import nations
from CurrentVehicle import g_currentPreviewVehicle
from async import async, await
from frameworks.wulf import WindowFlags, ViewStatus, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.DialogsInterface import showI18nConfirmDialog
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.game_control.event_progression_controller import EventProgressionScreens
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, TooltipData, getIntegralFormat
from gui.impl.dialogs.dialogs import showConvertCurrencyForVehicleView, showBuyCarouselSlotView
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.ui_kit.action_price_model import ActionPriceModel
from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_view_model import BuyVehicleViewModel
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import event_dispatcher, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent
from gui.shared.events import VehicleBuyEvent
from gui.shared.formatters import updateActionInViewModel, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getSmallIconPath, getLevelSmallIconPath, getTypeSmallIconPath, getNationLessName, getIconResourceName
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter, VehicleTradeInProcessor, VehicleRestoreProcessor, VehiclePersonalTradeInProcessor
from gui.shared.money import Currency, Money, ZERO_MONEY
from gui.shared.utils import decorators
from gui.shared.utils.vehicle_collector_helper import getCollectibleVehiclesInInventory
from gui.shop import showBuyGoldForVehicleWebOverlay, showTradeOffOverlay, showPersonalTradeOffOverlay
from helpers import dependency, int2roman, func_utils
from items import UNDEFINED_ITEM_CD
from rent_common import parseRentID
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IRentalsController, ITradeInController, IRestoreController, IBootcampController, IWalletController, IEventProgressionController, IPersonalTradeInController, ISoundEventChecker
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_content_view_model import BuyVehicleContentViewModel
    from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_item_slot_model import BuyVehicleItemSlotModel
    from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_congratulation_model import BuyVehicleCongratulationModel
    from gui.impl.gen.view_models.ui_kit.vehicle_btn_model import VehicleBtnModel
    from frameworks.wulf import Array
_logger = logging.getLogger(__name__)

class VehicleBuyActionTypes(CONST_CONTAINER):
    DEFAULT = 0
    BUY = 1
    RESTORE = 2
    RENT = 3


_VP_SHOW_PREVIOUS_SCREEN_ON_SUCCESS_ALIASES = (VIEW_ALIAS.VEHICLE_PREVIEW,
 VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW,
 VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW,
 VIEW_ALIAS.LOBBY_STORE)
_COLLECTIBLE_VEHICLE_TUTORIAL = 'collectibleVehicle'
_TITLE_ICON_PLACEHOLDER = '%%ICON%%'

class BuyVehicleView(ViewImpl, EventSystemEntity):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rentals = dependency.descriptor(IRentalsController)
    __tradeIn = dependency.descriptor(ITradeInController)
    __personalTradeIn = dependency.descriptor(IPersonalTradeInController)
    __wallet = dependency.descriptor(IWalletController)
    __restore = dependency.descriptor(IRestoreController)
    __bootcamp = dependency.descriptor(IBootcampController)
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __soundEventChecker = dependency.descriptor(ISoundEventChecker)
    __RENT_NOT_SELECTED_IDX = -2
    __RENT_UNLIM_IDX = -1
    __TRADE_OFF_NOT_SELECTED = -1

    def __init__(self, **kwargs):
        settings = ViewSettings(R.views.lobby.buy_vehicle.buy_vehicle_view.BuyVehicleView())
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
        self.__popoverIsAvailable = True
        self.__tradeInInProgress = False
        self.__purchaseInProgress = False
        self.__usePreviousAlias = False
        self.__tooltipIdToArgsFunc = {TOOLTIPS_CONSTANTS.TRADE_IN_INFO: self.__getTradeInTooltipArgs,
         TOOLTIPS_CONSTANTS.TRADE_IN_INFO_NOT_AVAILABLE: self.__getTradeInTooltipArgs,
         TOOLTIPS_CONSTANTS.PERSONAL_TRADE_IN_INFO: self.__getTradeInTooltipArgs,
         TOOLTIPS_CONSTANTS.TRADE_IN_STATE_NOT_AVAILABLE: self.__getTradeInStateNotAvailableTooltipArgs,
         TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_TRADEOFF: self.__getSelectedVehicleTradeOffTooltipArgs,
         TOOLTIPS_CONSTANTS.ACTION_PRICE: self.__getActionPriceTooltipArgs,
         TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY: self.__getCurrencyDeficitTooltipArgs,
         TOOLTIPS_CONSTANTS.BUY_VEHICLE_AMMO_TOOLTIP: self.__getAmmoTooltipArgs,
         TOOLTIPS_CONSTANTS.BUY_VEHICLE_SLOT_TOOLTIP: self.__getSlotTooltipArgs}
        return

    @property
    def viewModel(self):
        return super(BuyVehicleView, self).getViewModel()

    @property
    def isRent(self):
        return self.__vehicle.hasRentPackages and (not self.__vehicle.isRestoreAvailable() or self.__actionType == VehicleBuyActionTypes.RENT) and self.__actionType != VehicleBuyActionTypes.BUY

    @property
    def isTradeInVisible(self):
        return self.__isTradeIn() and self.__tradeOffVehicle is not None and not self.__isRentVisible

    @property
    def isPersonalTradeInVisible(self):
        return self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None and not self.__isRentVisible

    @property
    def hasEmptySlot(self):
        return self.__itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0

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
        self.setChildView(R.dynamic_ids.buy_vehicl_view.balance_content(), CommonBalanceContent())
        self.__addListeners()
        self.__isGoldAutoPurchaseEnabled = self.__wallet.isAvailable
        self.__updateData()
        if self.__showOnlyCongrats:
            self.viewModel.setIsContentHidden(True)
        with self.viewModel.transaction() as vm:
            vm.setBgSource(R.images.gui.maps.icons.store.shop_2_background_arsenal())
            vm.setNation(nations.NAMES[self.__vehicle.nationID])
            equipmentBlock = vm.equipmentBlock
            self.__setTexts(equipmentBlock)
            equipmentBlock.setVehicleType(self.__vehicle.typeBigIconResource())
            equipmentBlock.setIsElite(self.__vehicle.isElite)
            equipmentBlock.setIsRentVisible(self.__isRentVisible)
            equipmentBlock.setTradeInIsEnabled(self.__isTradeIn())
            equipmentBlock.setPersonalTradeInIsEnabled(self.__isPersonalTradeIn())
            equipmentBlock.setEmtySlotAvailable(self.hasEmptySlot)
            equipmentBlock.setIsRestore(self.__vehicle.isRestoreAvailable())
            equipmentBlock.ammo.setIsEnabled(not self.__vehicle.isAmmoFull)
            equipmentBlock.ammo.setTooltipId(TOOLTIPS_CONSTANTS.BUY_VEHICLE_AMMO_TOOLTIP)
            equipmentBlock.slot.setTooltipId(TOOLTIPS_CONSTANTS.BUY_VEHICLE_SLOT_TOOLTIP)
            resName = getIconResourceName(getNationLessName(self.__vehicle.name))
            vm.setVehicleImage(R.images.gui.maps.shop.vehicles.c_180x135.dyn(resName)())
            self.__updateSlotItem()
            self.__updateAmmoItem()
            self.__updateTradeInInfo()
            self.__updateRentInfo()
            self.__updateBuyBtnLabel()
            self.__updateTotalPrice()

    def _finalize(self):
        self.__removeListeners()
        super(BuyVehicleView, self)._finalize()

    def __addListeners(self):
        self.addListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffVehicleSelected)
        g_clientUpdateManager.addMoneyCallback(self.__updateIsEnoughStatus)
        g_clientUpdateManager.addCallbacks({'shop.exchangeRate': self.__updateIsEnoughStatus})
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onInHangarClick += self.__onInHangar
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onBackClick += self.__onWindowClose
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
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onInHangarClick -= self.__onInHangar
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onBackClick -= self.__onWindowClose
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onSelectTradeOffVehicle -= self.__onSelectTradeOffVehicle
        equipmentBlock.onCancelTradeOffVehicle -= self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange -= self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange -= self.__onSelectedChange
        self.__restore.onRestoreChangeNotify -= self.__onRestoreChange
        self.__itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged -= self.__onActiveTradeInSaleVehicleChanged

    def __setTexts(self, vm):
        rBuyVehicleWindow = R.strings.store.buyVehicleWindow
        if self.__selectedRentID > 0:
            resId = rBuyVehicleWindow.titleRent()
            footerResId = rBuyVehicleWindow.footerTextRent()
        elif self.__isRestore:
            resId = rBuyVehicleWindow.titleRestore()
            footerResId = rBuyVehicleWindow.footerTextRestore()
        else:
            resId = rBuyVehicleWindow.titleBuy()
            footerResId = rBuyVehicleWindow.footerText()
        text = backport.text(resId, vehicleType=backport.text(rBuyVehicleWindow.type.dyn(self.__vehicle.uiType)()), level=int2roman(self.__vehicle.level), vehicleName=self.__vehicle.shortUserName, icon=_TITLE_ICON_PLACEHOLDER)
        splitTitle = text.split(_TITLE_ICON_PLACEHOLDER)
        vm.setTitleLeft(splitTitle[0])
        vm.setTitleRight(splitTitle[1])
        vm.setBuyBlockLabel(footerResId)

    def __onItemCacheSyncCompleted(self, *_):
        if self.__purchaseInProgress or self.viewModel is None or self.viewModel.proxy is None:
            return
        else:
            self.__updateData()
            self.__updateSlotItem()
            self.__updateAmmoItem()
            self.__updateTradeInInfo()
            self.__updateRentInfo()
            self.__updateTotalPrice()
            return

    def __updateData(self):
        self.__vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        self.__tradeOffVehicle = self.__tradeIn.getActiveTradeOffVehicle()
        self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()
        self.__isRestore = self.__vehicle.isRestoreAvailable()
        self.__isRentVisible = self.__vehicle.hasRentPackages and not self.__isTradeIn() and not self.__isPersonalTradeIn()
        if self.__isRestore:
            self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
            self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX
        elif self.__vehicle.hasRentPackages and self.__vehicle.rentPackages:
            self.__selectedRentIdx = 0
            self.__selectedRentID = self.__vehicle.rentPackages[0]['rentID']
        else:
            self.__selectedRentIdx = self.__RENT_UNLIM_IDX
            self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX

    def __onInHangar(self, *_):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.__startTutorial()
        self.__destroyWindow()

    @async
    def __onBuyBtnClick(self, *_):
        if self.__tradeInInProgress:
            return
        if self.viewModel.getIsContentHidden():
            self.__onInHangar()
            return
        if self.__showBuyGoldWindowIfNeeded():
            return
        totalPrice = self.__getTotalItemPrice().price
        shortage = self.__stats.money.getShortage(totalPrice)
        shortageOfCredits = shortage.get(Currency.CREDITS)
        if shortageOfCredits > 0:
            if self._canBuyAmountOfCredits(shortageOfCredits):
                sdr = yield await(showConvertCurrencyForVehicleView(ctx={'needCredits': shortageOfCredits,
                 'vehicleCD': self.__vehicle.intCD,
                 'title': R.strings.detachment.commonCurrency.title()}))
                if sdr.busy:
                    return
                isOk, data = sdr.result
                if isOk == DialogButtons.SUBMIT and not self.isDisposed():
                    self.__exchangeGold(int(data['gold']))
            return
        if not self.viewModel.equipmentBlock.slot.getIsSelected() and not self.hasEmptySlot:
            busy, isOk = yield await(showBuyCarouselSlotView())
            if busy or self.isDisposed():
                return
            if isOk:
                self.viewModel.equipmentBlock.slot.setIsSelected(True)
                if self.__showBuyGoldWindowIfNeeded():
                    self.viewModel.equipmentBlock.slot.setIsSelected(False)
                    return
            else:
                self.__playSlotAnimation()
                return
        self.__requestForMoneyObtain()

    def __showBuyGoldWindowIfNeeded(self):
        totalPrice = self.__getTotalItemPrice().price
        shortageOfGold = self.__stats.money.getShortage(totalPrice).get(Currency.GOLD)
        if shortageOfGold > 0:
            if self.__isGoldAutoPurchaseEnabled:
                showBuyGoldForVehicleWebOverlay(shortageOfGold, self.__vehicle.intCD, self.getParentWindow())
                return True
        return False

    @decorators.process('transferMoney')
    def __exchangeGold(self, gold):
        result = yield GoldToCreditsExchanger(gold, withConfirm=False).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__onBuyBtnClick()

    def __onSelectedChange(self, *_):
        self.__updateSlotItem()
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
            self.__updateSlotItem()
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
            self.__updateSlotItem()
            self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        return

    def __onCancelTradeOffVehicle(self, _=None):
        self.__tradeOffVehicle = None
        self.__tradeIn.setActiveTradeOffVehicleCD(UNDEFINED_ITEM_CD)
        self.__updateTradeInInfo()
        self.__updateTotalPrice()
        self.__updateSlotItem()
        self.__updateBuyBtnLabel()
        return

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
        self.__updateSlotItem()
        self.__updateBuyBtnLabel()

    def __onRentTermSelected(self, event):
        itemIdx = event.ctx
        self.__selectedRentIdx = itemIdx
        if self.__selectedRentIdx == self.__RENT_UNLIM_IDX:
            if self.__isRestore:
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
        self.__updateSlotItem()
        self.viewModel.commit()

    def __onWindowClose(self, *_):
        self.__destroyWindow()
        if self.__usePreviousAlias and self.__returnCallback:
            self.__returnCallback()

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
            elif self.__previousAlias == VIEW_ALIAS.EVENT_PROGRESSION_VEHICLE_PREVIEW:
                returnCallback = partial(self.__eventProgression.showCustomScreen, EventProgressionScreens.MAIN)
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
                vType = self.__vehicle.type
                vehicleType = '{}_elite'.format(vType) if self.__vehicle.isElite else vType
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
                vm.setTitle(R.strings.store.congratulationAnim.restoreLabel() if self.__isRestore else R.strings.store.congratulationAnim.buyingLabel())
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
        isWithSlot = equipmentBlock.slot.getIsSelected()
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        result = None
        self.__purchaseInProgress = False
        if self.isTradeInVisible:
            vehicle = self.__tradeOffVehicle
            processor = VehicleTradeInProcessor(self.__vehicle, self.__tradeOffVehicle, isWithSlot, isWithAmmo)
        elif self.isPersonalTradeInVisible:
            vehicle = self.__personalTradeInSaleVehicle
            processor = VehiclePersonalTradeInProcessor(self.__vehicle, self.__personalTradeInSaleVehicle, isWithSlot, isWithAmmo)
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
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
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
        if not (self.isTradeInVisible or self.isPersonalTradeInVisible):
            if self.__isBuying():
                if self.__isRestore:
                    result = yield self.__getRestoreVehicleProcessor().request()
                else:
                    result = yield self.__getObtainVehicleProcessor().request()
            else:
                result = yield VehicleRenter(self.__vehicle, self.__selectedRentID, isWithAmmo).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
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
        if operations:
            operationsStr = [ backport.text(R.strings.dialogs.tradeInConfirmation.message.dyn(o)()) for o in operations ]
            addition = backport.text(R.strings.dialogs.tradeInConfirmation.message.addition(), operations=', '.join(operationsStr))
        ctx = {'vehName': text_styles.neutral(vehicle.userName),
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
        isEnough = statsMoney.get(currencyType) >= currencyValue
        priceModel.setIsEnough(isEnough)
        hasAction = itemPrice.getActionPrcAsMoney().get(currencyType) is not None
        priceModel.setIsWithAction(hasAction)
        if hasAction:
            updateActionInViewModel(currencyType, priceModel, itemPrice)
        priceModel.setIsBootcamp(self.__bootcamp.isInBootcamp())
        return

    def __updateSlotItem(self):
        slotItemPrice = self.__getSlotItemPrice()
        with self.viewModel.equipmentBlock.slot.transaction() as slotVm:
            self.__tradeOffVehicle = self.__tradeIn.getActiveTradeOffVehicle()
            self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()
            isAvailable = self.__getSlotIsAvailable()
            slotVm.setIsEnabled(isAvailable)
            if not isAvailable:
                slotVm.setIsSelected(False)
            listArray = slotVm.actionPrices.getItems()
            isInit = len(listArray) == 0
            if isInit:
                self.__addVMsInActionPriceList(listArray, slotItemPrice)
            self.__updateActionPriceArray(listArray, slotItemPrice)

    def __updateAmmoItem(self):
        ammoItemPrice = self.__getAmmoItemPrice()
        with self.viewModel.equipmentBlock.ammo.transaction() as ammoVm:
            listArray = ammoVm.actionPrices.getItems()
            isInit = len(listArray) == 0
            if isInit:
                self.__addVMsInActionPriceList(listArray, ammoItemPrice)
            self.__updateActionPriceArray(listArray, ammoItemPrice)

    def __updateTradeInInfo(self):
        self.__updateTradeOffVehicleIntCD()
        with self.viewModel.transaction() as vm:
            vm.equipmentBlock.setTradeOffWidgetEnabled(bool(self.__tradeIn.getTradeOffVehicles()))
            vm.equipmentBlock.setBuyVehicleIntCD(self.__vehicle.intCD)
            vm.equipmentBlock.setTradeInTooltip(TOOLTIPS_CONSTANTS.PERSONAL_TRADE_IN_INFO if self.__isPersonalTradeIn() else TOOLTIPS_CONSTANTS.TRADE_IN_INFO)
            vehicleTradeInBtnVm = vm.equipmentBlock.vehicleTradeInBtn
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
            if self.isTradeInVisible:
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
            elif self.__isPersonalTradeIn() and self.__personalTradeInSaleVehicle is not None and not self.__isRentVisible:
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__personalTradeInSaleVehicle.intCD)
            else:
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__TRADE_OFF_NOT_SELECTED)
        return

    def __updateRentInfo(self):
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
            self.__setTexts(equipmentBlockVm)
            equipmentBlockVm.setSelectedRentID(self.__selectedRentID)
            equipmentBlockVm.setSelectedRentType(rentType)
            equipmentBlockVm.setSelectedRentDays(selectedRentDays)
            equipmentBlockVm.setSelectedRentSeason(selectedRentSeason)
            vehicleRentBtnVm = equipmentBlockVm.vehicleRentBtn
            if self.__vehicle.hasRentPackages:
                vehicleRentBtnVm.setIcon(R.images.gui.maps.icons.library.rent_ico_big())
            rentBtnAvailable = self.__isToggleRentAndTradeInState() and self.__isRentVisible
            rentBtnAvailable |= not self.__isToggleRentAndTradeInState() and self.__vehicle.hasRentPackages
            vehicleRentBtnVm.setIsVisible(rentBtnAvailable)

    def __updateTradeOffVehicleBtnData(self):
        with self.viewModel.equipmentBlock.vehicleBtn.transaction() as vehicleBtnVm:
            tradeInSaleVehicle = None
            if self.isTradeInVisible:
                tradeInSaleVehicle = self.__tradeOffVehicle
            elif self.isPersonalTradeInVisible:
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
                self.__updateActionPriceArray(ammoPriceModel, self.__getAmmoItemPrice())
                slotPriceModel = vm.equipmentBlock.slot.actionPrices.getItems()
                slotItemPrice = self.__getSlotItemPrice()
                self.__updateActionPriceArray(slotPriceModel, slotItemPrice)
            self.__updateTotalPrice()

    def __updateTotalPrice(self):
        vehiclePrice = self.__getVehiclePrice()
        totalPrice = self.__getTotalItemPrice()
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockVm:
            if self.__isTradeIn() or self.__isPersonalTradeIn():
                equipmentBlockVm.setConfirmGoldPrice(int(totalPrice.price.get(Currency.GOLD)))
                popoverIsAvailable = totalPrice.price.get(Currency.GOLD) <= self.__stats.money.get(Currency.GOLD)
                if totalPrice.price.gold <= 0:
                    popoverIsAvailable = False
                self.__popoverIsAvailable = popoverIsAvailable
                equipmentBlockVm.setPopoverIsAvailable(popoverIsAvailable and not self.__isRentVisible)
            totalPriceArray = equipmentBlockVm.totalPrice.getItems()
            totalPriceArray.clear()
            self.__addVMsInActionPriceList(totalPriceArray, totalPrice, False)
            totalPriceArray.invalidate()
            for model in totalPriceArray:
                currencyType = model.getType()
                currencyValue = int(totalPrice.price.get(currencyType, 0))
                currencyDefValue = int(totalPrice.defPrice.get(currencyType, 0))
                model.setPrice(self.gui.systemLocale.getNumberFormat(currencyValue))
                model.setDefPrice(getIntegralFormat(currencyDefValue))
                model.setIsEnough(currencyValue <= self.__stats.money.get(currencyType))
                isAction = vehiclePrice.getActionPrcAsMoney().get(currencyType) is not None and currencyValue < currencyDefValue
                model.setIsWithAction(isAction and (self.__tradeOffVehicle is None or not self.__isValidTradeOffSelected()) and self.__vehicle.intCD not in self.__personalTradeIn.getBuyVehicleCDs())
                model.setIsBootcamp(self.__bootcamp.isInBootcamp())
                if isAction:
                    updateActionInViewModel(currencyType, model, vehiclePrice)
                if not isAction and not model.getIsEnough():
                    model.setTooltipType(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY)
                model.setTooltipType('')

            equipmentBlockVm.setIsFree(not totalPriceArray)
            self.__updateBuyBtnStatus(totalPrice, equipmentBlockVm)
        return

    def __updateBuyBtnStatus(self, totalPrice, vm):
        totalPriceMoney = totalPrice.price
        statsMoney = self.__stats.money
        isEnabled = True
        vm.setDisabledBuyButtonTooptip('')
        shortage = statsMoney.getShortage(totalPriceMoney)
        if shortage.get(Currency.GOLD) > 0 and not self.__isGoldAutoPurchaseEnabled:
            isEnabled = False
            vm.setDisabledBuyButtonTooptip(TOOLTIPS_CONSTANTS.BUY_VEHICLE_NO_WALLET)
        elif shortage.get(Currency.CREDITS) > 0 and not self._canBuyAmountOfCredits(shortage.get(Currency.CREDITS)):
            isEnabled = False
            vm.setDisabledBuyButtonTooptip(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY)
        else:
            skipCurrencies = (Currency.GOLD, Currency.CREDITS)
            for currency in Currency.ALL:
                if currency not in skipCurrencies:
                    isEnabled &= not shortage.get(currency)

        if self.isTradeInVisible:
            isEnabled &= self.__isValidTradeOffSelected() and self.__tradeOffVehicle.isReadyToTradeOff
        if self.isPersonalTradeInVisible:
            isEnabled &= self.__isValidPersonalTradeInSelected() and self.__personalTradeInSaleVehicle.isReadyPersonalTradeInSale
        self.viewModel.equipmentBlock.setBuyBtnIsEnabled(isEnabled)

    def __updateBuyBtnLabel(self):
        rBuyVehicleWindow = R.strings.store.buyVehicleWindow
        if self.__selectedRentIdx == self.__RENT_NOT_SELECTED_IDX:
            label = rBuyVehicleWindow.restore()
        elif self.isTradeInVisible or self.isPersonalTradeInVisible:
            label = rBuyVehicleWindow.exchange()
        elif self.__selectedRentID >= 0:
            label = rBuyVehicleWindow.rentBtn()
        else:
            label = rBuyVehicleWindow.buyBtn()
        self.viewModel.equipmentBlock.setBuyBtnLabel(label)

    def __getAmmoItemPrice(self):
        ammoPrice = ITEM_PRICE_EMPTY
        for shell in self.__vehicle.gun.defaultAmmo:
            ammoPrice += shell.buyPrices.itemPrice * shell.count

        return ammoPrice

    def __getSlotItemPrice(self):
        return self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)

    def __getSlotIsAvailable(self):
        isSlotForRent = self.__selectedRentIdx >= 0 and self.__isRentVisible
        return not isSlotForRent and not self.isTradeInVisible

    def __getVehiclePrice(self):
        price = defPrice = ZERO_MONEY
        if self.isTradeInVisible:
            tradeInPrice = self.__tradeIn.getTradeInPrice(self.__vehicle)
            price = tradeInPrice.price
            defPrice = tradeInPrice.defPrice
        elif self.isPersonalTradeInVisible:
            tradeInPrice = self.__personalTradeIn.getPersonalTradeInPrice(self.__vehicle)
            price = tradeInPrice.price
            defPrice = tradeInPrice.defPrice
        elif self.__selectedRentIdx >= 0 and self.__isRentVisible:
            price += self.__vehicle.rentPackages[self.__selectedRentIdx]['rentPrice']
        elif self.__isRestore:
            price += self.__vehicle.restorePrice
        else:
            price += self.__vehicle.buyPrices.itemPrice.price
            defPrice += self.__vehicle.buyPrices.itemPrice.defPrice
        return ItemPrice(price=price, defPrice=defPrice)

    def __getTotalItemPrice(self):
        vehiclePrice = self.__getVehiclePrice()
        price = vehiclePrice.price
        defPrice = vehiclePrice.defPrice
        if self.viewModel.equipmentBlock.slot.getIsSelected() and not (self.__selectedRentIdx >= 0 and self.__isRentVisible):
            vehSlots = self.__stats.vehicleSlots
            price += self.__shop.getVehicleSlotsItemPrice(vehSlots).price
        if self.viewModel.equipmentBlock.ammo.getIsSelected():
            price += self.__getAmmoItemPrice().price
        if defPrice is ZERO_MONEY:
            defPrice = price
        price = Money(**{c:price.get(c) for c in Currency.ALL if price.get(c) or defPrice.get(c)})
        return ItemPrice(price=price, defPrice=defPrice)

    def __getObtainVehicleProcessor(self):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleBuyer(self.__vehicle, isWithSlot, isWithAmmo)

    def __getRestoreVehicleProcessor(self):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleRestoreProcessor(self.__vehicle, isWithSlot, isWithAmmo)

    def __getTradeInTooltipArgs(self, _):
        return (self.__tradeIn.getAllowedVehicleLevels(self.__vehicle.level),)

    def __getTradeInStateNotAvailableTooltipArgs(self, _):
        if self.__previousAlias in (VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW, VIEW_ALIAS.LOBBY_STORE):
            veh = self.__personalTradeInSaleVehicle
        else:
            veh = self.__tradeOffVehicle
        return (veh,)

    def __getSelectedVehicleTradeOffTooltipArgs(self, _):
        return (self.__tradeOffVehicle.intCD,)

    def __getActionPriceTooltipArgs(self, event):
        return (event.getArgument('tooltipType'),
         event.getArgument('key'),
         (event.getArgument('newCredits'), event.getArgument('newGold'), event.getArgument('newCrystal')),
         (event.getArgument('oldCredits'), event.getArgument('oldGold'), event.getArgument('oldCrystal')),
         event.getArgument('isBuying'),
         False,
         None,
         True)

    def __getCurrencyDeficitTooltipArgs(self, event):
        currency = event.getArgument('currency', Currency.CREDITS)
        return (self.__stats.money.getShortage(self.__getTotalItemPrice().price).get(currency), currency)

    def __getAmmoTooltipArgs(self, _):
        return (self.__getAmmoItemPrice(),)

    def __getSlotTooltipArgs(self, _):
        return (self.__getSlotItemPrice(), self.hasEmptySlot)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return
        else:
            getArgsFunc = self.__tooltipIdToArgsFunc.get(tooltipId)
            if getArgsFunc is not None:
                args = getArgsFunc(event)
            else:
                args = ()
            return TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=args)

    def __addVMsInActionPriceList(self, listArray, itemPrice, addCreditsIfEmpty=True):
        for currency in reversed(Currency.ALL):
            value = itemPrice.price.get(currency)
            defValue = itemPrice.defPrice.get(currency)
            if value or defValue:
                model = ActionPriceModel()
                model.setType(currency)
                listArray.addViewModel(model)

        if addCreditsIfEmpty and not listArray:
            model = ActionPriceModel()
            model.setType(Currency.CREDITS)
            listArray.addViewModel(model)

    def _canBuyAmountOfCredits(self, neededAmount):
        return self.__shop.exchangeRate * self.__stats.money.get(Currency.GOLD) >= neededAmount

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
