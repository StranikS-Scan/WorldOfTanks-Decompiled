# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/tabs/inventory.py
from constants import IS_RENTALS_ENABLED
from gui.Scaleform.daapi.view.lobby.store.tabs import StoreItemsTab, StoreModuleTab, StoreVehicleTab, StoreShellTab, StoreArtefactTab, StoreOptionalDeviceTab, StoreEquipmentTab
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers.i18n import makeString

class InventoryItemsTab(StoreItemsTab):

    def _getItemPrice(self, item):
        return item.sellPrice

    def _getItemActionData(self, item):
        return packItemActionTooltipData(item, False) if item.sellPrice != item.defaultSellPrice and not item.isRented else None

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.EMPTY

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        if 'onVehicle' in extra:
            requestCriteria |= ~REQ_CRITERIA.CUSTOM(lambda item: len(item.getInstalledVehicles(invVehicles)) == 0 and item.inventoryCount == 0)
        else:
            requestCriteria |= REQ_CRITERIA.INVENTORY
        return requestCriteria

    def _getStatusParams(self, item):
        disabled = False
        statusMessage = ''
        if not item.isInInventory:
            statusMessage = makeString(MENU.INVENTORY_ERRORS_RESERVED)
            disabled = True
        return (statusMessage, disabled)

    def _getItemStatusLevel(self, item):
        return Vehicle.VEHICLE_STATE_LEVEL.INFO


class InventoryModuleTab(InventoryItemsTab, StoreModuleTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryModuleTab, self)._getRequestCriteria(invVehicles)
        extra = self._filterData['extra']
        fitsType = self._filterData['fitsType']
        requestTypeIds = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], requestTypeIds)
            if not vehicle.hasTurrets:
                requestCriteria |= ~REQ_CRITERIA.IN_CD_LIST([vehicle.turret.intCD])
        elif fitsType == 'myVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, requestTypeIds)
        else:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, requestTypeIds)
        return self._getExtraCriteria(extra, requestCriteria, invVehicles)


class InventoryVehicleTab(InventoryItemsTab, StoreVehicleTab):

    def _getItemInventoryID(self, item):
        return item.invID if item.isInInventory else None

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryVehicleTab, self)._getRequestCriteria(invVehicles)
        requestCriteria |= REQ_CRITERIA.INVENTORY
        vehicleType = self._filterData['vehicleType']
        extra = self._filterData['extra']
        if vehicleType != 'all':
            requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type.lower() == vehicleType.lower())
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
        isStateSuitable = state in (Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER, Vehicle.VEHICLE_STATE.IGR_RENTAL_IS_ORVER)
        isExcludedState = state in (Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT,)
        if isStateSuitable or not isExcludedState and not item.canSell:
            statusMessage = makeString('#menu:store/vehicleStates/%s' % state)
            disable = not item.canSell
        return (statusMessage, disable)

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
            shellsList = map(lambda x: x.intCD, vehicle.gun.defaultAmmo)
            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        elif fitsType == 'myVehiclesInventoryGuns':
            shellsList = set()
            myGuns = self._items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
            for gun in myGuns:
                shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

            for vehicle in invVehicles:
                shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        else:
            shellsList = set()
            myGuns = self._items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
            for gun in myGuns:
                shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

            for vehicle in invVehicles:
                shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

            requestCriteria |= ~REQ_CRITERIA.IN_CD_LIST(shellsList)
        return requestCriteria


class InventoryArtefactTab(InventoryItemsTab, StoreArtefactTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(InventoryArtefactTab, self)._getRequestCriteria(invVehicles)
        fitsType = self._filterData['fitsType']
        itemTypeID = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [itemTypeID])
        elif fitsType == 'myVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, [itemTypeID])
        else:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, [itemTypeID])
        return self._getExtraCriteria(self._filterData['extra'], requestCriteria, invVehicles)


class InventoryOptionalDeviceTab(InventoryArtefactTab, StoreOptionalDeviceTab):

    def _getStatusParams(self, item):
        disabled = False
        statusMessage = ''
        if not item.isInInventory:
            if not item.descriptor['removable']:
                statusMessage = makeString(MENU.INVENTORY_DEVICE_ERRORS_NOT_REMOVABLE)
                disabled = True
            else:
                statusMessage = makeString(MENU.INVENTORY_DEVICE_ERRORS_RESERVED)
                disabled = True
        return (statusMessage, disabled)


class InventoryEquipmentTab(InventoryArtefactTab, StoreEquipmentTab):
    pass
