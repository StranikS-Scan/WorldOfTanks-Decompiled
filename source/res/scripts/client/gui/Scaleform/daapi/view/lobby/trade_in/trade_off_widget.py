# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trade_in/trade_off_widget.py
from gui.Scaleform.daapi.view.meta.TradeOffWidgetMeta import TradeOffWidgetMeta
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shop import showTradeOffOverlay, showPersonalTradeOffOverlay
from gui.shared import events
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import getSmallIconPath
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import ITradeInController, IPersonalTradeInController
from skeletons.gui.shared import IItemsCache
_DEFAULT_TRADE_IN_VEHICLE_LEVEL = 10

class TradeOffWidget(TradeOffWidgetMeta, EventSystemEntity):
    __tradeIn = dependency.descriptor(ITradeInController)
    __personalTradeIn = dependency.descriptor(IPersonalTradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(TradeOffWidget, self).__init__()
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        self.__tradeInVehicle = None
        return

    def setTradeInVehicle(self, tradeInVehicle):
        self.__tradeInVehicle = tradeInVehicle
        if self.__isPersonalTradeIn():
            self.__setData(self.__personalTradeIn.getActiveTradeInSaleVehicle())

    def onClick(self):
        if self.__isPersonalTradeIn():
            showPersonalTradeOffOverlay()
        else:
            showTradeOffOverlay(self.__getTradeInVehicleLevel())

    def onResetClick(self):
        if self.__isPersonalTradeIn():
            showPersonalTradeOffOverlay()
        else:
            self.__tradeIn.setActiveTradeOffVehicleCD(UNDEFINED_ITEM_CD)

    def getTooltip(self):
        if self.__isPersonalTradeIn():
            tooltipType = TOOLTIPS_CONSTANTS.PERSONAL_TRADE_IN_INFO
            data = ''
        elif self.__tradeIn.isEnabled() and bool(self.__tradeIn.getTradeOffVehicles()):
            tooltipType = TOOLTIPS_CONSTANTS.TRADE_IN_INFO
            data = self.__tradeIn.getAllowedVehicleLevels(self.__getTradeInVehicleLevel())
        else:
            tooltipType = TOOLTIPS_CONSTANTS.TRADE_IN_INFO_NOT_AVAILABLE
            data = self.__tradeIn.getAllowedVehicleLevels(self.__getTradeInVehicleLevel())
        return {'type': tooltipType,
         'data': data}

    def _populate(self):
        super(TradeOffWidget, self)._populate()
        self.__setData(self.__tradeIn.getActiveTradeOffVehicle())
        self.addListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)
        self.__itemsCache.onSyncCompleted += self.__onCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged += self.__onTradeOffSelectedChanged

    def _dispose(self):
        self.__itemsCache.onSyncCompleted -= self.__onCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged -= self.__onTradeOffSelectedChanged
        self.removeListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)
        super(TradeOffWidget, self)._dispose()

    def __onTradeOffSelectedChanged(self, _=None):
        if self.__isPersonalTradeIn():
            self.__setData(self.__personalTradeIn.getActiveTradeInSaleVehicle())
        else:
            self.__setData(self.__tradeIn.getActiveTradeOffVehicle())

    def __setData(self, vehicle=None):
        self.as_setDataS(self.__createVO(vehicle))

    def __createVO(self, vehicle=None):
        if self.__isPersonalTradeIn():
            vehiclesAvailable = True
        else:
            vehiclesAvailable = bool(self.__tradeIn.getTradeOffVehicles())
        vo = {'showTradeOff': vehicle is None,
         'available': vehiclesAvailable}
        if vehicle is not None:
            vo.update({'vehicleNationFlag': RES_ICONS.getTradeInNationFlag(vehicle.nationName),
             'vehicleType': Vehicle.getTypeSmallIconPath(vehicle.type, vehicle.isElite),
             'vehicleLevel': RES_ICONS.getLevelIcon(vehicle.level),
             'vehicleIcon': getSmallIconPath(vehicle.name),
             'vehicleTitle': vehicle.shortUserName,
             'isPersonal': self.__isPersonalTradeIn()})
        return vo

    def __onCacheSyncCompleted(self, updateReason, _=None):
        if updateReason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC):
            if self.__isPersonalTradeIn():
                veh = self.__personalTradeIn.getActiveTradeInSaleVehicle()
            else:
                veh = self.__tradeIn.getActiveTradeOffVehicle()
            self.__setData(veh)

    def __getTradeInVehicleLevel(self):
        return self.__tradeInVehicle.level if self.__tradeInVehicle is not None else _DEFAULT_TRADE_IN_VEHICLE_LEVEL

    def __isPersonalTradeIn(self):
        try:
            isPersonalTradeIN = self.__tradeInVehicle.intCD in self.__personalTradeIn.getBuyVehicleCDs()
        except AttributeError:
            isPersonalTradeIN = False

        return isPersonalTradeIN
