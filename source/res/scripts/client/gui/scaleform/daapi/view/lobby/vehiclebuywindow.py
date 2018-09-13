# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleBuyWindow.py
import BigWorld
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, VehicleSlotBuyer
from account_helpers.AccountSettings import AccountSettings, VEHICLE_BUY_WINDOW_SETTINGS
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.VehicleBuyWindowMeta import VehicleBuyWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui import SystemMessages
from gui.shared import g_itemsCache
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE, getItemActionTooltipData
from gui.shared.utils import decorators
from gui.shared.gui_items import GUI_ITEM_TYPE

class VehicleBuyWindow(View, VehicleBuyWindowMeta, AppRef, AbstractWindowView):

    def __init__(self, ctx):
        super(VehicleBuyWindow, self).__init__()
        self.nationID = ctx.get('nationID')
        self.inNationID = ctx.get('itemID')

    def _populate(self):
        super(VehicleBuyWindow, self)._populate()
        self._initData()
        g_itemsCache.onSyncCompleted += self._initData
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
            return
        else:
            shop = g_itemsCache.items.shop
            shopDefaults = shop.defaults
            tankMenCount = len(vehicle.crew)
            tankMenStudyPrice = shop.tankmanCost
            totalTankMenStudePrice = (tankMenStudyPrice[1]['credits'] * tankMenCount, tankMenStudyPrice[2]['gold'] * tankMenCount)
            defTankMenStudyPrice = shopDefaults.tankmanCost
            defTotalTankMenStudePrice = (defTankMenStudyPrice[1]['credits'] * tankMenCount, defTankMenStudyPrice[2]['gold'] * tankMenCount)
            studyPriceCreditsActionData = None
            if totalTankMenStudePrice[0] != defTotalTankMenStudePrice[0]:
                studyPriceCreditsActionData = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
                 'key': 'creditsTankmanCost',
                 'isBuying': True,
                 'state': (ACTION_TOOLTIPS_STATE.DISCOUNT, None),
                 'newPrice': (totalTankMenStudePrice[0], 0),
                 'oldPrice': (defTotalTankMenStudePrice[0], 0)}
            studyPriceGoldActionData = None
            if totalTankMenStudePrice[1] != defTotalTankMenStudePrice[1]:
                studyPriceGoldActionData = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
                 'key': 'goldTankmanCost',
                 'isBuying': True,
                 'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
                 'newPrice': (0, totalTankMenStudePrice[1]),
                 'oldPrice': (0, defTotalTankMenStudePrice[1])}
            vehiclePricesActionData = None
            if vehicle.buyPrice != vehicle.defaultPrice:
                vehiclePricesActionData = getItemActionTooltipData(vehicle)
            ammoPrice = [0, 0]
            defAmmoPrice = [0, 0]
            for shell in vehicle.gun.defaultAmmo:
                ammoPrice[0] += shell.buyPrice[0] * shell.defaultCount
                ammoPrice[1] += shell.buyPrice[1] * shell.defaultCount
                defAmmoPrice[0] += shell.defaultPrice[0] * shell.defaultCount
                defAmmoPrice[1] += shell.defaultPrice[1] * shell.defaultCount

            ammoActionPriceData = None
            if ammoPrice[0] != defAmmoPrice[0]:
                ammoActionPriceData = {'type': ACTION_TOOLTIPS_TYPE.AMMO,
                 'key': str(vehicle.intCD),
                 'isBuying': True,
                 'state': (ACTION_TOOLTIPS_STATE.DISCOUNT, None),
                 'newPrice': ammoPrice,
                 'oldPrice': defAmmoPrice}
            slotPrice = shop.getVehicleSlotsPrice(stats.vehicleSlots)
            slotDefaultPrice = shopDefaults.getVehicleSlotsPrice(stats.vehicleSlots)
            slotActionPriceData = None
            if slotPrice != slotDefaultPrice:
                slotActionPriceData = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
                 'key': 'slotsPrices',
                 'isBuying': True,
                 'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
                 'newPrice': (0, slotPrice),
                 'oldPrice': (0, slotDefaultPrice)}
            initData = {'expanded': windowExpanded,
             'name': vehicle.userName,
             'longName': vehicle.longUserName,
             'description': vehicle.fullDescription,
             'type': vehicle.type,
             'icon': vehicle.icon,
             'nation': self.nationID,
             'level': vehicle.level,
             'isElite': vehicle.isElite,
             'tankmenCount': tankMenCount,
             'studyPriceCredits': totalTankMenStudePrice[0],
             'studyPriceCreditsActionData': studyPriceCreditsActionData,
             'studyPriceGold': totalTankMenStudePrice[1],
             'studyPriceGoldActionData': studyPriceGoldActionData,
             'vehiclePrices': vehicle.buyPrice,
             'vehiclePricesActionData': vehiclePricesActionData,
             'ammoPrice': ammoPrice[0],
             'ammoActionPriceData': ammoActionPriceData,
             'slotPrice': slotPrice,
             'slotActionPriceData': slotActionPriceData}
            self.as_setInitDataS(initData)
            return

    def storeSettings(self, expanded):
        AccountSettings.setSettings(VEHICLE_BUY_WINDOW_SETTINGS, expanded)

    @decorators.process('buyItem')
    def submit(self, data):
        vehicle = g_itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, self.nationID, self.inNationID)
        if data.buySlot:
            result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
            if len(result.userMsg):
                SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success:
                return
        result = yield VehicleBuyer(vehicle, data.buySlot, data.buyAmmo, data.crewType).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
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
        super(VehicleBuyWindow, self)._dispose()
