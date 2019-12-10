# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/tabs/inventory.py
from constants import IS_RENTALS_ENABLED
from gui.Scaleform.daapi.view.lobby.store.tabs import StoreItemsTab, StoreModuleTab, StoreVehicleTab, StoreShellTab, StoreArtefactTab, StoreOptionalDeviceTab, StoreEquipmentTab, StoreBattleBoosterTab
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle, getVehicleStateIcon
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers.i18n import makeString
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup

class InventoryItemsTab(StoreItemsTab):

    def _getItemPrices(self, item):
        return item.sellPrices

    def _getItemActionData(self, item):
        return packItemActionTooltipData(item, False) if item.sellPrices.itemPrice.isActionPrice() and not item.isRented else None

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.EMPTY

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        if 'onVehicle' in extra:
            requestCriteria |= ~REQ_CRITERIA.CUSTOM(lambda item: not item.getInstalledVehicles(invVehicles) and item.inventoryCount == 0)
        else:
            requestCriteria |= REQ_CRITERIA.INVENTORY
        return requestCriteria

    def _getDiscountCriteria(self):
        return REQ_CRITERIA.DISCOUNT_SELL if self._actionsSelected else REQ_CRITERIA.EMPTY

    def _getStatusParams(self, item):
        disabled = False
        statusMessage = ''
        if not item.isInInventory:
            statusMessage = makeString(MENU.INVENTORY_ERRORS_RESERVED)
            disabled = True
        return (statusMessage, disabled or not item.isForSale)

    def _getItemStatusLevel(self, item):
        return Vehicle.VEHICLE_STATE_LEVEL.INFO

    def _isItemOnDiscount(self, item):
        return item.sellPrices.itemPrice.isActionPrice()


class InventoryModuleTab(InventoryItemsTab, StoreModuleTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryModuleTab, self)._getRequestCriteria(invVehicles)
        extra = self._filterData['extra']
        fitsType = self._filterData['fitsType']
        requestTypeIds = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE_FOR_MULTI_NATION([vehicle], requestTypeIds)
            if not vehicle.hasTurrets:
                requestCriteria |= ~REQ_CRITERIA.IN_CD_LIST([vehicle.turret.intCD])
        elif fitsType == 'myVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE_FOR_MULTI_NATION(invVehicles, requestTypeIds)
        else:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.SUITABLE_FOR_MULTI_NATION(invVehicles, requestTypeIds)
        return self._getExtraCriteria(extra, requestCriteria, invVehicles)


class InventoryVehicleTab(InventoryItemsTab, StoreVehicleTab):

    def _getItemInventoryID(self, item):
        return item.invID if item.isInInventory else None

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryVehicleTab, self)._getRequestCriteria(invVehicles)
        requestCriteria |= REQ_CRITERIA.INVENTORY
        requestCriteria |= REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
        requestCriteria |= self._getVehicleRiterias(self._filterData['selectedTypes'], self._filterData['selectedLevels'])
        extra = self._filterData['extra']
        return self._getExtraCriteria(extra, requestCriteria, invVehicles)

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        if 'brocken' not in extra:
            requestCriteria |= ~REQ_CRITERIA.CUSTOM(lambda item: item.repairCost > 0)
        if 'locked' not in extra:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.LOCKED
        if 'premiumIGR' not in extra:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if IS_RENTALS_ENABLED and 'rentals' not in extra:
            requestCriteria |= ~REQ_CRITERIA.CUSTOM(lambda item: item.isRented and not item.isPremiumIGR)
        return requestCriteria

    def _getStatusParams(self, item):
        disable = False
        statusMessage = ''
        state = item.getState()[0]
        isStateSuitable = state in (Vehicle.VEHICLE_STATE.RENTAL_IS_OVER, Vehicle.VEHICLE_STATE.IGR_RENTAL_IS_OVER, Vehicle.VEHICLE_STATE.RENTABLE_AGAIN)
        isExcludedState = state in (Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT,)
        if isStateSuitable or not isExcludedState and not item.canSell:
            statusMessage = makeString('#menu:store/vehicleStates/%s' % state)
            disable = not item.canSell
        return (statusMessage, disable)

    def _getStatusImg(self, item):
        return getVehicleStateIcon(item.getState()[0]) if item.isUnlocked else ''

    def _getItemStatusLevel(self, item):
        return item.getState()[1]


class InventoryShellTab(InventoryItemsTab, StoreShellTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryShellTab, self)._getRequestCriteria(invVehicles)
        requestCriteria |= REQ_CRITERIA.INVENTORY
        requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type in self._filterData['itemTypes'])
        fitsType = self._filterData['fitsType']
        if fitsType == 'myVehicleGun':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            shellsList = [ x.intCD for x in vehicle.gun.defaultAmmo ]
            if vehicle.hasNationGroup:
                targetVehicleCD = iterVehTypeCDsInNationGroup(vehicle.intCD).next()
                targetVehicle = self._items.getItemByCD(targetVehicleCD)
                for ammo in targetVehicle.gun.defaultAmmo:
                    shellsList.append(ammo.intCD)

            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        elif fitsType == 'myVehiclesInventoryGuns':
            shellsList = set()
            myGuns = self._items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
            for gun in myGuns:
                shellsList.update((x.intCD for x in gun.defaultAmmo))

            for vehicle in invVehicles:
                shellsList.update((x.intCD for x in vehicle.gun.defaultAmmo))

            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        else:
            shellsList = set()
            myGuns = self._items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
            for gun in myGuns:
                shellsList.update((x.intCD for x in gun.defaultAmmo))

            for vehicle in invVehicles:
                shellsList.update((x.intCD for x in vehicle.gun.defaultAmmo))

            requestCriteria |= ~REQ_CRITERIA.IN_CD_LIST(shellsList)
        return requestCriteria


class InventoryArtefactTab(InventoryItemsTab, StoreArtefactTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryArtefactTab, self)._getRequestCriteria(invVehicles)
        fitsType = self._filterData['fitsType']
        itemTypeID = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE_FOR_MULTI_NATION([vehicle], [itemTypeID])
        elif fitsType == 'myVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE_FOR_MULTI_NATION(invVehicles, [itemTypeID])
        else:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.SUITABLE_FOR_MULTI_NATION(invVehicles, [itemTypeID])
        return self._getExtraCriteria(self._filterData['extra'], requestCriteria, invVehicles)


class InventoryOptionalDeviceTab(InventoryArtefactTab, StoreOptionalDeviceTab):

    def _getStatusParams(self, item):
        disabled = False
        statusMessage = ''
        if not item.isInInventory:
            if not item.descriptor.removable:
                statusMessage = makeString(MENU.INVENTORY_DEVICE_ERRORS_NOT_REMOVABLE)
                disabled = True
            else:
                statusMessage = makeString(MENU.INVENTORY_DEVICE_ERRORS_RESERVED)
                disabled = True
        return (statusMessage, disabled)


class InventoryEquipmentTab(StoreEquipmentTab, InventoryArtefactTab):
    pass


class InventoryBattleBoosterTab(StoreBattleBoosterTab, InventoryArtefactTab):

    def _getRequestCriteria(self, invVehicles):
        targetType = self._filterData['targetType']
        if targetType == STORE_CONSTANTS.FOR_EQUIPMENT_FIT:
            result = REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT
        elif targetType == STORE_CONSTANTS.FOR_CREW_FIT:
            result = REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT
        else:
            result = REQ_CRITERIA.BATTLE_BOOSTER.ALL
        return result | REQ_CRITERIA.INVENTORY
