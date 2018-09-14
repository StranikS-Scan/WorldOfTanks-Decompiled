# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/research_cm_handlers.py
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.managers.context_menu.AbstractContextMenuHandler import AbstractContextMenuHandler
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE, UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import MODULE, SimpleVehicleCMHandler, VEHICLE
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import g_itemsCache, event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory

class ResearchItemContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx=None):
        super(ResearchItemContextMenuHandler, self).__init__(cmProxy, ctx, {MODULE.INFO: 'showModuleInfo',
         MODULE.UNLOCK: 'unlockModule',
         MODULE.BUY_AND_EQUIP: 'buyModule',
         MODULE.EQUIP: 'equipModule',
         MODULE.SELL: 'sellModule'})

    def fini(self):
        super(ResearchItemContextMenuHandler, self).fini()

    def showModuleInfo(self):
        vehicle = g_itemsCache.items.getItemByCD(self._rootCD)
        if vehicle:
            shared_events.showModuleInfo(self._nodeCD, vehicle.descriptor)

    def unlockModule(self):
        vehicle = g_itemsCache.items.getItemByCD(self._rootCD)
        if vehicle:
            unlockIdx, xpCost, _ = vehicle.getUnlockDescrByIntCD(self._nodeCD)
            ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, self._nodeCD, self._rootCD, unlockIdx, xpCost)

    def buyModule(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM, self._nodeCD, self._rootCD)

    def equipModule(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.INSTALL_ITEM, self._nodeCD, self._rootCD)

    def sellModule(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.SELL_ITEM, self._nodeCD)

    def _initFlashValues(self, ctx):
        self._nodeCD = int(ctx.nodeCD)
        self._rootCD = int(ctx.rootCD)
        self._nodeState = int(ctx.nodeState)

    def _clearFlashValues(self):
        self._nodeCD = None
        self._rootCD = None
        self._nodeState = None
        return

    def _generateOptions(self, ctx=None):
        options = [self._makeItem(MODULE.INFO, MENU.contextmenu(MODULE.INFO)), self._makeSeparator(), self._makeItem(MODULE.UNLOCK, MENU.contextmenu(MODULE.UNLOCK), {'enabled': NODE_STATE.isAvailable2Unlock(self._nodeState)})]
        if NODE_STATE.isUnlocked(self._nodeState):
            if NODE_STATE.inInventory(self._nodeState) or NODE_STATE.isInstalled(self._nodeState):
                options.extend([self._makeItem(MODULE.EQUIP, MENU.contextmenu(MODULE.EQUIP), {'enabled': self._isAvailable2Install()}), self._makeSeparator(), self._makeItem(MODULE.SELL, MENU.CONTEXTMENU_SELLFROMINVENTORY, {'enabled': not NODE_STATE.isInstalled(self._nodeState)})])
            else:
                options.extend([self._makeItem(MODULE.BUY_AND_EQUIP, MENU.CONTEXTMENU_BUYANDEQUIP, {'enabled': self._isAvailable2Buy()}), self._makeSeparator(), self._makeItem(MODULE.SELL, MENU.CONTEXTMENU_SELLFROMINVENTORY, {'enabled': NODE_STATE.isAvailable2Sell(self._nodeState)})])
        else:
            options.extend([self._makeItem(MODULE.BUY_AND_EQUIP, MENU.CONTEXTMENU_BUYANDEQUIP, {'enabled': False}), self._makeSeparator(), self._makeItem(MODULE.SELL, MENU.CONTEXTMENU_SELLFROMINVENTORY, {'enabled': False})])
        return options

    def _isAvailable2Install(self):
        return not NODE_STATE.isInstalled(self._nodeState) and NODE_STATE.inInventory(self._nodeState) and self._canInstallItems()

    def _isAvailable2Buy(self):
        return not NODE_STATE.isInstalled(self._nodeState) and NODE_STATE.isAvailable2Buy(self._nodeState) and self._canInstallItems()

    def _canInstallItems(self):
        rootItem = g_itemsCache.items.getItemByCD(self._rootCD)
        return rootItem.isInInventory and not rootItem.isLocked and not rootItem.repairCost


class ResearchVehicleContextMenuHandler(SimpleVehicleCMHandler):

    def __init__(self, cmProxy, ctx=None):
        super(ResearchVehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.UNLOCK: 'unlockVehicle',
         VEHICLE.BUY: 'buyVehicle',
         VEHICLE.SELL: 'sellVehicle',
         VEHICLE.SELECT: 'selectVehicle',
         VEHICLE.STATS: 'showVehicleStats'})

    def getVehCD(self):
        return self._nodeCD

    def getVehInvID(self):
        return self._nodeInvID

    def unlockVehicle(self):
        stats = g_itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        unlockKwargs = unlockStats._asdict()
        _, unlockProps = g_techTreeDP.isNext2Unlock(self._nodeCD, **unlockKwargs)
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, self._nodeCD, unlockProps.parentID, unlockProps.unlockIdx, unlockProps.xpCost)

    def selectVehicle(self):
        shared_events.selectVehicleInHangar(self._nodeCD)

    def _initFlashValues(self, ctx):
        self._nodeCD = int(ctx.nodeCD)
        self._rootCD = int(ctx.rootCD)
        self._nodeState = int(ctx.nodeState)
        vehicle = g_itemsCache.items.getItemByCD(self._nodeCD)
        self._nodeInvID = vehicle.invID if vehicle is not None else None
        return

    def _clearFlashValues(self):
        self._nodeCD = None
        self._rootCD = None
        self._nodeState = None
        self._nodeInvID = None
        return

    def _generateOptions(self, ctx=None):
        vehicle = g_itemsCache.items.getItemByCD(self._nodeCD)
        options = [self._makeItem(VEHICLE.INFO, MENU.CONTEXTMENU_VEHICLEINFOEX),
         self._makeItem(VEHICLE.STATS, MENU.CONTEXTMENU_SHOWVEHICLESTATISTICS, {'enabled': NODE_STATE.isWasInBattle(self._nodeState)}),
         self._makeSeparator(),
         self._makeItem(VEHICLE.UNLOCK, MENU.CONTEXTMENU_UNLOCK, {'enabled': NODE_STATE.isAvailable2Unlock(self._nodeState) and not NODE_STATE.isPremium(self._nodeState)})]
        if not vehicle.isPremiumIGR:
            options.extend([self._makeItem(VEHICLE.BUY, MENU.CONTEXTMENU_BUY, {'enabled': NODE_STATE.isAvailable2Buy(self._nodeState)}),
             self._makeItem(VEHICLE.SELL, MENU.CONTEXTMENU_VEHICLEREMOVE if vehicle.isRented else MENU.CONTEXTMENU_SELL, {'enabled': NODE_STATE.isAvailable2Sell(self._nodeState)}),
             self._makeSeparator(),
             self._makeItem(VEHICLE.SELECT, MENU.CONTEXTMENU_SELECTVEHICLEINHANGAR, {'enabled': (NODE_STATE.inInventory(self._nodeState) or NODE_STATE.isRentalOver(self._nodeState)) and NODE_STATE.isVehicleCanBeChanged(self._nodeState)})])
        return options
