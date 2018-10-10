# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_cm_handlers.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control import prbDispatcherProperty
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.processors.tankman import TankmanUnload
from gui.shared.gui_items.processors.vehicle import VehicleFavoriteProcessor
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

class CREW(object):
    PERSONAL_CASE = 'personalCase'
    UNLOAD = 'tankmanUnload'


class MODULE(object):
    INFO = 'moduleInfo'
    CANCEL_BUY = 'cancelBuy'
    UNLOAD = 'unload'
    UNLOCK = 'unlock'
    EQUIP = 'equip'
    SELL = 'sell'
    BUY_AND_EQUIP = 'buyAndEquip'


class VEHICLE(object):
    INFO = 'vehicleInfoEx'
    PREVIEW = 'preview'
    STATS = 'showVehicleStatistics'
    UNLOCK = 'unlock'
    SELECT = 'selectVehicle'
    SELL = 'sell'
    BUY = 'buy'
    RESEARCH = 'vehicleResearch'
    REMOVE = 'vehicleRemove'
    CHECK = 'vehicleCheck'
    UNCHECK = 'vehicleUncheck'
    COMPARE = 'compare'


class CrewContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, cmProxy, ctx=None):
        super(CrewContextMenuHandler, self).__init__(cmProxy, ctx, {CREW.PERSONAL_CASE: 'showPersonalCase',
         CREW.UNLOAD: 'unloadTankman'})

    def showPersonalCase(self):
        shared_events.showPersonalCase(self._tankmanID, 0, EVENT_BUS_SCOPE.LOBBY)

    @decorators.process('unloading')
    def unloadTankman(self):
        tankman = self.itemsCache.items.getTankman(self._tankmanID)
        result = yield TankmanUnload(g_currentVehicle.item, tankman.vehicleSlotIdx).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def _generateOptions(self, ctx=None):
        return [self._makeItem(CREW.PERSONAL_CASE, MENU.contextmenu('personalCase')), self._makeSeparator(), self._makeItem(CREW.UNLOAD, MENU.contextmenu('tankmanUnload'), {'enabled': True})]

    def _initFlashValues(self, ctx):
        self._tankmanID = int(ctx.tankmanID)

    def _clearFlashValues(self):
        self._tankmanID = None
        return


class TechnicalMaintenanceCMHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx=None):
        super(TechnicalMaintenanceCMHandler, self).__init__(cmProxy, ctx, {MODULE.INFO: 'showModuleInfo',
         MODULE.CANCEL_BUY: 'resetSlot',
         MODULE.UNLOAD: 'resetSlot'})

    def showModuleInfo(self):
        if self._equipmentCD is not None and g_currentVehicle.isPresent():
            shared_events.showModuleInfo(self._equipmentCD, g_currentVehicle.item.descriptor)
        return

    def resetSlot(self):
        self.fireEvent(events.TechnicalMaintenanceEvent(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, ctx={'eqCD': self._equipmentCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _initFlashValues(self, ctx):
        self._equipmentCD = ctx.equipmentCD
        self._isCanceled = bool(ctx.isCanceled)

    def _clearFlashValues(self):
        self._equipmentCD = None
        self._isCanceled = None
        return

    def _generateOptions(self, ctx=None):
        options = [self._makeItem(MODULE.INFO, MENU.contextmenu(MODULE.INFO))]
        if self._isCanceled:
            options.append(self._makeItem(MODULE.CANCEL_BUY, MENU.contextmenu(MODULE.CANCEL_BUY)))
        else:
            options.append(self._makeItem(MODULE.UNLOAD, MENU.contextmenu(MODULE.UNLOAD)))
        return options


class SimpleVehicleCMHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)

    def getVehCD(self):
        raise NotImplementedError

    def getVehInvID(self):
        raise NotImplementedError

    def showVehicleInfo(self):
        shared_events.showVehicleInfo(self.getVehCD())

    def showVehicleStats(self):
        shared_events.showVehicleStats(self.getVehCD())

    def sellVehicle(self):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle:
            shared_events.showVehicleSellDialog(self.getVehInvID())

    def buyVehicle(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self.getVehCD())

    def _generateOptions(self, ctx=None):
        return []


class VehicleContextMenuHandler(SimpleVehicleCMHandler):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, cmProxy, ctx=None):
        super(VehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.SELL: 'sellVehicle',
         VEHICLE.RESEARCH: 'toResearch',
         VEHICLE.CHECK: 'checkFavoriteVehicle',
         VEHICLE.UNCHECK: 'uncheckFavoriteVehicle',
         VEHICLE.STATS: 'showVehicleStats',
         VEHICLE.BUY: 'buyVehicle',
         VEHICLE.COMPARE: 'compareVehicle'})

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getVehCD(self):
        return self.vehCD

    def getVehInvID(self):
        return self.vehInvID

    def toResearch(self):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle is not None:
            shared_events.showResearchView(vehicle.intCD)
        else:
            LOG_ERROR("Can't go to Research because id for current vehicle is None")
        return

    def checkFavoriteVehicle(self):
        self.__favoriteVehicle(True)

    def uncheckFavoriteVehicle(self):
        self.__favoriteVehicle(False)

    def compareVehicle(self):
        self.comparisonBasket.addVehicle(self.vehCD)

    def _initFlashValues(self, ctx):
        self.vehInvID = int(ctx.inventoryId)
        vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
        self.vehCD = vehicle.intCD if vehicle is not None else None
        return

    def _clearFlashValues(self):
        self.vehInvID = None
        self.vehCD = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        vehicleWasInBattle = False
        accDossier = self.itemsCache.items.getAccountDossier(None)
        if vehicle is None:
            return options
        else:
            isEventVehicle = vehicle.isOnlyForEventBattles
            if accDossier:
                wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
                wasInBattleSet.update(accDossier.getGlobalMapStats().getVehicles().keys())
                if vehicle.intCD in wasInBattleSet:
                    vehicleWasInBattle = True
            if vehicle is not None:
                options.extend([self._makeItem(VEHICLE.INFO, MENU.contextmenu(VEHICLE.INFO)), self._makeItem(VEHICLE.STATS, MENU.contextmenu(VEHICLE.STATS), {'enabled': vehicleWasInBattle}), self._makeSeparator()])
                self._manageVehCompareOptions(options, vehicle)
                if self.prbDispatcher is not None:
                    isNavigationEnabled = not self.prbDispatcher.getFunctionalState().isNavigationDisabled()
                else:
                    isNavigationEnabled = True
                options.append(self._makeItem(VEHICLE.RESEARCH, MENU.contextmenu(VEHICLE.RESEARCH), {'enabled': isNavigationEnabled}))
                if vehicle.isRented:
                    if not vehicle.isPremiumIGR:
                        items = self.itemsCache.items
                        enabled = vehicle.mayObtainWithMoneyExchange(items.stats.money, items.shop.exchangeRate)
                        label = MENU.CONTEXTMENU_RESTORE if vehicle.isRestoreAvailable() else MENU.CONTEXTMENU_BUY
                        options.append(self._makeItem(VEHICLE.BUY, label, {'enabled': enabled}))
                    options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.REMOVE), {'enabled': vehicle.canSell and vehicle.rentalIsOver}))
                else:
                    options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.SELL), {'enabled': vehicle.canSell and not isEventVehicle}))
                if vehicle.isFavorite:
                    options.append(self._makeItem(VEHICLE.UNCHECK, MENU.contextmenu(VEHICLE.UNCHECK)))
                else:
                    options.append(self._makeItem(VEHICLE.CHECK, MENU.contextmenu(VEHICLE.CHECK), {'enabled': not isEventVehicle}))
            return options

    def _manageVehCompareOptions(self, options, vehicle):
        if self.comparisonBasket.isEnabled():
            options.append(self._makeItem(VEHICLE.COMPARE, MENU.contextmenu(VEHICLE.COMPARE), {'enabled': self.comparisonBasket.isReadyToAdd(vehicle)}))

    @process
    def __favoriteVehicle(self, isFavorite):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle is not None:
            result = yield VehicleFavoriteProcessor(vehicle, bool(isFavorite)).request()
            if not result.success:
                LOG_ERROR('Cannot set selected vehicle as favorite due to following error: ', result.userMsg)
        return
