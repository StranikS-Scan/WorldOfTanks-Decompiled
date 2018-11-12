# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_obtain_windows.py
from collections import namedtuple
from soft_exception import SoftException
import constants
from rent_common import parseRentID, isWithinMaxRentTime
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.DialogsInterface import showI18nConfirmDialog
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.VehicleBuyWindowMeta import VehicleBuyWindowMeta
from gui.Scaleform.genConsts.VEHICLE_BUY_WINDOW_ALIASES import VEHICLE_BUY_WINDOW_ALIASES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.ingame_shop import showBuyGoldForVehicleWebOverlay
from gui.shared.events import VehicleBuyEvent
from gui.shared.formatters import text_styles, moneyWithIcon
from gui.shared.formatters.text_styles import neutral
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ItemPrice, ITEM_PRICE_EMPTY
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter, VehicleRestoreProcessor, VehicleTradeInProcessor
from gui.shared.money import Money, Currency
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.formatters import packItemActionTooltipData, packItemRentActionTooltipData
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IRentalsController, ITradeInController, IRestoreController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class _TABS(CONST_CONTAINER):
    UNDEFINED = -1
    BUY = 0
    TRADE = 1


VehicleBuyWindowState = namedtuple('VehicleBuyWindowState', ('buyAmmo',
 'buySlot',
 'crewType',
 'rentID'))

class VehicleBuyWindow(VehicleBuyWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    rentals = dependency.descriptor(IRentalsController)
    tradeIn = dependency.descriptor(ITradeInController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(VehicleBuyWindow, self).__init__()
        self.nationID = ctx.get('nationID')
        self.inNationID = ctx.get('itemID')
        self.vehicle = None
        self.tradeOffVehicle = None
        self.__state = VehicleBuyWindowState(False, False, -1, -1)
        self.__isGoldAutoPurhaseEnabled = isIngameShopEnabled()
        if ctx.get('isTradeIn', False):
            self.selectedTab = _TABS.TRADE
        else:
            self.selectedTab = _TABS.UNDEFINED
        return

    def onWindowClose(self):
        self.destroy()

    def submit(self, data):
        if self.__isGoldAutoPurhaseEnabled:
            availableGold = self.itemsCache.items.stats.money.gold
            requiredGold = (self._getVehiclePrice(self.vehicle) + self._getSetupPrice()).price.gold
            if availableGold < requiredGold:
                showBuyGoldForVehicleWebOverlay(requiredGold, self.vehicle.intCD)
                return
        self.__requestForMoneyObtain(data)

    def stateChange(self, data):
        self.__state = VehicleBuyWindowState(data.buyAmmo, data.buySlot, data.crewType, data.rentId)
        self.__updateButtons()

    def onTradeInClearVehicle(self):
        self.tradeOffVehicle = None
        self.as_setTradeInWarningMessagegeS('')
        return

    def selectTab(self, tabIndex):
        self.selectedTab = tabIndex

    def _populate(self):
        super(VehicleBuyWindow, self)._populate()
        self._initData()
        self.itemsCache.onSyncCompleted += self._initData
        self.rentals.onRentChangeNotify += self.__onRentChange
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.__setCreditsCallBack)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.__setGoldCallBack)
        self.addListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__setTradeOffVehicle)

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self._initData
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.rentals.onRentChangeNotify -= self.__onRentChange
        self.removeListener(VehicleBuyEvent.VEHICLE_SELECTED, self.__setTradeOffVehicle)
        self.vehicle = None
        self.tradeOffVehicle = None
        super(VehicleBuyWindow, self)._dispose()
        return

    def _getGuiFields(self, vehicle):
        return {'title': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TITLE, vehiclename=vehicle.userName),
         'submitBtnLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_SUBMITBTN),
         'cancelBtnLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_CANCELBTN)}

    def _isTradeIn(self):
        return self.tradeIn.isEnabled() and self.vehicle.canTradeIn

    def __getTradeInGuiFields(self, vehicle):
        return {'tradeInTitle': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_TITLE, vehiclename=vehicle.userName),
         'tradeInSubmitBtnLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_SUBMITBTN),
         'tradeInCancelBtnLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_CANCELBTN)}

    def _getContentFields(self, vehicle):
        slotCheckboxTooltip = None
        if self.itemsCache.items.inventory.getFreeSlots(self.itemsCache.items.stats.vehicleSlots) <= 0:
            slotCheckboxTooltip = makeTooltip(TOOLTIPS.CONTENTBUYVIEW_SLOTCHECKBOX_NOTENOUGHSLOTS_HEADER, TOOLTIPS.CONTENTBUYVIEW_SLOTCHECKBOX_NOTENOUGHSLOTS_BODY)
        return {'slotCheckboxTooltip': slotCheckboxTooltip,
         'priceLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_PRICELABEL, vehiclename=vehicle.shortUserName),
         'crewCheckbox': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TANKMENCHECKBOX),
         'warningMsg': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_WARNING) if constants.IS_KOREA else None}

    def __getTradeInContentFields(self, vehicle):
        if self.selectedTab == _TABS.UNDEFINED:
            if vehicle.mayPurchase(self.itemsCache.items.stats.money)[0]:
                self.selectedTab = _TABS.BUY
            else:
                self.selectedTab = _TABS.TRADE
        return {'tradeInPriceLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_PRICELABEL, vehiclename=vehicle.shortUserName),
         'tradeInCrewCheckbox': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_TANKMENCHECKBOX),
         'tradeInVehiclePrices': self._getVehiclePrice(vehicle).price.toMoneyTuple(),
         'tradeInVehiclePricesActionData': self._getItemPriceActionData(vehicle),
         'tradeInStudyLabel': i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_STUDYLABEL, count=text_styles.stats(str(len(vehicle.crew)))),
         'hasTradeOffVehicles': self.tradeIn.getTradeInInfo(vehicle) is not None,
         'selectedTab': self.selectedTab}

    def _isSubmitBtnEnabled(self):
        if self.vehicle.isPurchased:
            return False
        money = self.itemsCache.items.stats.money
        vehiclePrice = self._getVehiclePrice(self.vehicle)
        setupPrice = self._getSetupPrice()
        totalPrice = vehiclePrice + setupPrice
        canBuy = totalPrice.price <= money
        canBuy |= self.__isGoldAutoPurhaseEnabled and totalPrice.price.gold > money.gold and totalPrice.price.credits <= money.credits
        return canBuy

    def _initData(self, *args):
        stats = self.itemsCache.items.stats
        self.as_setGoldS(stats.gold)
        self.as_setCreditsS(stats.credits)
        self.vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        self.__updateButtons()
        if self.vehicle is None:
            LOG_ERROR("Vehicle Item mustn't be None!", 'NationID:', self.nationID, 'InNationID:', self.inNationID)
        elif self.vehicle.isInInventory and not self.vehicle.isRented:
            self.onWindowClose()
        else:
            isTradeIn = self._isTradeIn()
            initData = {'headerData': self._getOptainHeaderData(self.vehicle),
             'isTradeIn': isTradeIn,
             'contentData': self._getBuyContentData(self.vehicle, stats, isTradeIn)}
            initData.update(self._getContentLinkageFields())
            initData.update(self._getGuiFields(self.vehicle))
            if isTradeIn:
                initData.update(self.__getTradeInGuiFields(self.vehicle))
            self.as_setInitDataS(initData)
        return

    def _getContentLinkageFields(self):
        tradeInUI = VEHICLE_BUY_WINDOW_ALIASES.CONTENT_BUY_TRADE_IN_CONTAINER_VIEW_UI
        buyUI = VEHICLE_BUY_WINDOW_ALIASES.CONTENT_BUY_VIEW_UI
        return {'contentLinkage': tradeInUI if self._isTradeIn() else buyUI,
         'isContentDAAPI': False}

    def _getOptainHeaderData(self, vehicle):
        from helpers import int2roman
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(vehicle.level)), text_styles.main(i18n.makeString(DIALOGS.VEHICLESELLDIALOG_VEHICLE_LEVEL)))
        if vehicle.isElite:
            description = TOOLTIPS.tankcaruseltooltip_vehicletype_elite(vehicle.type)
        else:
            description = DIALOGS.vehicleselldialog_vehicletype(vehicle.type)
        return {'userName': vehicle.userName,
         'levelStr': levelStr,
         'description': description,
         'intCD': vehicle.intCD,
         'icon': vehicle.icon,
         'level': vehicle.level,
         'isElite': vehicle.isElite,
         'isPremium': vehicle.isPremium,
         'type': vehicle.type,
         'nationID': self.nationID}

    def _getBuyContentData(self, vehicle, stats, isTradeIn):
        shop = self.itemsCache.items.shop
        shopDefaults = shop.defaults
        tankMenCount = len(vehicle.crew)
        vehiclePricesActionData = self._getItemPriceActionData(vehicle)
        ammoPrice = self._getAmmoPrice()
        ammoActionPriceData = None
        if ammoPrice.isActionPrice():
            ammoActionPriceData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.AMMO, str(vehicle.intCD), True, ammoPrice.price, ammoPrice.defPrice)
        slotPrice = shop.getVehicleSlotsPrice(stats.vehicleSlots)
        slotDefaultPrice = shopDefaults.getVehicleSlotsPrice(stats.vehicleSlots)
        slotActionPriceData = None
        if slotPrice != slotDefaultPrice:
            slotActionPriceData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'slotsPrices', True, Money(gold=slotPrice), Money(gold=slotDefaultPrice))
        tankmenTotalLabel = i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TANKMENTOTALLABEL, count=str(tankMenCount))
        studyData = []
        for index, (tCost, defTCost, typeID) in enumerate(zip(shop.tankmanCostWithGoodyDiscount, shopDefaults.tankmanCost, ('free', 'school', 'academy'))):
            if tCost['isPremium']:
                currency = Currency.GOLD
            else:
                currency = Currency.CREDITS
            price = tCost[currency] * tankMenCount
            defPrice = defTCost[currency] * tankMenCount
            totalPrice = Money.makeFrom(currency, price)
            totalDefPrice = Money.makeFrom(currency, defPrice)
            if typeID == 'free':
                formatedPrice = i18n.makeString(MENU.TANKMANTRAININGWINDOW_FREE_PRICE)
            else:
                formatedPrice = moneyWithIcon(totalPrice, currType=currency)
            studyPriceActionData = None
            if price != defPrice:
                studyPriceActionData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, '%sTankmanCost' % currency, True, totalPrice, totalDefPrice)
            studyData.insert(0, {'id': typeID,
             'price': price,
             'crewType': index,
             'actionPrice': studyPriceActionData,
             'label': '%d%% - %s' % (tCost['roleLevel'], formatedPrice)})

        initData = {'tankmenTotalLabel': tankmenTotalLabel,
         'vehiclePrices': self._getVehiclePrice(vehicle).price.toMoneyTuple(),
         'vehiclePricesActionData': vehiclePricesActionData,
         'isRentable': vehicle.isRentable,
         'rentDataDD': self._getRentData(vehicle, vehiclePricesActionData),
         'ammoPrice': ammoPrice.price.getSignValue(Currency.CREDITS),
         'ammoActionPriceData': ammoActionPriceData,
         'slotPrice': slotPrice,
         'slotActionPriceData': slotActionPriceData,
         'isStudyDisabled': vehicle.hasCrew,
         'isNoAmmo': not vehicle.hasShells,
         'studyData': studyData,
         'nation': self.nationID}
        initData.update(self._getContentFields(vehicle))
        if isTradeIn:
            initData.update(self.__getTradeInContentFields(vehicle))
        return initData

    def _getSetupPrice(self):
        setupPrice = ITEM_PRICE_EMPTY
        if self.__state.buyAmmo:
            setupPrice = setupPrice + self._getAmmoPrice()
        if self.__state.buySlot:
            setupPrice = setupPrice + self._getSlotPrice()
        if self.__state.crewType != -1:
            setupPrice = setupPrice + self._getCrewPrice()
        return setupPrice

    def _getAmmoPrice(self):
        ammoPrice = ITEM_PRICE_EMPTY
        for shell in self.vehicle.gun.defaultAmmo:
            ammoPrice += shell.buyPrices.itemPrice * shell.defaultCount

        return ammoPrice

    def _getSlotPrice(self):
        shop = self.itemsCache.items.shop
        stats = self.itemsCache.items.stats
        price = Money(gold=shop.getVehicleSlotsPrice(stats.vehicleSlots))
        defPrice = Money(gold=shop.defaults.getVehicleSlotsPrice(stats.vehicleSlots))
        return ItemPrice(price, defPrice)

    def _getCrewPrice(self):
        if self.__state.crewType != -1:
            shop = self.itemsCache.items.shop
            costs = (shop.tankmanCostWithGoodyDiscount[self.__state.crewType], shop.defaults.tankmanCost[self.__state.crewType])
            tankmanCount = len(self.vehicle.crew)
            return ItemPrice(*[ Money(gold=cost[Currency.GOLD], credits=cost[Currency.CREDITS]) for cost in costs ]) * tankmanCount
        return ITEM_PRICE_EMPTY

    def _getVehiclePrice(self, vehicle):
        if self.__state.rentID == -1:
            return vehicle.buyPrices.itemPrice
        rentPackage = vehicle.rentPackages[self.__state.rentID]
        price, defPrice = rentPackage['rentPrice'], rentPackage['defaultRentPrice']
        return ItemPrice(price, defPrice)

    def _getItemPriceActionData(self, vehicle):
        return packItemActionTooltipData(vehicle) if vehicle.buyPrices.itemPrice.isActionPrice() else None

    def _getRentData(self, vehicle, vehiclePricesActionData):
        result = []
        rentPackages = vehicle.rentPackages
        for rentPackage in rentPackages:
            rentID = rentPackage['rentID']
            rentType, packageID = parseRentID(rentID)
            if rentType == constants.RentType.TIME_RENT:
                label = i18n.makeString(MENU.SHOP_MENU_VEHICLE_RENT_DAYS, days=packageID)
                enabled = isWithinMaxRentTime(vehicle.maxRentDuration, vehicle.rentLeftTime, packageID)
            elif rentType == constants.RentType.SEASON_RENT:
                seasonType = rentPackage['seasonType']
                label = i18n.makeString(MENU.SHOP_MENU_VEHICLE_RENT_SEASON, season=packageID, seasonType=seasonType)
                enabled = True
            elif rentType == constants.RentType.SEASON_CYCLE_RENT:
                seasonType = rentPackage['seasonType']
                label = i18n.makeString(MENU.SHOP_MENU_VEHICLE_RENT_CYCLE, cycle=packageID, seasonType=seasonType)
                enabled = True
            else:
                raise SoftException('Unknown rentType=[{}] in rentPackages ID [{}]!'.format(rentType, rentID))
            actionRentPrice = None
            if rentPackage['rentPrice'] != rentPackage['defaultRentPrice']:
                actionRentPrice = packItemRentActionTooltipData(vehicle, rentPackage)
            result.append({'itemId': rentID,
             'label': label,
             'price': rentPackage['rentPrice'].toMoneyTuple(),
             'enabled': enabled,
             'actionPrice': actionRentPrice})

        result = self._addPriceBlock(result, vehicle, vehiclePricesActionData)
        selectedId = -1
        for ddItem in result:
            if ddItem['enabled']:
                selectedId = ddItem['itemId']
                break

        return {'data': result,
         'selectedId': selectedId}

    def _addPriceBlock(self, result, vehicle, vehiclePricesActionData):
        result.append({'itemId': -1,
         'label': i18n.makeString(MENU.SHOP_MENU_VEHICLE_RENT_FOREVER),
         'price': vehicle.buyPrices.itemPrice.price.toMoneyTuple(),
         'enabled': not vehicle.isDisabledForBuy and not vehicle.isHidden,
         'actionPrice': vehiclePricesActionData})
        return result

    def _getObtainVehicleProcessor(self, vehicle, data):
        return VehicleBuyer(vehicle, data.buySlot, data.buyAmmo, data.crewType)

    def __onRentChange(self, vehicles):
        vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        if vehicle and vehicle.intCD in vehicles:
            self._initData()

    def __updateButtons(self):
        isBuyEnabled = self._isSubmitBtnEnabled()
        isStudyEnabled = not self.vehicle.hasCrew
        academyEnabled = isStudyEnabled
        schoolEnabled = isStudyEnabled
        freeEnabled = isStudyEnabled
        self.as_setStateS(academyEnabled, schoolEnabled, freeEnabled, isBuyEnabled)

    @decorators.process('buyItem')
    def __requestForMoneyObtain(self, data):
        isTradeIn = data.tradeOff != -1
        result = None
        if isTradeIn:
            tradeOffVehicle = self.itemsCache.items.getItemByCD(int(data.tradeOff))
            confirmationType = 'tradeInConfirmation'
            addition = ''
            operations = []
            if tradeOffVehicle.hasCrew:
                operations.append('crew')
            if tradeOffVehicle.hasShells:
                operations.append('shells')
            if tradeOffVehicle.hasEquipments:
                operations.append('equipments')
            if tradeOffVehicle.hasOptionalDevices:
                operations.append('optionalDevices')
            if operations:
                operationsStr = [ i18n.makeString('#dialogs:%s/message/%s' % (confirmationType, o)) for o in operations ]
                addition = i18n.makeString('#dialogs:%s/message/addition' % confirmationType, operations=', '.join(operationsStr))
            ctx = {'vehName': neutral(tradeOffVehicle.userName),
             'addition': addition}
            result = yield showI18nConfirmDialog(confirmationType, meta=I18nConfirmDialogMeta(confirmationType, ctx, ctx), focusedID=DIALOG_BUTTON_ID.SUBMIT)
            if not result:
                return
            tradeOffVehicle = self.itemsCache.items.getItemByCD(int(data.tradeOff))
            result = yield VehicleTradeInProcessor(self.vehicle, tradeOffVehicle, data.buySlot, data.buyAmmo, data.crewType).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success:
                self.onWindowClose()
                return
        if data.buySlot:
            result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success:
                return
        if not isTradeIn:
            if data.rentId != -1:
                result = yield VehicleRenter(self.vehicle, data.rentId, data.buyAmmo, data.crewType).request()
            else:
                result = yield self._getObtainVehicleProcessor(self.vehicle, data).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result and result.success:
            self.onWindowClose()
        return

    def __setGoldCallBack(self, gold):
        self.as_setGoldS(gold)

    def __setCreditsCallBack(self, credit):
        self.as_setCreditsS(credit)

    def __setTradeOffVehicle(self, event):
        selectedVehCD = int(event.ctx)
        self.tradeOffVehicle = self.itemsCache.items.getItemByCD(selectedVehCD)
        tradeOffVehicleHtml = moneyWithIcon(self.tradeOffVehicle.tradeOffPrice, currType=Currency.GOLD)
        tradeOffVehicleStatus = i18n.makeString(DIALOGS.BUYVEHICLEWINDOW_TRADEIN_INFO_SAVING, cost=tradeOffVehicleHtml)
        tradeOffVehicleVo = makeVehicleVO(self.tradeOffVehicle)
        tradeOffVehicleVo['actionPrice'] = self._getItemPriceActionData(self.tradeOffVehicle)
        tradeOffData = {'vehicleVo': tradeOffVehicleVo,
         'price': self.tradeOffVehicle.tradeOffPrice.getSignValue(Currency.GOLD),
         'status': tradeOffVehicleStatus}
        self.as_updateTradeOffVehicleS(tradeOffData)
        self.as_setTradeInWarningMessagegeS(i18n.makeString(DIALOGS.TRADEINCONFIRMATION_MESSAGE, vehName=self.tradeOffVehicle.userName, addition=''))


class VehicleRestoreWindow(VehicleBuyWindow):
    restore = dependency.descriptor(IRestoreController)

    def submit(self, data):
        super(VehicleRestoreWindow, self).submit(data)

    def _populate(self):
        super(VehicleRestoreWindow, self)._populate()
        self.restore.onRestoreChangeNotify += self.__onRestoreChange

    def _dispose(self):
        super(VehicleRestoreWindow, self)._dispose()
        self.restore.onRestoreChangeNotify -= self.__onRestoreChange

    def _addPriceBlock(self, result, vehicle, vehiclePricesActionData):
        disabled = not vehicle.isRestoreAvailable() or constants.IS_CHINA and vehicle.rentalIsActive
        result.insert(0, {'itemId': -1,
         'label': i18n.makeString(MENU.SHOP_MENU_VEHICLE_RESTORE),
         'price': vehicle.restorePrice.toMoneyTuple(),
         'enabled': not disabled,
         'actionPrice': vehiclePricesActionData})
        return result

    def _getObtainVehicleProcessor(self, vehicle, data):
        return VehicleRestoreProcessor(vehicle, data.buySlot, data.buyAmmo, data.crewType)

    def _getVehiclePrice(self, vehicle):
        return ItemPrice(vehicle.restorePrice, vehicle.restorePrice)

    def _getItemPriceActionData(self, vehicle):
        return None

    def _getGuiFields(self, vehicle):
        return {'title': i18n.makeString(DIALOGS.RESTOREVEHICLEDIALOG_TITLE, vehiclename=vehicle.userName),
         'cancelBtnLabel': i18n.makeString(DIALOGS.RESTOREVEHICLEDIALOG_CANCELBTN),
         'submitBtnLabel': i18n.makeString(DIALOGS.RESTOREVEHICLEDIALOG_SUBMITBTN)}

    def _getContentFields(self, vehicle):
        vehicleName = vehicle.shortUserName if vehicle.isRentable else vehicle.userName
        return {'priceLabel': i18n.makeString(DIALOGS.RESTOREVEHICLEDIALOG_PRICELABEL, vehiclename=vehicleName),
         'crewCheckbox': i18n.makeString(DIALOGS.RESTOREVEHICLEDIALOG_TANKMENCHECKBOX),
         'warningMsg': i18n.makeString(DIALOGS.RESTOREVEHICLEDIALOG_WARNING) if constants.IS_KOREA else None}

    def _isTradeIn(self):
        return False

    def __onRestoreChange(self, _):
        vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        if vehicle and not vehicle.isRestoreAvailable():
            self.onWindowClose()
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.VEHICLE_RESTORE_FINISHED, vehicleName=vehicle.userName)
