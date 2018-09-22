# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/buy_vehicle_view.py
import logging
import BigWorld
import nations
import GUI
from gui import SystemMessages
import constants
from gui import GUI_SETTINGS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.impl.pub import ViewImpl
from gui.DialogsInterface import showI18nConfirmDialog
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from frameworks.wulf import ViewFlags, WindowFlags, ViewStatus, Window
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.buy_vehicle_view_model import BuyVehicleViewModel
from gui.shared import event_dispatcher
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent
from gui.ingame_shop import showBuyGoldForVehicleWebOverlay
from gui.shared.gui_items.Tankman import CrewTypes
from helpers import i18n, dependency, int2roman
from skeletons.gui.game_control import IRentalsController, ITradeInController, IRestoreController, IBootcampController, IWalletController
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import ZERO_MONEY
from gui.Scaleform.locale.STORE import STORE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.gui_items.Vehicle import getTypeUserName, getSmallIconPath, getLevelSmallIconPath, getTypeSmallIconPath
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.formatters import getItemPricesViewModel, updateActionInViewModel
from gui.shared.formatters.text_styles import neutral
from gui.impl.gen.view_models.views.buy_vehicle_view.commander_slot_model import CommanderSlotModel
from gui.shared.money import Currency, Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.utils import decorators
from gui.shared.events import VehicleBuyEvent
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter, VehicleTradeInProcessor, VehicleRestoreProcessor
from gui.app_loader import g_appLoader
from gui.Scaleform.framework.managers.loaders import ViewKey
_logger = logging.getLogger(__name__)

class BuyVehicleView(ViewImpl, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)
    rentals = dependency.descriptor(IRentalsController)
    tradeIn = dependency.descriptor(ITradeInController)
    wallet = dependency.descriptor(IWalletController)
    restore = dependency.descriptor(IRestoreController)
    bootcamp = dependency.descriptor(IBootcampController)
    __RENT_NOT_SELECTED_IDX = -2
    __RENT_UNLIM_IDX = -1
    __CREW_NOT_SELECTED_IDX = -1
    __TRADE_OFF_NOT_SELECTED = -1

    def __init__(self, *args, **kwargs):
        super(BuyVehicleView, self).__init__(R.views.buyVehicleView, ViewFlags.COMPONENT, BuyVehicleViewModel, *args, **kwargs)
        self.__shop = self.itemsCache.items.shop
        self.__stats = self.itemsCache.items.stats
        ctx = kwargs['ctx']
        if ctx is not None:
            self.__nationID = ctx.get('nationID')
            self.__inNationID = ctx.get('itemID')
            self.__previousAlias = ctx.get('previousAlias')
        else:
            self.__nationID = None
            self.__inNationID = None
            self.__previousAlias = ''
        self.__selectedCardIdx = 0
        self.__isWithoutCommander = False
        self.__vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        self.__tradeOffVehicle = None
        self.__selectedRentTerm = self.__RENT_NOT_SELECTED_IDX
        if self.__vehicle.isRestoreAvailable():
            self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
        else:
            self.__selectedRentIdx = self.__RENT_UNLIM_IDX
        self.__isGoldAutoPurhaseEnabled = isIngameShopEnabled()
        self.__isGoldAutoPurhaseEnabled &= self.wallet.isAvailable
        self.__isRentVisible = self.__vehicle.hasRentPackages and not self.__isTradeIn()
        self.__popoverIsAvailable = True
        self.__tradeinInProgress = False
        self.__successOperation = False
        self.__purchaseInProgress = False
        return

    @property
    def viewModel(self):
        return super(BuyVehicleView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(BuyVehicleView, self)._initialize()
        self._blur = GUI.WGUIBackgroundBlur()
        self._blur.enable = True
        self.__addListeners()
        isElite = self.__vehicle.isElite
        vehType = self.__vehicle.type.replace('-', '_')
        isRestoreAvailable = self.__vehicle.isRestoreAvailable()
        with self.viewModel.transaction() as model:
            model.setTankType('{}_elite'.format(vehType) if isElite else vehType)
            vehicleTooltip = i18n.makeString(getTypeUserName(self.__vehicle.type, isElite))
            noCrewLabelPath = R.strings.store.buyVehicleWindow.checkBox
            model.setVehicleNameTooltip(vehicleTooltip)
            model.setNation(nations.NAMES[self.__vehicle.nationID])
            model.setNoCrewCheckboxLabel(noCrewLabelPath.restore.withoutCrew if isRestoreAvailable else noCrewLabelPath.buy.withoutCrew)
            model.setTankLvl(int2roman(self.__vehicle.level))
            model.setTankName(self.__vehicle.shortUserName)
            model.setCountCrew(len(self.__vehicle.crew))
            model.setBuyVehicleIntCD(self.__vehicle.intCD)
            model.setIsToggleBtnVisible(self.__isTradeIn() and self.__vehicle.hasRentPackages)
            model.setIsElite(isElite)
            model.setIsRentVisible(self.__isRentVisible)
            model.setIsInBootcamp(self.__isBootcampBuyVehicle())
            model.setIsMovingTextEnabled(constants.IS_CHINA and GUI_SETTINGS.movingText.show)
            if self.__vehicle.hasCrew:
                model.setWithoutCommanderAltText(R.strings.store.buyVehicleWindow.crewInVehicle)
            equipmentBlock = model.equipmentBlock
            equipmentBlock.setIsRentVisible(self.__isRentVisible)
            equipmentBlock.setTradeInIsEnabled(self.__isTradeIn())
            emtySlotAvailable = self.itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0
            equipmentBlock.setEmtySlotAvailable(emtySlotAvailable)
            equipmentBlock.setIsRestore(isRestoreAvailable)
            if self.__vehicle.hasRentPackages and not isRestoreAvailable:
                self.__selectedRentIdx = 0
                self.__selectedRentTerm = self.__vehicle.rentPackages[self.__selectedRentIdx]['days']
            tankPriceArray = model.tankPrice.getItems()
            self.__addVMsInActionPriceList(tankPriceArray, self.__vehicle.buyPrices.itemPrice)
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

    def __isBootcampBuyVehicle(self):
        commanderLvlsCost = self.__shop.getTankmanCostItemPrices()
        lastItemDiscount = commanderLvlsCost.pop().getActionPrc()
        return self.bootcamp.isInBootcamp() and lastItemDiscount == 100

    def __isTradeIn(self):
        isBuyingAllowed = not self.__vehicle.isDisabledForBuy and not self.__vehicle.isHidden
        return self.tradeIn.isEnabled() and self.__vehicle.canTradeIn and isBuyingAllowed

    def __updateTankPrice(self):
        if self.__isRentVisible:
            if self.__selectedRentIdx == self.__RENT_NOT_SELECTED_IDX:
                self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.restore)
                defaultPrice = self.__vehicle.restorePrice
                self.__updateTankPriceModel(ItemPrice(self.__vehicle.restorePrice, defaultPrice))
            elif self.__selectedRentIdx == self.__RENT_UNLIM_IDX:
                self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.full)
                self.__updateTankPriceModel(self.__vehicle.buyPrices.itemPrice)
            else:
                rentPackage = self.__vehicle.rentPackages[self.__selectedRentIdx]
                self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.rent)
                self.__updateTankPriceModel(ItemPrice(rentPackage['rentPrice'], rentPackage['defaultRentPrice']))
        elif self.__tradeOffVehicle is not None:
            vehItemPrice = self.__vehicle.buyPrices.itemPrice
            tradeOffPrice = vehItemPrice.price - self.__tradeOffVehicle.tradeOffPrice
            tradeOffDefPrice = vehItemPrice.defPrice - self.__tradeOffVehicle.tradeOffPrice
            self.__updateTankPriceModel(ItemPrice(tradeOffPrice, tradeOffDefPrice))
            self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.tradeIn)
        elif self.__vehicle.isRestoreAvailable():
            self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.restore)
            defaultPrice = self.__vehicle.restorePrice
            self.__updateTankPriceModel(ItemPrice(self.__vehicle.restorePrice, defaultPrice))
        else:
            self.__updateTankPriceModel(self.__vehicle.buyPrices.itemPrice)
            self.viewModel.setPriceDescription(R.strings.store.buyVehicleWindow.priceDescription.full)
        return

    def __updateTankPriceModel(self, itemPrice):
        with self.viewModel.transaction() as model:
            for priceModel in model.tankPrice.getItems():
                self.__updatePriceModel(priceModel, itemPrice)

    def __addListeners(self):
        self.addListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__setTradeOffVehicle)
        g_clientUpdateManager.addMoneyCallback(self.__updateIsEnoughStatus)
        self.wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onShowInHangarClick += self.__onShowInHangar
        self.viewModel.onCheckboxWithoutCrewChanged += self.__onCheckboxWithoutCrewChanged
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onCommanderLvlChange += self.__onCommanderLvlChange
        self.viewModel.onToggleRentAndTradeIn += self.__onToggleRentAndTradeIn
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onCancelTradeOffVehicle += self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange += self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange += self.__onSelectedChange
        self.restore.onRestoreChangeNotify += self.__onRestoreChange
        self.itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted

    def __removeListeners(self):
        self.removeListener(ShopEvent.CONFIRM_TRADE_IN, self.__onTradeInConfirmed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(ShopEvent.SELECT_RENT_TERM, self.__onRentTermSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__setTradeOffVehicle)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onShowInHangarClick -= self.__onShowInHangar
        self.viewModel.onCheckboxWithoutCrewChanged -= self.__onCheckboxWithoutCrewChanged
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onCommanderLvlChange -= self.__onCommanderLvlChange
        self.viewModel.onToggleRentAndTradeIn -= self.__onToggleRentAndTradeIn
        equipmentBlock = self.viewModel.equipmentBlock
        equipmentBlock.onCancelTradeOffVehicle -= self.__onCancelTradeOffVehicle
        equipmentBlock.slot.onSelectedChange -= self.__onSelectedChange
        equipmentBlock.ammo.onSelectedChange -= self.__onSelectedChange
        self.restore.onRestoreChangeNotify -= self.__onRestoreChange
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted

    def __onItemCacheSyncCompleted(self, *args):
        if self.__purchaseInProgress or self.viewModel is None or self.viewModel.proxy is None:
            return
        else:
            self.__vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
            self.__shop = self.itemsCache.items.shop
            self.__stats = self.itemsCache.items.stats
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
        wgGetIntegralFormat = BigWorld.wg_getIntegralFormat
        statsMoney = self.__stats.money
        price = itemPrice.price
        defPrice = itemPrice.defPrice
        currencyType = priceModel.getType()
        currencyValue = price.get(currencyType)
        if currencyValue is not None:
            priceModel.setPrice(wgGetIntegralFormat(currencyValue))
            priceModel.setDefPrice(wgGetIntegralFormat(defPrice.get(currencyType)))
        else:
            for currencyType in Currency.ALL:
                currencyValue = price.get(currencyType)
                if currencyValue:
                    priceModel.setType(currencyType)
                    priceModel.setPrice(BigWorld.wg_getIntegralFormat(currencyValue))
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
        with self.viewModel.equipmentBlock.slot.transaction() as slotModel:
            listArray = slotModel.actionPrices.getItems()
            if self.__isBootcampBuyVehicle():
                slotModel.setIsBtnEnabled(False)
            else:
                isEnough = self.__getSlotIsAvailable(slotItemPrice.price)
                if self.__selectedRentIdx >= 0 and self.__isRentVisible:
                    slotModel.setDisabledTooltip(DIALOGS.BUYVEHICLEWINDOW_FREERENTSLOT)
                else:
                    slotModel.setDisabledTooltip('')
                slotModel.setIsBtnEnabled(isEnough)
                if not isEnough:
                    slotModel.setIsSelected(False)
            isInit = len(listArray) == 0
            if isInit:
                self.__addVMsInActionPriceList(listArray, slotItemPrice, not self.__isGoldAutoPurhaseEnabled)
            else:
                self.__updateActionPriceArray(listArray, slotItemPrice)

    def __onWalletStatusChanged(self, status):
        self.__isGoldAutoPurhaseEnabled &= self.wallet.isAvailable
        self.__updateTotalPrice()

    def __getAmmoItemPrice(self):
        ammoPrice = ITEM_PRICE_EMPTY
        for shell in self.__vehicle.gun.defaultAmmo:
            ammoPrice += shell.buyPrices.itemPrice * shell.defaultCount

        return ammoPrice

    def __updateAmmoPrice(self):
        ammoItemPrice = self.__getAmmoItemPrice()
        with self.viewModel.equipmentBlock.ammo.transaction() as ammoModel:
            isEnough = ammoItemPrice.price <= self.__stats.money
            if self.__isBootcampBuyVehicle():
                ammoModel.setIsBtnEnabled(False)
            else:
                ammoModel.setIsBtnEnabled(isEnough)
            if not isEnough:
                ammoModel.setIsSelected(False)
            listArray = ammoModel.actionPrices.getItems()
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
                if not self.__isBootcampBuyVehicle():
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
            if self.__isBootcampBuyVehicle():
                if commanderLvlPercents[idx] == CrewTypes.SKILL_100:
                    commanderLvlModel.setShowBootcampAnim(self.bootcamp.isInBootcamp())
                    self.__selectedCardIdx = idx
                    isEnabled = True
                else:
                    isEnabled = False
            commanderLvlModel.setSlotIsEnabled(isEnabled and not self.__isWithoutCommander)
            commanderActionPriceArray = commanderLvlModel.actionPrice.getItems()
            if isInit:
                self.__addVMsInActionPriceList(commanderActionPriceArray, commanderItemPrice, not isEnabled)
                listArray.addViewModel(commanderLvlModel)
            self.__updateActionPriceArray(commanderActionPriceArray, commanderItemPrice)

    def __setTradeOffVehicle(self, event):
        selectedVehCD = int(event.ctx)
        self.__tradeOffVehicle = self.itemsCache.items.getItemByCD(selectedVehCD)
        if self.__tradeOffVehicle is not None:
            self.__updateTradeInInfo()
            self.__updateTotalPrice()
            self.__updateTankPrice()
            self.__updateSlotPrice()
        else:
            _logger.error('No vehicle with given id = %d', selectedVehCD)
        self.__updateBuyBtnLabel()
        return

    def __addVMsInActionPriceList(self, listArray, itemPrice, fontNotEnoughIsEnabled=True):
        actionPriceModels = getItemPricesViewModel(self.__stats.money, itemPrice)[0]
        for model in actionPriceModels:
            listArray.addViewModel(model)
            if self.__isPurchaseCurrencyAvailable(model.getType()):
                model.setFontNotEnoughIsEnabled(fontNotEnoughIsEnabled)

    def __isPurchaseCurrencyAvailable(self, currencyType):
        return currencyType == Currency.GOLD and self.__isGoldAutoPurhaseEnabled

    def __updateTradeInInfo(self):
        with self.viewModel.transaction() as model:
            model.equipmentBlock.setBuyVehicleIntCD(self.__vehicle.intCD)
            if self.__tradeOffVehicle is not None:
                model.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
                model.equipmentBlock.setTradeOffVehicleIntCD(self.__tradeOffVehicle.intCD)
            else:
                model.setTradeOffVehicleIntCD(self.__TRADE_OFF_NOT_SELECTED)
                model.equipmentBlock.setTradeOffVehicleIntCD(self.__TRADE_OFF_NOT_SELECTED)
            with model.equipmentBlock.vehicleTradeInBtn.transaction() as vehicleTradeInBtnModel:
                if self.__isTradeIn():
                    vehicleTradeInBtnModel.setImage(R.images.gui.maps.icons.library.trade_in)
                    vehicleTradeInBtnModel.setText(STORE.BUYVEHICLEWINDOW_TRADEINBTNLABEL)
                isTradeIn = not self.__isRentVisible and self.__isTradeIn()
                vehicleTradeInBtnModel.setVisible(isTradeIn and self.__tradeOffVehicle is None)
            self.__updateTradeOffVehicleBtnData()
        return

    def __updateRentInfo(self):
        with self.viewModel.equipmentBlock.transaction() as equipmentBlock:
            equipmentBlock.setSelectedRentTerm(self.__selectedRentTerm)
            with equipmentBlock.vehicleRentBtn.transaction() as vehicleRentBtnModel:
                if self.__vehicle.hasRentPackages:
                    vehicleRentBtnModel.setImage(R.images.gui.maps.icons.library.rent_ico_big)
                rentBtnAvailable = self.__isToggleRentAndTradeInState() and self.__isRentVisible
                rentBtnAvailable |= not self.__isToggleRentAndTradeInState() and self.__vehicle.hasRentPackages
                vehicleRentBtnModel.setVisible(rentBtnAvailable)
            self.__updateTankPrice()

    def __updateTradeOffVehicleBtnData(self):
        with self.viewModel.equipmentBlock.vehicleBtn.transaction() as vehicleBtnModel:
            isTradeIn = not self.__isRentVisible and self.__isTradeIn()
            vehicleBtnModel.setVisible(isTradeIn and self.__tradeOffVehicle is not None)
            if self.__tradeOffVehicle is not None:
                vehicleBtnModel.setFlag(self.__tradeOffVehicle.nationName)
                vehicleBtnModel.setVehType(getTypeSmallIconPath(self.__tradeOffVehicle.type, self.__tradeOffVehicle.isPremium))
                vehicleBtnModel.setVehLvl(getLevelSmallIconPath(self.__tradeOffVehicle.level))
                vehicleBtnModel.setVehIcon(getSmallIconPath(self.__tradeOffVehicle.name))
                vehicleBtnModel.setVehName(self.__tradeOffVehicle.shortUserName)
        return

    def __onTradeInConfirmed(self, event):
        self.__requestForMoneyObtain()

    def __onRentTermSelected(self, event):
        itemIdx = event.ctx
        self.__selectedRentIdx = itemIdx
        if self.__selectedRentIdx == self.__RENT_UNLIM_IDX:
            if self.__vehicle.isRestoreAvailable():
                self.__selectedRentIdx = self.__RENT_NOT_SELECTED_IDX
                self.__selectedRentTerm = self.__RENT_NOT_SELECTED_IDX
            else:
                self.__selectedRentTerm = self.__selectedRentIdx
        else:
            self.__selectedRentTerm = self.__vehicle.rentPackages[self.__selectedRentIdx]['days']
        self.viewModel.hold()
        self.__updateTankPrice()
        self.__updateRentInfo()
        self.__updateTotalPrice()
        self.__updateBuyBtnLabel()
        self.__updateSlotPrice()
        self.viewModel.commit()

    def __updateIsEnoughStatus(self, *args):
        if not self.__vehicle.isRented:
            with self.viewModel.transaction() as model:
                ammoPriceModel = model.equipmentBlock.ammo.actionPrices.getItems()
                ammoPrice = self.__getAmmoItemPrice()
                self.__updateActionPriceArray(ammoPriceModel, self.__getAmmoItemPrice())
                ammoIsAvailable = self.__isAvailablePrice(ammoPrice.price)
                slotPriceModel = model.equipmentBlock.slot.actionPrices.getItems()
                slotItemPrice = self.__shop.getVehicleSlotsItemPrice(self.__stats.vehicleSlots)
                self.__updateActionPriceArray(slotPriceModel, slotItemPrice)
                equipmentBlock = model.equipmentBlock
                equipmentBlock.ammo.setIsBtnEnabled(ammoIsAvailable)
                equipmentBlock.slot.setIsBtnEnabled(self.__getSlotIsAvailable(slotItemPrice.price))
                idx = 0
                commanderCards = model.commanderLvlCards.getItems()
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
        elif self.__vehicle.isRestoreAvailable():
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
        with self.viewModel.equipmentBlock.transaction() as equipmentBlockModel:
            if self.__tradeOffVehicle is not None:
                equipmentBlockModel.setConfirmGoldPrice(totalPirce.price.get(Currency.GOLD))
                popoverIsAvailable = totalPirce.price.get(Currency.GOLD) <= self.__stats.money.get(Currency.GOLD)
                self.__popoverIsAvailable = popoverIsAvailable
                equipmentBlockModel.setPopoverIsAvailable(popoverIsAvailable and not self.__isRentVisible)
            totalPriceArray = equipmentBlockModel.totalPrice.getItems()
            for model in totalPriceArray:
                statsMoney = self.__stats.money
                currencyType = model.getType()
                currencyValue = totalPirce.price.get(currencyType)
                model.setPrice(BigWorld.wg_getIntegralFormat(currencyValue))
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

        if self.__isBootcampBuyVehicle():
            self.viewModel.equipmentBlock.setBuyBtnIsEnabled(False)
        else:
            self.viewModel.equipmentBlock.setBuyBtnIsEnabled(isEnabled)

    def __onWindowClose(self, *args):
        self.__showHangar()
        self.__destroyWindow()

    def __destroyWindow(self):
        window = self.getParentWindow()
        if window is not None:
            window.destroy()
        else:
            self.destroy()
        return

    def __showHangar(self):
        if not self.bootcamp.isInBootcamp() and self.__successOperation and self.__previousAlias in (VIEW_ALIAS.VEHICLE_PREVIEW, VIEW_ALIAS.VEHICLE_PREVIEW_20):
            event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)

    def __onShowInHangar(self, *args):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.__destroyWindow()

    def __onCheckboxWithoutCrewChanged(self, args):
        self.__isWithoutCommander = args['value']
        with self.viewModel.transaction() as model:
            cardModels = model.commanderLvlCards.getItems()
            for model in cardModels:
                model.setSlotIsEnabled(not self.__isWithoutCommander)

            if not self.__isWithoutCommander:
                self.__updateIsEnoughStatus()
        self.__updateTotalPrice()

    def __onBuyBtnClick(self):
        if self.__tradeinInProgress:
            return
        if self.viewModel.getIsContentHidden():
            self.__onShowInHangar()
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
        if self.__isBootcampBuyVehicle():
            self.viewModel.equipmentBlock.setBuyBtnIsEnabled(True)
            self.viewModel.equipmentBlock.setShowBuyBootcampAnim(True)

    def __onToggleRentAndTradeIn(self, args):
        self.__isRentVisible = not self.__isRentVisible
        self.viewModel.setIsRentVisible(self.__isRentVisible)
        with self.viewModel.equipmentBlock.transaction() as equipmentBlock:
            equipmentBlock.vehicleTradeInBtn.setVisible(not self.__isRentVisible and self.__tradeOffVehicle is None)
            equipmentBlock.vehicleBtn.setVisible(not self.__isRentVisible and self.__tradeOffVehicle is not None)
            equipmentBlock.vehicleRentBtn.setVisible(self.__isRentVisible)
            equipmentBlock.setIsRentVisible(self.__isRentVisible)
            if self.__isRentVisible:
                equipmentBlock.setPopoverIsAvailable(False)
            else:
                equipmentBlock.setPopoverIsAvailable(self.__popoverIsAvailable)
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
        isRestore = self.__vehicle.isRestoreAvailable()
        if not isTradeIn:
            self.__purchaseInProgress = True
            emtySlotAvailable = self.itemsCache.items.inventory.getFreeSlots(self.__stats.vehicleSlots) > 0
            if self.__isBuying():
                if isRestore:
                    result = yield self.getRestoreVehicleProcessor(crewType).request()
                else:
                    result = yield self.__getObtainVehicleProcessor(crewType).request()
                if not emtySlotAvailable and not isWithSlot:
                    self.__playSlotAnimation()
            else:
                result = yield VehicleRenter(self.__vehicle, self.__selectedRentTerm, isWithAmmo, crewType).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self.__purchaseInProgress = False
            self.__onItemCacheSyncCompleted()
        if result and result.success:
            self.__successOperation = True
            if self.__isRenting() or self.bootcamp.isInBootcamp():
                self.__onWindowClose()
            else:
                self.__showCongratulations(isRestore)
        else:
            self.__onWindowClose()
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

    def __showCongratulations(self, isRestore):
        if self.viewStatus != ViewStatus.LOADED:
            _logger.warning('Can not show congratulations! The view is not loaded anymore.')
            return
        else:
            self.viewModel.setIsContentHidden(True)
            with self.viewModel.congratulationAnim.transaction() as model:
                vehicleType = '{}_elite'.format(self.__vehicle.type) if self.__vehicle.isElite else self.__vehicle.type
                image = self.__vehicle.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_LARGE)
                defaultImage = RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_LARGE, 'empty_tank')
                model.setIsElite(self.__vehicle.isElite)
                model.setVehicleType(vehicleType)
                model.setLvl(int2roman(self.__vehicle.level))
                model.setVName(self.__vehicle.userName)
                model.setImage(image if image is not None else defaultImage)
                model.setImageAlt(defaultImage)
                model.setTitle(R.strings.store.congratulationAnim.restoreLabel if isRestore else R.strings.store.congratulationAnim.buyingLabel)
                model.setBtnLbl(R.strings.store.congratulationAnim.showPreviewBtn)
            return

    def __getObtainVehicleProcessor(self, crewType):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleBuyer(self.__vehicle, isWithSlot, isWithAmmo, crewType)

    def __updateBuyBtnLabel(self):
        if self.__selectedRentIdx == self.__RENT_NOT_SELECTED_IDX:
            label = R.strings.store.buyVehicleWindow.restore
        elif self.__tradeOffVehicle is not None and not self.__isRentVisible:
            label = R.strings.store.buyVehicleWindow.exchange
        else:
            label = R.strings.store.buyVehicleWindow.buyBtn
        self.viewModel.equipmentBlock.setBuyBtnLabel(label)
        return

    def getRestoreVehicleProcessor(self, crewType):
        equipmentBlock = self.viewModel.equipmentBlock
        isWithAmmo = equipmentBlock.ammo.getIsSelected()
        isWithSlot = equipmentBlock.slot.getIsSelected()
        return VehicleRestoreProcessor(self.__vehicle, isWithSlot, isWithAmmo, crewType)

    def __onRestoreChange(self, _):
        vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.__nationID, self.__inNationID)
        if vehicle and not vehicle.isRestoreAvailable():
            self.__onWindowClose()
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.VEHICLE_RESTORE_FINISHED, vehicleName=vehicle.userName)


class BuyVehicleWindow(Window):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        app = g_appLoader.getApp()
        view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
        if view is not None:
            parent = view.getParentWindow()
        else:
            parent = None
        super(BuyVehicleWindow, self).__init__(content=BuyVehicleView(*args, **kwargs), wndFlags=WindowFlags.DIALOG, decorator=None, parent=parent)
        return
