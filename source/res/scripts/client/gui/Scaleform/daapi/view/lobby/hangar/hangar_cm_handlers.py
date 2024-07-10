# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_cm_handlers.py
from logging import getLogger
from typing import TYPE_CHECKING
import BigWorld
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getTradeInVehiclesUrl
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler, CM_BUY_COLOR
from gui.Scaleform.locale.MENU import MENU
from gui.impl.lobby.hangar.buy_vehicle_view import VehicleBuyActionTypes
from gui.prb_control import prbDispatcherProperty
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showShop, showTelecomRentalPage
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.processors.vehicle import VehicleFavoriteProcessor
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from skeletons.gui.game_control import IVehicleComparisonBasket, IEpicBattleMetaGameController, ITradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
_logger = getLogger(__name__)
if TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items import Vehicle

class MODULE(object):
    INFO = 'moduleInfo'
    CANCEL_BUY = 'cancelBuy'
    UNLOAD = 'unload'
    UNLOCK = 'unlock'
    EQUIP = 'equip'
    SELL = 'sell'
    BUY_AND_EQUIP = 'buyAndEquip'


class VEHICLE(object):
    EXCHANGE = 'exchange'
    INFO = 'vehicleInfo'
    PREVIEW = 'preview'
    STATS = 'showVehicleStatistics'
    UNLOCK = 'unlock'
    SELECT = 'selectVehicle'
    SELL = 'sell'
    BUY = 'buy'
    RESEARCH = 'vehicleResearch'
    POST_PROGRESSION = 'vehiclePostProgression'
    RENEW = 'vehicleRentRenew'
    REMOVE = 'vehicleRemove'
    CHECK = 'vehicleCheck'
    UNCHECK = 'vehicleUncheck'
    COMPARE = 'compare'
    BLUEPRINT = 'blueprint'
    NATION_CHANGE = 'nationChange'
    GO_TO_COLLECTION = 'goToCollection'
    TELECOM_RENT = 'telecomRent'


class TechnicalMaintenanceCMHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)

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
        equipment = self.itemsCache.items.getItemByCD(int(self._equipmentCD))
        if equipment is not None and equipment.isBuiltIn:
            return options
        else:
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
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self.getVehCD(), False, VehicleBuyActionTypes.BUY)

    def _generateOptions(self, ctx=None):
        return []


class VehicleContextMenuHandler(SimpleVehicleCMHandler):
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _epicController = dependency.descriptor(IEpicBattleMetaGameController)
    _tradeInController = dependency.descriptor(ITradeInController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, cmProxy, ctx=None):
        super(VehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.EXCHANGE: 'showVehicleExchange',
         VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.SELL: 'sellVehicle',
         VEHICLE.RESEARCH: 'toResearch',
         VEHICLE.POST_PROGRESSION: 'showPostProgression',
         VEHICLE.CHECK: 'checkFavoriteVehicle',
         VEHICLE.UNCHECK: 'uncheckFavoriteVehicle',
         VEHICLE.STATS: 'showVehicleStats',
         VEHICLE.BUY: 'buyVehicle',
         VEHICLE.COMPARE: 'compareVehicle',
         VEHICLE.NATION_CHANGE: 'changeVehicleNation',
         VEHICLE.GO_TO_COLLECTION: 'goToCollection',
         VEHICLE.TELECOM_RENT: 'showTelecomRent'})

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
            _logger.error('Can not go to Research because id for current vehicle is None')
        return

    def showPostProgression(self):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        shared_events.showVehPostProgressionView(vehicle.intCD)

    def showVehicleExchange(self):
        oldSellVeh = self._tradeInController.getSelectedVehicleToSell()
        self._tradeInController.selectVehicleToSell(self.vehCD)
        if not oldSellVeh or oldSellVeh.intCD != self.vehCD:
            self._tradeInController.selectVehicleToBuy(UNDEFINED_ITEM_CD)
        showShop(getTradeInVehiclesUrl())

    def checkFavoriteVehicle(self):
        self.__favoriteVehicle(True)

    def uncheckFavoriteVehicle(self):
        self.__favoriteVehicle(False)

    def compareVehicle(self):
        self._comparisonBasket.addVehicle(self.vehCD)

    def changeVehicleNation(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, self.vehCD)

    def goToCollection(self):
        vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
        shared_events.showCollectibleVehicles(vehicle.nationID)

    def showTelecomRent(self):
        showTelecomRentalPage()

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
        if vehicle is None or vehicle.isOnlyForFunRandomBattles:
            return options
        else:
            isEventVehicle = vehicle.isOnlyForEventBattles
            if accDossier:
                wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
                wasInBattleSet.update(accDossier.getGlobalMapStats().getVehicles().keys())
                if vehicle.intCD in wasInBattleSet:
                    vehicleWasInBattle = True
            if vehicle is not None:
                if vehicle.canTradeOff:
                    options.append(self._makeItem(VEHICLE.EXCHANGE, MENU.contextmenu(VEHICLE.EXCHANGE), {'enabled': vehicle.isReadyToTradeOff,
                     'textColor': CM_BUY_COLOR}))
                options.extend([self._makeItem(VEHICLE.INFO, MENU.contextmenu(VEHICLE.INFO)), self._makeItem(VEHICLE.STATS, MENU.contextmenu(VEHICLE.STATS), {'enabled': vehicleWasInBattle})])
                self._manageVehCompareOptions(options, vehicle)
                if self.prbDispatcher is not None:
                    isNavigationEnabled = not self.prbDispatcher.getFunctionalState().isNavigationDisabled()
                else:
                    isNavigationEnabled = True
                if not vehicle.isOnlyForEpicBattles:
                    options.append(self._makeItem(VEHICLE.RESEARCH, MENU.contextmenu(VEHICLE.RESEARCH), {'enabled': isNavigationEnabled}))
                if vehicle.isPostProgressionExists:
                    options.append(self._makeItem(VEHICLE.POST_PROGRESSION, MENU.contextmenu(VEHICLE.POST_PROGRESSION), {'enabled': isNavigationEnabled}))
                if vehicle.isCollectible:
                    options.append(self._makeItem(VEHICLE.GO_TO_COLLECTION, MENU.contextmenu(VEHICLE.GO_TO_COLLECTION), {'enabled': self._lobbyContext.getServerSettings().isCollectorVehicleEnabled()}))
                if vehicle.hasNationGroup:
                    isNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
                    options.append(self._makeItem(VEHICLE.NATION_CHANGE, MENU.CONTEXTMENU_NATIONCHANGE, {'enabled': vehicle.isNationChangeAvailable,
                     'isNew': isNew}))
                if vehicle.isRented:
                    canSell = vehicle.canSell and vehicle.rentalIsOver
                    if vehicle.isWotPlus and not self._lobbyContext.getServerSettings().isWoTPlusExclusiveVehicleEnabled():
                        canSell = False
                    if not vehicle.isPremiumIGR and not vehicle.isWotPlus:
                        items = self.itemsCache.items
                        enabled = vehicle.mayObtainWithMoneyExchange(items.stats.money, items.shop.exchangeRate)
                        label = MENU.CONTEXTMENU_RESTORE if vehicle.isRestoreAvailable() else MENU.CONTEXTMENU_BUY
                        options.append(self._makeItem(VEHICLE.BUY, label, {'enabled': enabled}))
                    if vehicle.isTelecomRent:
                        canSell = False
                        serverSettings = self._lobbyContext.getServerSettings()
                        isRentalEnabled = serverSettings.isTelecomRentalsEnabled()
                        isActive = BigWorld.player().telecomRentals.isActive()
                        options.append(self._makeItem(VEHICLE.TELECOM_RENT, MENU.contextmenu(VEHICLE.TELECOM_RENT), {'enabled': isRentalEnabled and isActive}))
                    options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.REMOVE), {'enabled': canSell}))
                else:
                    options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.SELL), {'enabled': vehicle.canSell and not isEventVehicle}))
                if vehicle.isFavorite:
                    options.append(self._makeItem(VEHICLE.UNCHECK, MENU.contextmenu(VEHICLE.UNCHECK)))
                else:
                    options.append(self._makeItem(VEHICLE.CHECK, MENU.contextmenu(VEHICLE.CHECK), {'enabled': not isEventVehicle}))
            return options

    def _manageVehCompareOptions(self, options, vehicle):
        if self._comparisonBasket.isEnabled():
            options.append(self._makeItem(VEHICLE.COMPARE, MENU.contextmenu(VEHICLE.COMPARE), {'enabled': self._comparisonBasket.isReadyToAdd(vehicle)}))

    @adisp_process
    def __favoriteVehicle(self, isFavorite):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle is not None:
            result = yield VehicleFavoriteProcessor(vehicle, bool(isFavorite)).request()
            if not result.success:
                _logger.error('Cannot set selected vehicle as favorite due to following error: %s', result.userMsg)
        return
