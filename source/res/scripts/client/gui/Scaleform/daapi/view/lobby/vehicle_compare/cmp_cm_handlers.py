# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_cm_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import SimpleVehicleCMHandler, VEHICLE
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.ingame_shop import canBuyGoldForVehicleThroughWeb
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket

class _OPT_IDS(object):
    COPY = 'copy'


class CommonContextMenuHandler(SimpleVehicleCMHandler):

    def __init__(self, cmProxy, ctx=None, handlers=None):
        self.__itemIndexInBasket = -1
        if handlers is not None:
            handlers.update({VEHICLE.PREVIEW: 'showVehiclePreview',
             VEHICLE.SELL: 'sellVehicle',
             VEHICLE.RESEARCH: 'researchVehicle',
             VEHICLE.BUY: 'buyVehicle',
             VEHICLE.SELECT: 'selectVehicleInHangar'})
        super(CommonContextMenuHandler, self).__init__(cmProxy, ctx, handlers)
        return

    def showVehiclePreview(self):
        shared_events.showVehiclePreview(self.vehCD, VIEW_ALIAS.VEHICLE_COMPARE)

    def selectVehicleInHangar(self):
        shared_events.selectVehicleInHangar(self.vehCD)

    def sellVehicle(self):
        shared_events.showVehicleSellDialog(self.__getVehicle(self.vehCD).invID)

    def buyVehicle(self):
        vehicle = self.itemsCache.items.getItemByCD(self.vehCD)
        if canBuyGoldForVehicleThroughWeb(vehicle):
            shared_events.showVehicleBuyDialog(vehicle)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self.vehCD)

    def researchVehicle(self):
        vehicle = self.itemsCache.items.getItemByCD(self.vehCD)
        unlockProps = g_techTreeDP.getUnlockProps(vehicle.intCD, vehicle.level)
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, self.vehCD, unlockProps)

    def getVehCD(self):
        return self.vehCD

    def _generateOptions(self, ctx=None):
        options = []
        vehicle = self.__getVehicle(self.vehCD)
        self._manageStartOptions(options, vehicle)
        if vehicle.isPurchased:
            options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.SELL), {'enabled': vehicle.canSell}))
        elif vehicle.isUnlocked:
            items = self.itemsCache.items
            if vehicle.isRestoreAvailable():
                label = MENU.CONTEXTMENU_RESTORE
            elif vehicle.canTradeIn:
                label = MENU.CONTEXTMENU_BUYORTRADEIN
            else:
                label = MENU.CONTEXTMENU_BUY
            if canBuyGoldForVehicleThroughWeb(vehicle):
                btnEnabled = True
            else:
                btnEnabled = vehicle.mayObtainWithMoneyExchange(items.stats.money, items.shop.exchangeRate)
            options.append(self._makeItem(VEHICLE.BUY, label, {'enabled': btnEnabled}))
        else:
            isNextToUnlock, isXpEnough = g_techTreeDP.isVehicleAvailableToUnlock(self.vehCD)
            isAvailableToUnlock = isNextToUnlock and isXpEnough
            options.append(self._makeItem(VEHICLE.RESEARCH, MENU.contextmenu(VEHICLE.RESEARCH), {'enabled': isAvailableToUnlock}))
        self._manageEndOptions(options, vehicle)
        return options

    def _manageStartOptions(self, options, vehicle):
        if vehicle.isPreviewAllowed():
            options.append(self._makeItem(VEHICLE.PREVIEW, MENU.CONTEXTMENU_SHOWVEHICLEPREVIEW))

    def _manageEndOptions(self, options, vehicle):
        if vehicle.isInInventory:
            options.append(self._makeItem(VEHICLE.SELECT, MENU.CONTEXTMENU_SELECTVEHICLEINHANGAR))

    def _initFlashValues(self, ctx):
        self.vehCD = int(ctx.id)

    @classmethod
    def __getVehicle(cls, intCD):
        return cls.itemsCache.items.getItemByCD(intCD)


class VehicleCompareContextMenuHandler(CommonContextMenuHandler):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, cmProxy, ctx=None):
        handlers = {VEHICLE.STATS: 'showVehicleStats',
         _OPT_IDS.COPY: 'copyComparedVehicle'}
        super(VehicleCompareContextMenuHandler, self).__init__(cmProxy, ctx, handlers)

    def copyComparedVehicle(self):
        self.comparisonBasket.cloneVehicle(self.__itemIndexInBasket)

    def _manageStartOptions(self, options, vehicle):
        options.append(self._makeItem(_OPT_IDS.COPY, VEH_COMPARE.MENU_CLONEFORCOMPARE, {'enabled': not self.comparisonBasket.isFull()}))
        if vehicle.isInInventory:
            options.append(self._makeItem(VEHICLE.SELECT, VEH_COMPARE.VEHICLECOMPAREVIEW_TOHANGAR))
        elif vehicle.isPreviewAllowed():
            options.append(self._makeItem(VEHICLE.PREVIEW, MENU.CONTEXTMENU_SHOWVEHICLEPREVIEW))

    def _manageEndOptions(self, options, vehicle):
        pass

    def _initFlashValues(self, ctx):
        super(VehicleCompareContextMenuHandler, self)._initFlashValues(ctx)
        self.__itemIndexInBasket = int(ctx.index)
