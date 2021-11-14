# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_cm_handlers.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import VEHICLE, SimpleVehicleCMHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.utils.vehicle_collector_helper import isAvailableForPurchase
from gui.shop import canBuyGoldForVehicleThroughWeb
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class PostProgressionContextMenuHandler(SimpleVehicleCMHandler):
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, cmProxy, ctx=None):
        super(PostProgressionContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.STATS: 'showVehicleStats',
         VEHICLE.COMPARE: 'compareVehicle',
         VEHICLE.BUY: 'buyVehicle',
         VEHICLE.SELL: 'sellVehicle',
         VEHICLE.NATION_CHANGE: 'changeVehicleNation',
         VEHICLE.SELECT: 'selectVehicle'})

    def getVehCD(self):
        return self._vehCD

    def getVehInvID(self):
        return self._vehInvID

    def compareVehicle(self):
        self.__cmpBasket.addVehicle(self._vehCD)

    def buyVehicle(self):
        vehicle = self.itemsCache.items.getItemByCD(self._vehCD)
        if canBuyGoldForVehicleThroughWeb(vehicle):
            shared_events.showVehicleBuyDialog(vehicle)
        else:
            super(PostProgressionContextMenuHandler, self).buyVehicle()

    def changeVehicleNation(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, self._vehCD)

    def selectVehicle(self):
        shared_events.selectVehicleInHangar(self._vehCD)

    def _initFlashValues(self, ctx):
        self._vehCD = int(ctx.vehCD)
        vehicle = self.__itemsCache.items.getItemByCD(self._vehCD)
        self._vehInvID = vehicle.invID if vehicle is not None else None
        return

    def _clearFlashValues(self):
        self._vehCD = None
        self._vehInvID = None
        return

    def _generateOptions(self, ctx=None):
        vehicle = self.__itemsCache.items.getItemByCD(self._vehCD)
        isPrevSeparator = False
        options = [self._makeItem(VEHICLE.INFO, MENU.CONTEXTMENU_VEHICLEINFOEX)]
        self.__addStatsOption(options, vehicle)
        self.__addCompareOption(options, vehicle)
        isPrevSeparator |= self.__addSeparator(options, isPrevSeparator)
        isPrevSeparator &= not self.__addBuyOption(options, vehicle)
        isPrevSeparator &= not self.__addNationChangeOption(options, vehicle)
        isPrevSeparator &= not self.__addSellOption(options, vehicle)
        self.__addSeparator(options, isPrevSeparator)
        self.__addSelectOption(options, vehicle)
        return options

    def __addStatsOption(self, options, vehicle):
        if self.__vehicleWasInBattle(vehicle):
            options.append(self._makeItem(VEHICLE.STATS, MENU.CONTEXTMENU_SHOWVEHICLESTATISTICS))

    def __addCompareOption(self, options, vehicle):
        if self.__cmpBasket.isEnabled():
            options.append(self._makeItem(VEHICLE.COMPARE, MENU.contextmenu(VEHICLE.COMPARE), {'enabled': self.__cmpBasket.isReadyToAdd(vehicle)}))

    def __addBuyOption(self, options, vehicle):
        if vehicle.isPremiumIGR or vehicle.isPurchased or not (vehicle.isUnlocked or vehicle.isCollectible):
            return False
        label = MENU.CONTEXTMENU_BUY
        if vehicle.isRestoreAvailable():
            label = MENU.CONTEXTMENU_RESTORE
        elif vehicle.canTradeIn:
            label = MENU.CONTEXTMENU_BUYORTRADEIN
        itemsRequester = self.__itemsCache.items
        btnEnabled = vehicle.mayObtainWithMoneyExchange(itemsRequester.stats.money, itemsRequester.shop.exchangeRate)
        if vehicle.isCollectible and not self.__isCollectibleVehicleEnabled(vehicle):
            btnEnabled = False
        elif canBuyGoldForVehicleThroughWeb(vehicle):
            btnEnabled = True
        options.append(self._makeItem(VEHICLE.BUY, label, {'enabled': btnEnabled}))
        return True

    def __addSellOption(self, options, vehicle):
        if vehicle.isPremiumIGR or not vehicle.canSell or vehicle.isTelecomRent:
            return False
        options.append(self._makeItem(VEHICLE.SELL, MENU.CONTEXTMENU_VEHICLEREMOVE if vehicle.isRented else MENU.CONTEXTMENU_SELL))
        return True

    def __addNationChangeOption(self, options, vehicle):
        if not vehicle.hasNationGroup:
            return False
        isNationChangeAvailable = nationChangeIsNew = False
        if vehicle.isInInventory or vehicle.isRented:
            isNationChangeAvailable = vehicle.isNationChangeAvailable
            nationChangeIsNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
        options.append(self._makeItem(VEHICLE.NATION_CHANGE, MENU.CONTEXTMENU_NATIONCHANGE, {'enabled': isNationChangeAvailable,
         'isNew': nationChangeIsNew}))
        return True

    def __addSelectOption(self, options, vehicle):
        options.append(self._makeItem(VEHICLE.SELECT, MENU.CONTEXTMENU_SELECTVEHICLEINHANGAR, {'enabled': vehicle.isInInventory or vehicle.rentalIsOver}))
        return True

    def __addSeparator(self, options, isPrevSeparator):
        separatorAdded = False
        if not isPrevSeparator:
            options.append(self._makeSeparator())
            separatorAdded = True
        return separatorAdded

    def __isCollectibleVehicleEnabled(self, vehicle):
        return self.__lobbyContext.getServerSettings().isCollectorVehicleEnabled() and isAvailableForPurchase(vehicle)

    def __vehicleWasInBattle(self, vehicle):
        accDossier = self.__itemsCache.items.getAccountDossier()
        wasInBattleSet = set()
        if accDossier:
            wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
            wasInBattleSet.update(accDossier.getGlobalMapStats().getVehicles().keys())
        return vehicle.intCD in wasInBattleSet
