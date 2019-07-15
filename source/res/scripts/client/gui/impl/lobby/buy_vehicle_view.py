# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/buy_vehicle_view.py
import logging
from collections import namedtuple
import nations
import GUI
import constants
from gui.game_control.epic_meta_game_ctrl import FRONTLINE_SCREENS
from rent_common import parseRentID
from gui import GUI_SETTINGS
from gui import SystemMessages
from gui.DialogsInterface import showI18nConfirmDialog
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.ingame_shop import showBuyGoldForVehicleWebOverlay
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORE import STORE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.framework.managers.loaders import ViewKey
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.impl.pub import ViewImpl
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.buy_vehicle_view_model import BuyVehicleViewModel
from gui.impl.gen.view_models.views.buy_vehicle_view.commander_slot_model import CommanderSlotModel
from gui.shared import event_dispatcher
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.gui_items.Tankman import CrewTypes
from skeletons.gui.app_loader import IAppLoader
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
from gui.shared.events import VehicleBuyEvent
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter, VehicleTradeInProcessor, VehicleRestoreProcessor
from helpers import i18n, dependency, int2roman, func_utils
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IRentalsController, ITradeInController, IRestoreController, IBootcampController, IWalletController, IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
from frameworks.wulf import ViewFlags, WindowFlags, ViewStatus, Window, WindowSettings

class VehicleBuyActionTypes(CONST_CONTAINER):
    DEFAULT = 0
    BUY = 1
    RESTORE = 2
    RENT = 3


_logger = logging.getLogger(__name__)
_TooltipExtraData = namedtuple('_TooltipExtraData', 'key, itemType')
_TANKMAN_KEYS = ('', 'creditsTankman', 'goldTankman')

class BuyVehicleView(ViewImpl, EventSystemEntity):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rentals = dependency.descriptor(IRentalsController)
    __tradeIn = dependency.descriptor(ITradeInController)
    __wallet = dependency.descriptor(IWalletController)
    __restore = dependency.descriptor(IRestoreController)
    __bootcamp = dependency.descriptor(IBootcampController)
    __epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __RENT_NOT_SELECTED_IDX = -2
    __RENT_UNLIM_IDX = -1
    __CREW_NOT_SELECTED_IDX = -1
    __TRADE_OFF_NOT_SELECTED = -1

    def __init__(self, *args, **kwargs):
        super(BuyVehicleView, self).__init__(R.views.lobby.shop.buy_vehicle_view.BuyVehicleView(), ViewFlags.COMPONENT, BuyVehicleViewModel, *args, **kwargs)
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
        else:
            self.__nationID = None
            self.__inNationID = None
            self.__previousAlias = ''
            self.__actionType = VehicleBuyActionTypes.DEFAULT
            self.__showOnlyCongrats = False
            self.__congratsViewSettings = {}
        self.__selectedCardIdx = 0
        self.__isWithoutCommander = False
        self.__vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        self.__tradeOffVehicle = None
        if self.__vehicle.isRestoreAvailable():
            self.__selectedRentID = self.__RENT_NOT_SELECTED_IDX
            self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
        else:
            self.__selectedRentID = self.__RENT_UNLIM_IDX
            self.__selectedRentIdx = self.__RENT_UNLIM_IDX
        self.__isGoldAutoPurhaseEnabled = isIngameShopEnabled()
        self.__isGoldAutoPurhaseEnabled &= self.__wallet.isAvailable
        self.__isRentVisible = self.__vehicle.hasRentPackages and not self.__isTradeIn()
        self.__popoverIsAvailable = True
        self.__tradeinInProgress = False
        self.__successOperation = False
        self.__purchaseInProgress = False
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
        self.__successOperation = True
        if self.__isRenting() or self.__bootcamp.isInBootcamp():
            self.__onWindowClose()
        else:
            self.__showCongratulationsView()

    def _initialize(self, *args, **kwargs):
        super(BuyVehicleView, self)._initialize()
        self._blur = GUI.WGUIBackgroundBlur()
        self._blur.enable = True
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
            vm.setCountCrew(len(self.__vehicle.crew))
            vm.setBuyVehicleIntCD(self.__vehicle.intCD)
            vm.toggleTradeInBtn.setIsVisible(self.__isTradeIn() and self.__vehicle.hasRentPackages)
            vm.setIsElite(isElite)
            vm.setIsMovingTextEnabled(constants.IS_CHINA and GUI_SETTINGS.movingText.show)
            if self.__vehicle.hasCrew:
                vm.setWithoutCommanderAltText(R.strings.store.buyVehicleWindow.crewInVehicle())
            equipmentBlock = vm.equipmentBlock
            equipmentBlock.setIsRentVisible(self.__isRentVisible)
            equipmentBlock.setTradeInIsEnabled(self.__isTradeIn())
            emtySlotAvailable = self.__itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0
            equipmentBlock.setEmtySlotAvailable(emtySlotAvailable)
            equipmentBlock.setIsRestore(isRestore)
            self.__updateToggleTradeInBtn()
            if self.__vehicle.hasRentPackages and (not isRestore or self.__actionType == VehicleBuyActionTypes.RENT) and self.__actionType != VehicleBuyActionTypes.BUY:
                self.__selectedRentIdx = 0
                self.__selectedRentID = self.__vehicle.rentPackages[self.__selectedRentIdx]['rentID']
            tankPriceArray = vm.tankPrice.getItems()
            self.__addVMsInActionPriceList(tankPriceArray, self.__vehicle.buyPrices.itemPrice, tooltipData=_TooltipExtraData(str(self.__vehicle.intCD), ACTION_TOOLTIPS_TYPE.ITEM))
            self.__updateTankPrice()
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
        self._blur.enable = False
        self._blur = None
        self.__removeListeners()
        super(BuyVehicleView, self)._finalize()
        return

    def __isTradeIn(self):
        isBuyingAllowed = not self.__vehicle.isDisabledForBuy and not self.__vehicle.isHidden
        return self.__tradeIn.isEnabled() and self.__vehicle.canTradeIn and isBuyingAllowed

    def __updateTankPrice(self):
        if self.__isRentVisible:
            if self.__selectedRentIdx == self.__RENT_NOT_SELECTED_IDX:
                self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.restore())
                defaultPrice = self.__vehicle.restorePrice
                self.__updateTankPriceModel(ItemPrice(self.__vehicle.restorePrice, defaultPrice))
            elif 0 <= self.__selectedRentIdx < len(self.__vehicle.rentPackages):
                rentPackage = self.__vehicle.rentPackages[self.__selectedRentIdx]
                self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.rent())
                self.__updateTankPriceModel(ItemPrice(rentPackage['rentPrice'], rentPackage['defaultRentPrice']))
            else:
                self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.full())
                self.__updateTankPriceModel(self.__vehicle.buyPrices.itemPrice)
        elif self.__tradeOffVehicle is not None:
            vehItemPrice = self.__vehicle.buyPrices.itemPrice
            tradeOffPrice = vehItemPrice.price - self.__tradeOffVehicle.tradeOffPrice
            tradeOffDefPrice = vehItemPrice.defPrice - self.__tradeOffVehicle.tradeOffPrice
            self.__updateTankPriceModel(ItemPrice(tradeOffPrice, tradeOffDefPrice))
            self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.tradeIn())
        elif self.viewModel.getIsRestore():
            self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.restore())
            defaultPrice = self.__vehicle.restorePrice
            self.__updateTankPriceModel(ItemPrice(self.__vehicle.restorePrice, defaultPrice))
        else:
            self.__updateTankPriceModel(self.__vehicle.buyPrices.itemPrice)
            self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.full())
        return

    def __updateTankPriceModel(self, itemPrice):
        with self.viewModel.transaction() as vm:
            for priceModel in vm.tankPrice.getItems():
                self.__updatePriceModel(priceModel, itemPrice)

    def __addListeners(self):
        self.addListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__setTradeOffVehicle)
        g_clientUpdateManager.addMoneyCallback(self.__updateIsEnoughStatus)
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onInHangarClick += self.__onInHangar
        self.viewModel.onCheckboxWithoutCrewChanged += self.__onCheckboxWithoutCrewChanged
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onCommanderLvlChange += self.__onCommanderLvlChange
        self.viewModel.toggleTradeInBtn.onClicked += self.__onToggleRentAndTradeIn
        self.viewModel.onBackClick += self.__onWindowClose
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onCancelTradeOffVehicle += self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange += self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange += self.__onSelectedChange
        self.__restore.onRestoreChangeNotify += self.__onRestoreChange
        self.__itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted

    def __removeListeners(self):
        self.removeListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__setTradeOffVehicle)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onInHangarClick -= self.__onInHangar
        self.viewModel.onCheckboxWithoutCrewChanged -= self.__onCheckboxWithoutCrewChanged
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onCommanderLvlChange -= self.__onCommanderLvlChange
        self.viewModel.toggleTradeInBtn.onClicked -= self.__onToggleRentAndTradeIn
        self.viewModel.onBackClick -= self.__onWindowClose
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onCancelTradeOffVehicle -= self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange -= self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange -= self.__onSelectedChange
        self.__restore.onRestoreChangeNotify -= self.__onRestoreChange
        self.__itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted

    def __onItemCacheSyncCompleted(self, *args):
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
        return

    def __updateSlotPrice(self):
        slotItemPrice = self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)
        with self.viewModel.equipmentBlock.slot.transaction() as slotVm:
            listArray = slotVm.actionPrices.getItems()
            isEnough = self.__getSlotIsAvailable(slotItemPrice.price)
            slotVm.setIsDisabledTooltip(self.__selectedRentIdx >= 0 and self.__isRentVisible)
            slotVm.setIsEnabled(isEnough)
            if not isEnough:
                slotVm.setIsSelected(False)
            isInit = len(listArray) == 0
            if isInit:
                self.__addVMsInActionPriceList(listArray, slotItemPrice, not self.__isGoldAutoPurhaseEnabled, tooltipData=_TooltipExtraData('slotsPrices', ACTION_TOOLTIPS_TYPE.ECONOMICS))
            else:
                self.__updateActionPriceArray(listArray, slotItemPrice)

    def __onWalletStatusChanged(self, status):
        self.__isGoldAutoPurhaseEnabled &= self.__wallet.isAvailable
        self.__updateTotalPrice()

    def __getAmmoItemPrice(self):
        ammoPrice = ITEM_PRICE_EMPTY
        for shell in self.__vehicle.gun.defaultAmmo:
            ammoPrice += shell.buyPrices.itemPrice * shell.defaultCount

        return ammoPrice

    def __updateAmmoPrice(self):
        ammoItemPrice = self.__getAmmoItemPrice()
        with self.viewModel.equipmentBlock.ammo.transaction() as ammoVm:
            isEnough = ammoItemPrice.price <= self.__stats.money
            ammoVm.setIsEnabled(isEnough)
            if not isEnough:
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
                commanderLvlModel.setIsSelected(idx == self.__selectedCardIdx)
            else:
                commanderLvlModel = listArray[idx]
            commanderLvlModel.setDiscount(commanderItemPrice.getActionPrc())
            isFree = commanderItemPrice.price <= ZERO_MONEY and commanderItemPrice.getActionPrc() == 0
            commanderLvlModel.setIsFree(isFree)
            if self.__vehicle.hasCrew:
                isEnabled = False
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

    def __setTradeOffVehicle(self, event):
        selectedVehCD = int(event.ctx)
        self.__tradeOffVehicle = self.__itemsCache.items.getItemByCD(selectedVehCD)
        if self.__tradeOffVehicle is not None:
            self.__updateTradeInInfo()
            self.__updateSlotPrice()
            self.__updateTankPrice()
            self.__updateTotalPrice()
        else:
            _logger.error('No vehicle with given id = %d', selectedVehCD)
        self.__updateBuyBtnLabel()
        return

    def __addVMsInActionPriceList(self, listArray, itemPrice, fontNotEnoughIsEnabled=True, tooltipData=None):
        actionPriceModels = getItemPricesViewModel(self.__stats.money, itemPrice)[0]
        for model in actionPriceModels:
            if tooltipData is not None:
                model.setKey(tooltipData.key)
                model.setTooltipType(tooltipData.itemType)
            listArray.addViewModel(model)
            if self.__isPurchaseCurrencyAvailable(model.getType()):
                model.setFontNotEnoughIsEnabled(fontNotEnoughIsEnabled)

        return

    def __isPurchaseCurrencyAvailable(self, currencyType):
        return currencyType == Currency.GOLD and self.__isGoldAutoPurhaseEnabled

    def __updateTradeInInfo(self):
        self.__updateTradeOffVehicleIntCD()
        with self.viewModel.transaction() as vm:
            vm.equipmentBlock.setBuyVehicleIntCD(self.__vehicle.intCD)
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
            if self.__tradeOffVehicle is not None and not self.__isRentVisible:
                vm.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
                vm.equipmentBlock.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
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
            self.__updateTankPrice()

    def __updateTradeOffVehicleBtnData(self):
        with self.viewModel.equipmentBlock.vehicleBtn.transaction() as vehicleBtnVm:
            isTradeIn = not self.__isRentVisible and self.__isTradeIn()
            vehicleBtnVm.setVisible(isTradeIn and self.__tradeOffVehicle is not None)
            if self.__tradeOffVehicle is not None:
                vehicleBtnVm.setFlag(self.__tradeOffVehicle.nationName)
                vehicleBtnVm.setVehType(getTypeSmallIconPath(self.__tradeOffVehicle.type, self.__tradeOffVehicle.isPremium))
                vehicleBtnVm.setVehLvl(getLevelSmallIconPath(self.__tradeOffVehicle.level))
                vehicleBtnVm.setVehIcon(getSmallIconPath(self.__tradeOffVehicle.name))
                vehicleBtnVm.setVehName(self.__tradeOffVehicle.shortUserName)
        return

    def __onTradeInConfirmed(self, event):
        self.__requestForMoneyObtain()

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
        self.__updateTankPrice()
        self.__updateRentInfo()
        self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        self.__updateSlotPrice()
        self.viewModel.commit()

    def __updateIsEnoughStatus(self, *args):
        if not self.__vehicle.isRented:
            with self.viewModel.transaction() as vm:
                ammoPriceModel = vm.equipmentBlock.ammo.actionPrices.getItems()
                ammoPrice = self.__getAmmoItemPrice()
                self.__updateActionPriceArray(ammoPriceModel, self.__getAmmoItemPrice())
                ammoIsAvailable = self.__isAvailablePrice(ammoPrice.price)
                slotPriceModel = vm.equipmentBlock.slot.actionPrices.getItems()
                slotItemPrice = self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)
                self.__updateActionPriceArray(slotPriceModel, slotItemPrice)
                equipmentBlock = vm.equipmentBlock
                equipmentBlock.ammo.setIsEnabled(ammoIsAvailable)
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

    def __getSlotIsAvailable(self, slotPrice):
        isSlotForRent = self.__selectedRentIdx >= 0 and self.__isRentVisible
        isSlotForTradeIn = self.__tradeOffVehicle is not None and not self.__isRentVisible
        return not isSlotForRent and not isSlotForTradeIn and self.__isAvailablePrice(slotPrice)

    def __isAvailablePrice(self, money):
        isPurchaseCurrencyAvailable = money.isDefined()
        statsMoney = self.__stats.money
        for currency in Currency.ALL:
            currencyValue = money.get(currency)
            if currencyValue and currencyValue > statsMoney.get(currency):
                isPurchaseCurrencyAvailable &= self.__isPurchaseCurrencyAvailable(currency)

        return self.__stats.money >= money or isPurchaseCurrencyAvailable

    def __getTotalItemPrice(self):
        result = ZERO_MONEY
        if self.__selectedRentIdx >= 0 and self.__isRentVisible:
            result += self.__vehicle.rentPackages[self.__selectedRentIdx]['rentPrice']
        elif self.viewModel.getIsRestore():
            result += self.__vehicle.restorePrice
        else:
            result += self.__vehicle.buyPrices.itemPrice.price
        if not self.__isWithoutCommander:
            comanderCardsPrices = self.__shop.getTankmanCostItemPrices()
            commanderItemPrice = comanderCardsPrices[self.__selectedCardIdx]
            commanderItemPrice *= len(self.__vehicle.crew)
            result += commanderItemPrice.price
        if self.viewModel.equipmentBlock.slot.getIsSelected():
            vehSlots = self.__stats.vehicleSlots
            result += self.__shop.getVehicleSlotsItemPrice(vehSlots).price
        if self.viewModel.equipmentBlock.ammo.getIsSelected():
            result += self.__getAmmoItemPrice().price
        if self.__tradeOffVehicle is not None and not self.__isRentVisible:
            result -= self.__tradeOffVehicle.tradeOffPrice
        return ItemPrice(price=result, defPrice=result)

    def __updateTotalPrice(self):
        totalPirce = self.__getTotalItemPrice()
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockVm:
            if self.__tradeOffVehicle is not None:
                equipmentBlockVm.setConfirmGoldPrice(totalPirce.price.get(Currency.GOLD))
                popoverIsAvailable = totalPirce.price.get(Currency.GOLD) <= self.__stats.money.get(Currency.GOLD)
                self.__popoverIsAvailable = popoverIsAvailable
                equipmentBlockVm.setPopoverIsAvailable(popoverIsAvailable and not self.__isRentVisible)
            totalPriceArray = equipmentBlockVm.totalPrice.getItems()
            for model in totalPriceArray:
                statsMoney = self.__stats.money
                currencyType = model.getType()
                currencyValue = totalPirce.price.get(currencyType)
                model.setPrice(self.gui.systemLocale.getNumberFormat(currencyValue))
                if not self.__isPurchaseCurrencyAvailable(currencyType):
                    model.setIsEnough(currencyValue <= statsMoney.get(currencyType))

            self.__updateBuyBtnStatus(totalPirce)
        return

    def __updateBuyBtnStatus(self, totalPirce):
        totalPriceMoney = totalPirce.price
        statsMoney = self.__stats.money
        isEnabled = True
        for currency in Currency.ALL:
            if not self.__isPurchaseCurrencyAvailable(currency):
                isEnabled &= totalPriceMoney.get(currency) <= statsMoney.get(currency)

        self.viewModel.equipmentBlock.setBuyBtnIsEnabled(isEnabled)

    def __onWindowClose(self, *args):
        self.__showHangar()
        self.__destroyWindow()

    def __destroyWindow(self):
        self.viewModel.congratulationAnim.setResetAnimTrgigger(True)
        self.destroyWindow()

    def __showHangar(self):
        if not self.__bootcamp.isInBootcamp() and self.__successOperation:
            if self.__previousAlias in (VIEW_ALIAS.VEHICLE_PREVIEW, VIEW_ALIAS.VEHICLE_PREVIEW_20):
                event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
            elif self.__previousAlias == VIEW_ALIAS.FRONTLINE_VEHICLE_PREVIEW_20:
                self.__epicCtrl.showCustomScreen(FRONTLINE_SCREENS.REWARDS_SCREEN)

    def __updateToggleTradeInBtn(self):
        with self.viewModel.toggleTradeInBtn.transaction() as toggleTradeInBtnVm:
            toggleTradeInBtnVm.setIcon(R.images.gui.maps.icons.library.trade_in() if self.__isRentVisible else R.images.gui.maps.icons.library.rent_ico_big())
            toggleTradeInBtnVm.setLabel(R.strings.store.buyVehicleWindow.toggleBtn.rent() if self.__isRentVisible else R.strings.store.buyVehicleWindow.toggleBtn.buy())
            toggleTradeInBtnVm.setIsRent(self.__isRentVisible)

    def __onInHangar(self, *args):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.__destroyWindow()

    def __onCheckboxWithoutCrewChanged(self, args):
        self.__isWithoutCommander = args['selected']
        with self.viewModel.transaction() as vm:
            cardVMs = vm.commanderLvlCards.getItems()
            for vm in cardVMs:
                vm.setSlotIsEnabled(not self.__isWithoutCommander)

            if not self.__isWithoutCommander:
                self.__updateIsEnoughStatus()
        self.__updateTotalPrice()

    def __onBuyBtnClick(self):
        if self.__tradeinInProgress:
            return
        if self.viewModel.getIsContentHidden():
            self.__onInHangar()
            return
        totalPrice = self.__getTotalItemPrice().price
        if self.__isAvailablePrice(totalPrice):
            availableGold = self.__stats.money.gold
            requiredGold = totalPrice.gold
            if availableGold < requiredGold:
                showBuyGoldForVehicleWebOverlay(requiredGold, self.__vehicle.intCD)
                return
        self.__requestForMoneyObtain()

    def __onSelectedChange(self, args):
        self.__updateTotalPrice()

    def __onCommanderLvlChange(self, args):
        cardModels = self.viewModel.commanderLvlCards.getItems()
        cardModels[self.__selectedCardIdx].setIsSelected(False)
        self.__selectedCardIdx = int(args['value'])
        cardModels[self.__selectedCardIdx].setIsSelected(True)
        self.__updateTotalPrice()

    def __onToggleRentAndTradeIn(self):
        self.__isRentVisible = not self.__isRentVisible
        self.__updateToggleTradeInBtn()
        self.__updateTradeOffVehicleIntCD()
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockVm:
            equipmentBlockVm.vehicleTradeInBtn.setIsVisible(not self.__isRentVisible and self.__tradeOffVehicle is None)
            equipmentBlockVm.vehicleBtn.setVisible(not self.__isRentVisible and self.__tradeOffVehicle is not None)
            equipmentBlockVm.vehicleRentBtn.setIsVisible(self.__isRentVisible)
            equipmentBlockVm.setIsRentVisible(self.__isRentVisible)
            if self.__isRentVisible:
                equipmentBlockVm.setPopoverIsAvailable(False)
            else:
                equipmentBlockVm.setPopoverIsAvailable(self.__popoverIsAvailable)
            self.__updateSlotPrice()
            self.__updateTankPrice()
            self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        return

    def __onCancelTradeOffVehicle(self, *args):
        self.__tradeOffVehicle = None
        self.__updateTradeInInfo()
        self.__updateTotalPrice()
        self.__updateTankPrice()
        self.__updateSlotPrice()
        self.__updateBuyBtnLabel()
        return

    def __isToggleRentAndTradeInState(self):
        return False if not self.__vehicle else self.__isTradeIn() and self.__vehicle.hasRentPackages

    @decorators.process('buyItem')
    def __requestForMoneyObtain(self):
        equipmentBlock = self.viewModel.equipmentBlock
        isTradeIn = self.__tradeOffVehicle is not None and not self.__isRentVisible
        isWithSlot = equipmentBlock.slot.getIsSelected()
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        if self.__isWithoutCommander:
            crewType = self.__CREW_NOT_SELECTED_IDX
        else:
            crewType = self.__selectedCardIdx
        result = None
        if isTradeIn:
            confirmationType = 'tradeInConfirmation'
            addition = ''
            operations = []
            if self.__tradeOffVehicle.hasCrew:
                operations.append('crew')
            if self.__tradeOffVehicle.hasShells:
                operations.append('shells')
            if self.__tradeOffVehicle.hasEquipments:
                operations.append('equipments')
            if self.__tradeOffVehicle.hasOptionalDevices:
                operations.append('optionalDevices')
            if operations:
                operationsStr = [ i18n.makeString('#dialogs:%s/message/%s' % (confirmationType, o)) for o in operations ]
                addition = i18n.makeString('#dialogs:%s/message/addition' % confirmationType, operations=', '.join(operationsStr))
            ctx = {'vehName': neutral(self.__tradeOffVehicle.userName),
             'addition': addition}
            self.__tradeinInProgress = True
            result = yield showI18nConfirmDialog(confirmationType, meta=I18nConfirmDialogMeta(confirmationType, ctx, ctx), focusedID=DIALOG_BUTTON_ID.SUBMIT)
            if not result:
                return
            result = yield VehicleTradeInProcessor(self.__vehicle, self.__tradeOffVehicle, isWithSlot, isWithAmmo, crewType).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self.__tradeinInProgress = False
            if not result.success:
                self.__onWindowClose()
                return
        if isWithSlot:
            result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success:
                return
        if not isTradeIn:
            self.__purchaseInProgress = True
            emtySlotAvailable = self.__itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0
            if self.__isBuying():
                if self.viewModel.getIsRestore():
                    result = yield self.getRestoreVehicleProcessor(crewType).request()
                else:
                    result = yield self.__getObtainVehicleProcessor(crewType).request()
                if not emtySlotAvailable and not isWithSlot:
                    self.__playSlotAnimation()
            else:
                result = yield VehicleRenter(self.__vehicle, self.__selectedRentID, isWithAmmo, crewType).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self.__purchaseInProgress = False
            self.__onItemCacheSyncCompleted()
        if result and result.success:
            self.showCongratulations()
        return

    def __isBuying(self):
        return self.__selectedRentIdx in (self.__RENT_UNLIM_IDX, self.__RENT_NOT_SELECTED_IDX) or not self.__isRentVisible

    def __isRenting(self):
        return not self.__isBuying()

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
                vm.setVehicleType(vehicleType)
                vm.setLvl(int2roman(self.__vehicle.level))
                vm.setVName(self.__vehicle.userName)
                vm.setImage(image if image is not None else defaultImage)
                vm.setImageAlt(defaultImage)
                vm.setTitle(R.strings.store.congratulationAnim.restoreLabel() if self.viewModel.getIsRestore() else R.strings.store.congratulationAnim.buyingLabel())
                vm.setBtnLbl(R.strings.store.congratulationAnim.showPreviewBtnLabel())
            return

    def __getObtainVehicleProcessor(self, crewType):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleBuyer(self.__vehicle, isWithSlot, isWithAmmo, crewType)

    def __updateBuyBtnLabel(self):
        if self.__selectedRentIdx == self.__RENT_NOT_SELECTED_IDX:
            label = R.strings.store.buyVehicleWindow.restore()
        elif self.__tradeOffVehicle is not None and not self.__isRentVisible:
            label = R.strings.store.buyVehicleWindow.exchange()
        elif self.__selectedRentID >= 0:
            label = R.strings.store.buyVehicleWindow.rentBtn()
        else:
            label = R.strings.store.buyVehicleWindow.buyBtn()
        self.viewModel.equipmentBlock.setBuyBtnLabel(label)
        return

    def getRestoreVehicleProcessor(self, crewType):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleRestoreProcessor(self.__vehicle, isWithSlot, isWithAmmo, crewType)

    def __onRestoreChange(self, _):
        vehicle = self.__itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        if vehicle and not vehicle.isRestoreAvailable():
            self.__onWindowClose()
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.VEHICLE_RESTORE_FINISHED, vehicleName=vehicle.userName)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return
        else:
            if tooltipId == TOOLTIPS_CONSTANTS.TRADE_IN_PRICE:
                args = (self.__vehicle.intCD, self.__tradeOffVehicle.intCD)
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


class BuyVehicleWindow(Window):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        app = self.appLoader.getApp()
        view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
        if view is not None:
            parent = view.getParentWindow()
        else:
            parent = None
        settings = WindowSettings()
        settings.flags = WindowFlags.DIALOG
        settings.content = BuyVehicleView(*args, **kwargs)
        settings.parent = parent
        super(BuyVehicleWindow, self).__init__(settings)
        return

    def showCongratulations(self):
        self.content.showCongratulations()
