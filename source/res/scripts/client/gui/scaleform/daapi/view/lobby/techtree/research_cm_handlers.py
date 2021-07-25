# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/research_cm_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import MODULE, SimpleVehicleCMHandler, VEHICLE
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE, UnlockProps
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shop import canBuyGoldForVehicleThroughWeb
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket, IBootcampController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED

class ResearchItemContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):
    _itemsCache = dependency.descriptor(IItemsCache)
    _bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, cmProxy, ctx=None):
        super(ResearchItemContextMenuHandler, self).__init__(cmProxy, ctx, {MODULE.INFO: 'showModuleInfo',
         MODULE.UNLOCK: 'unlockModule',
         MODULE.BUY_AND_EQUIP: 'buyModule',
         MODULE.EQUIP: 'equipModule',
         MODULE.SELL: 'sellModule'})
        self.__skipConfirm = self._bootcampController.isInBootcamp()

    def showModuleInfo(self):
        vehicle = self._itemsCache.items.getItemByCD(self._rootCD)
        if vehicle:
            shared_events.showModuleInfo(self._nodeCD, vehicle.descriptor)

    def unlockModule(self):
        vehicle = self._itemsCache.items.getItemByCD(self._rootCD)
        unlockIdx, xpCost, required = vehicle.getUnlockDescrByIntCD(self._nodeCD)
        unlockProps = UnlockProps(self._rootCD, unlockIdx, xpCost, required, 0, xpCost)
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, self._nodeCD, unlockProps, skipConfirm=self.__skipConfirm)

    def buyModule(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_AND_SELL_ITEM, self._nodeCD, self._rootCD, skipConfirm=self.__skipConfirm)

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
        rootItem = self._itemsCache.items.getItemByCD(self._rootCD)
        return rootItem.isInInventory and not rootItem.isLocked and not rootItem.repairCost


class ResearchVehicleContextMenuHandler(SimpleVehicleCMHandler):
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, cmProxy, ctx=None):
        super(ResearchVehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.PREVIEW: 'showVehiclePreview',
         VEHICLE.UNLOCK: 'unlockVehicle',
         VEHICLE.BUY: 'buyVehicle',
         VEHICLE.SELL: 'sellVehicle',
         VEHICLE.SELECT: 'selectVehicle',
         VEHICLE.STATS: 'showVehicleStats',
         VEHICLE.COMPARE: 'compareVehicle',
         VEHICLE.NATION_CHANGE: 'changeVehicleNation'})

    def getVehCD(self):
        return self._nodeCD

    def getVehInvID(self):
        return self._nodeInvID

    def unlockVehicle(self):
        vehicleCD = self._nodeCD
        level = self.itemsCache.items.getItemByCD(vehicleCD).level
        unlockProps = g_techTreeDP.getUnlockProps(vehicleCD, level)
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, vehicleCD, unlockProps)

    def showVehiclePreview(self):
        shared_events.showVehiclePreview(self._nodeCD, self._previewAlias)

    def selectVehicle(self):
        shared_events.selectVehicleInHangar(self._nodeCD)

    def compareVehicle(self):
        self._comparisonBasket.addVehicle(self._nodeCD)

    def buyVehicle(self):
        vehicle = self.itemsCache.items.getItemByCD(self._nodeCD)
        if canBuyGoldForVehicleThroughWeb(vehicle):
            shared_events.showVehicleBuyDialog(vehicle)
        else:
            super(ResearchVehicleContextMenuHandler, self).buyVehicle()

    def changeVehicleNation(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, self._nodeCD)

    def _initFlashValues(self, ctx):
        self._nodeCD = int(ctx.vehCD)
        self._nodeState = int(ctx.nodeState)
        vehicle = self.itemsCache.items.getItemByCD(self._nodeCD)
        self._previewAlias = getattr(ctx, 'previewAlias', VIEW_ALIAS.LOBBY_TECHTREE)
        self._nodeInvID = vehicle.invID if vehicle is not None else None
        return

    def _clearFlashValues(self):
        self._nodeCD = None
        self._nodeState = None
        self._nodeInvID = None
        return

    def _generateOptions(self, ctx=None):
        vehicle = self.itemsCache.items.getItemByCD(self._nodeCD)
        options = [self._makeItem(VEHICLE.INFO, MENU.CONTEXTMENU_VEHICLEINFOEX)]
        if vehicle.isPreviewAllowed():
            options.append(self._makeItem(VEHICLE.PREVIEW, MENU.CONTEXTMENU_SHOWVEHICLEPREVIEW, {'enabled': self._hangarSpace.spaceInited}))
        if NODE_STATE.isWasInBattle(self._nodeState):
            options.append(self._makeItem(VEHICLE.STATS, MENU.CONTEXTMENU_SHOWVEHICLESTATISTICS))
        self._manageVehCompareItem(options, vehicle)
        options.append(self._makeSeparator())
        if vehicle.isUnlocked:
            if not vehicle.isPremiumIGR and (not vehicle.isInInventory or vehicle.isRented):
                if vehicle.isRestoreAvailable():
                    label = MENU.CONTEXTMENU_RESTORE
                elif vehicle.canTradeIn:
                    label = MENU.CONTEXTMENU_BUYORTRADEIN
                else:
                    label = MENU.CONTEXTMENU_BUY
                options.append(self._makeItem(VEHICLE.BUY, label, {'enabled': NODE_STATE.isAvailable2Buy(self._nodeState)}))
        else:
            options.append(self._makeItem(VEHICLE.UNLOCK, MENU.CONTEXTMENU_UNLOCK, {'enabled': NODE_STATE.isAvailable2Unlock(self._nodeState) and not NODE_STATE.isPremium(self._nodeState)}))
        if vehicle.hasNationGroup:
            if vehicle.isInInventory or vehicle.isRented:
                isNationChangeAvailable = vehicle.isNationChangeAvailable
                nationChangeIsNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
            else:
                isNationChangeAvailable = False
                nationChangeIsNew = False
            options.append(self._makeItem(VEHICLE.NATION_CHANGE, MENU.CONTEXTMENU_NATIONCHANGE, {'enabled': isNationChangeAvailable,
             'isNew': nationChangeIsNew}))
        if not vehicle.isPremiumIGR:
            isAvailable2SellOrRemove = NODE_STATE.isAvailable2Sell(self._nodeState)
            if isAvailable2SellOrRemove:
                options.append(self._makeItem(VEHICLE.SELL, MENU.CONTEXTMENU_VEHICLEREMOVE if vehicle.isRented else MENU.CONTEXTMENU_SELL, {'enabled': isAvailable2SellOrRemove}))
        options.extend([self._makeSeparator(), self._makeItem(VEHICLE.SELECT, MENU.CONTEXTMENU_SELECTVEHICLEINHANGAR, {'enabled': NODE_STATE.inInventory(self._nodeState) or NODE_STATE.isRentalOver(self._nodeState)})])
        return options

    def _manageVehCompareItem(self, optionsRef, vehicle):
        if self._comparisonBasket.isEnabled():
            optionsRef.append(self._makeItem(VEHICLE.COMPARE, MENU.contextmenu(VEHICLE.COMPARE), {'enabled': self._comparisonBasket.isReadyToAdd(vehicle)}))


class BlueprintVehicleContextMenuHandler(SimpleVehicleCMHandler):
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, cmProxy, ctx=None):
        super(BlueprintVehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.UNLOCK: 'unlockVehicle',
         VEHICLE.BLUEPRINT: 'showVehicleBlueprint'})

    def getVehCD(self):
        return self._nodeCD

    def getVehInvID(self):
        return None

    def unlockVehicle(self):
        level = self.itemsCache.items.getItemByCD(self._nodeCD).level
        unlockProps = g_techTreeDP.getUnlockProps(self._nodeCD, level)
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, self._nodeCD, unlockProps)

    def showVehicleBlueprint(self):
        shared_events.showBlueprintView(self._nodeCD)

    def _initFlashValues(self, ctx):
        self._nodeCD = int(ctx.vehCD)
        self._nodeState = int(ctx.nodeState)
        self._previewAlias = getattr(ctx, 'previewAlias', VIEW_ALIAS.LOBBY_TECHTREE)

    def _clearFlashValues(self):
        self._nodeCD = None
        self._nodeState = None
        self._previewAlias = None
        return

    def _generateOptions(self, ctx=None):
        options = [self._makeItem(VEHICLE.BLUEPRINT, MENU.CONTEXTMENU_GOTOBLUEPRINT), self._makeItem(VEHICLE.UNLOCK, MENU.CONTEXTMENU_UNLOCK, {'enabled': NODE_STATE.isAvailable2Unlock(self._nodeState)})]
        return options
