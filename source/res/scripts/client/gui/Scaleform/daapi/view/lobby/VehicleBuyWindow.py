# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleBuyWindow.py
import BigWorld
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer, VehicleRenter
from account_helpers.AccountSettings import AccountSettings, VEHICLE_BUY_WINDOW_SETTINGS
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.VehicleBuyWindowMeta import VehicleBuyWindowMeta
from gui import SystemMessages
from gui.shared import g_itemsCache
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from gui.shared.tooltips.formatters import packItemActionTooltipData, packItemRentActionTooltipData
from gui.shared.utils import decorators
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Money, ZERO_MONEY
from gui.shared.tooltips.formatters import packActionTooltipData
from helpers import i18n, time_utils
from gui.game_control import g_instance as g_gameCtrl

class VehicleBuyWindow(VehicleBuyWindowMeta):

    def __init__(self, ctx=None):
        super(VehicleBuyWindow, self).__init__()
        self.nationID = ctx.get('nationID')
        self.inNationID = ctx.get('itemID')

    def _populate(self):
        super(VehicleBuyWindow, self)._populate()
        self._initData()
        g_itemsCache.onSyncCompleted += self._initData
        g_gameCtrl.rentals.onRentChangeNotify += self._onRentChange
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__setCreditsCallBack,
         'stats.gold': self.__setGoldCallBack})

    def _initData(self, *args):
        stats = g_itemsCache.items.stats
        self.as_setGoldS(stats.gold)
        self.as_setCreditsS(stats.credits)
        windowExpanded = AccountSettings.getSettings(VEHICLE_BUY_WINDOW_SETTINGS)
        vehicle = g_itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        if vehicle is None:
            LOG_ERROR("Vehicle Item mustn't be None!", 'NationID:', self.nationID, 'InNationID:', self.inNationID)
        elif vehicle.isInInventory and not vehicle.isRented:
            self.onWindowClose()
        else:
            shop = g_itemsCache.items.shop
            shopDefaults = shop.defaults
            tankMenCount = len(vehicle.crew)
            tankMenStudyPrice = shop.tankmanCostWithGoodyDiscount
            totalTankMenStudePrice = tankMenCount * Money(credits=tankMenStudyPrice[1]['credits'], gold=tankMenStudyPrice[2]['gold'])
            defTankMenStudyPrice = shopDefaults.tankmanCost
            defTotalTankMenStudePrice = tankMenCount * Money(credits=defTankMenStudyPrice[1]['credits'], gold=defTankMenStudyPrice[2]['gold'])
            studyPriceCreditsActionData = None
            if totalTankMenStudePrice != defTotalTankMenStudePrice:
                studyPriceCreditsActionData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'creditsTankmanCost', True, totalTankMenStudePrice, defTotalTankMenStudePrice)
            studyPriceGoldActionData = None
            if totalTankMenStudePrice != defTotalTankMenStudePrice:
                studyPriceGoldActionData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'goldTankmanCost', True, totalTankMenStudePrice, defTotalTankMenStudePrice)
            vehiclePricesActionData = None
            if vehicle.buyPrice != vehicle.defaultPrice:
                vehiclePricesActionData = packItemActionTooltipData(vehicle)
            ammoPrice = ZERO_MONEY
            defAmmoPrice = ZERO_MONEY
            for shell in vehicle.gun.defaultAmmo:
                ammoPrice += shell.buyPrice * shell.defaultCount
                defAmmoPrice += shell.defaultPrice * shell.defaultCount

            ammoActionPriceData = None
            if ammoPrice != defAmmoPrice:
                ammoActionPriceData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.AMMO, str(vehicle.intCD), True, ammoPrice, defAmmoPrice)
            slotPrice = shop.getVehicleSlotsPrice(stats.vehicleSlots)
            slotDefaultPrice = shopDefaults.getVehicleSlotsPrice(stats.vehicleSlots)
            slotActionPriceData = None
            if slotPrice != slotDefaultPrice:
                slotActionPriceData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'slotsPrices', True, Money(gold=slotPrice), Money(gold=slotDefaultPrice))
            tankmenLabel = i18n.makeString(DIALOGS.BUYVEHICLEDIALOG_TANKMENLABEL, count=text_styles.titleFont(i18n.makeString(DIALOGS.BUYVEHICLEDIALOG_TANKMEN) + ' ' + str(tankMenCount)))
            initData = {'expanded': windowExpanded,
             'name': vehicle.userName,
             'shortName': vehicle.shortUserName,
             'longName': vehicle.longUserName,
             'description': vehicle.fullDescription,
             'type': vehicle.type,
             'icon': vehicle.icon,
             'nation': self.nationID,
             'level': vehicle.level,
             'isElite': vehicle.isElite,
             'tankmenLabel': tankmenLabel,
             'studyPriceCredits': totalTankMenStudePrice.credits,
             'studyPriceCreditsActionData': studyPriceCreditsActionData,
             'studyPriceGold': totalTankMenStudePrice.gold,
             'studyPriceGoldActionData': studyPriceGoldActionData,
             'vehiclePrices': vehicle.buyPrice,
             'vehiclePricesActionData': vehiclePricesActionData,
             'ammoPrice': ammoPrice.credits,
             'ammoActionPriceData': ammoActionPriceData,
             'slotPrice': slotPrice,
             'slotActionPriceData': slotActionPriceData,
             'isRentable': vehicle.isRentable,
             'isStudyDisabled': vehicle.hasCrew,
             'isNoAmmo': not vehicle.hasShells,
             'rentDataDD': self._getRentData(vehicle, vehiclePricesActionData)}
            self.as_setInitDataS(initData)
        return

    def storeSettings(self, expanded):
        AccountSettings.setSettings(VEHICLE_BUY_WINDOW_SETTINGS, expanded)

    def _onRentChange(self, vehicles):
        vehicle = g_itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        if vehicle and vehicle.intCD in vehicles:
            self._initData()

    def _getRentData(self, vehicle, vehiclePricesActionData):
        result = []
        rentPackages = vehicle.rentPackages
        for rentPackage in rentPackages:
            days = rentPackage['days']
            actionRentPrice = None
            if rentPackage['rentPrice'] != rentPackage['defaultRentPrice']:
                actionRentPrice = packItemRentActionTooltipData(vehicle, rentPackage)
            result.append({'itemId': days,
             'label': i18n.makeString(MENU.SHOP_MENU_VEHICLE_RENT_DAYS, days=days),
             'price': rentPackage['rentPrice'],
             'enabled': vehicle.maxRentDuration - vehicle.rentLeftTime >= days * time_utils.ONE_DAY,
             'actionPrice': actionRentPrice})

        result.append({'itemId': -1,
         'label': i18n.makeString(MENU.SHOP_MENU_VEHICLE_RENT_FOREVER),
         'price': vehicle.buyPrice,
         'enabled': not vehicle.isDisabledForBuy and not vehicle.isHidden,
         'actionPrice': vehiclePricesActionData})
        selectedId = -1
        for ddItem in result:
            if ddItem['enabled']:
                selectedId = ddItem['itemId']
                break

        return {'data': result,
         'selectedId': selectedId}

    def submit(self, data):
        self.__requestForBuy(data)

    @decorators.process('buyItem')
    def __requestForBuy(self, data):
        vehicle = g_itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        if data.buySlot:
            result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
            if len(result.userMsg):
                SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success:
                return
        if data.rentId == -1:
            result = yield VehicleBuyer(vehicle, data.buySlot, data.buyAmmo, data.crewType).request()
        else:
            result = yield VehicleRenter(vehicle, data.rentId, data.buyAmmo, data.crewType).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.as_setEnabledSubmitBtnS(True)
        if result.success:
            self.storeSettings(data.isHasBeenExpanded)
            self.onWindowClose()

    def onWindowClose(self):
        self.destroy()

    def __setGoldCallBack(self, gold):
        self.as_setGoldS(gold)

    def __setCreditsCallBack(self, credits):
        self.as_setCreditsS(credits)

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self._initData
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_gameCtrl.rentals.onRentChangeNotify -= self._onRentChange
        super(VehicleBuyWindow, self)._dispose()
