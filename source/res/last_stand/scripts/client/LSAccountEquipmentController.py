# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSAccountEquipmentController.py
import logging
import BigWorld
import weakref
import functools
from last_stand_common import ls_account_commands, last_stand_constants
from CurrentVehicle import g_currentVehicle
from constants import IS_DEVELOPMENT
from items import vehicles
from PlayerEvents import g_playerEvents
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from gui.shared.gui_items.vehicle_equipment import _ExpendableEquipment
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.requesters import getDiffID
_logger = logging.getLogger(__name__)

def getLSConsumables(vehicle):
    return BigWorld.player().LSAccountEquipmentController.getExtConsumables(vehicle)


def devSetLayout(layout, invID=None):
    if not IS_DEVELOPMENT:
        return
    BigWorld.player().LSAccountEquipmentController.devSetLayout(layout, invID)


def devSetAutoMaintenanceEnabled(isEnabled, invID=None):
    if not IS_DEVELOPMENT:
        return
    BigWorld.player().LSAccountEquipmentController.devSetAutoMaintenanceEnabled(isEnabled, invID)


class _ExtConsumables(object):
    __slots__ = ('layout', 'installed', 'isAutoEquip')

    def __init__(self, layout, installed, isAutoEquip):
        super(_ExtConsumables, self).__init__()
        self.layout = layout
        self.installed = installed
        self.isAutoEquip = isAutoEquip


class _ExtExpendableEquipment(_ExpendableEquipment):
    __slots__ = ()

    def _createItem(self, intCD):
        return None if not intCD else super(_ExtExpendableEquipment, self)._createItem(intCD)


class LSInventorySessionCache(object):
    DATA_KEY = last_stand_constants.LS_INVENTORY_PDATA_KEY
    extendedInventoryCache = None
    vehObjsCache = None

    @classmethod
    def inventory(cls):
        return cls.extendedInventoryCache.get(cls.DATA_KEY, {})

    @classmethod
    def init(cls):
        if cls.extendedInventoryCache is not None:
            return
        else:
            cls.extendedInventoryCache = {}
            cls.vehObjsCache = {}
            g_playerEvents.onClientSynchronize += cls._onClientSynchronize
            connectionMgr = dependency.instance(IConnectionManager)
            connectionMgr.onDisconnected += cls.__deleteInstance
            return

    @classmethod
    def getCachedEquipment(cls, obj, initializer):
        objID = id(obj)
        if objID not in cls.vehObjsCache:
            cls.vehObjsCache[objID] = (initializer(obj), weakref.ref(obj, functools.partial(cls.__delCachedEquipment, objID)))
        return cls.vehObjsCache[objID][0]

    @classmethod
    def vehInventoryInvalidator(cls, params):
        for data in params.diff.get(cls.DATA_KEY, {}).itervalues():
            for vehInvID in data.iterkeys():
                vehData = params.inventory.getVehicleData(getDiffID(vehInvID))
                if vehData is not None:
                    params.invalidate[GUI_ITEM_TYPE.VEHICLE].add(vehData.descriptor.type.compactDescr)

        return

    @classmethod
    def _onClientSynchronize(cls, isFullSync, diff):
        cache = cls.extendedInventoryCache
        if isFullSync:
            cache.clear()
            cls.vehObjsCache.clear()
        dataResetKey = (cls.DATA_KEY, '_r')
        if dataResetKey in diff:
            cache[cls.DATA_KEY] = diff[dataResetKey]
        if cls.DATA_KEY in diff:
            synchronizeDicts(diff[cls.DATA_KEY], cache.setdefault(cls.DATA_KEY, {}))

    @classmethod
    def __deleteInstance(cls):
        cls.extendedInventoryCache = None
        cls.vehObjsCache = None
        g_playerEvents.onClientSynchronize -= cls._onClientSynchronize
        connectionMgr = dependency.instance(IConnectionManager)
        connectionMgr.onDisconnected -= cls.__deleteInstance
        return

    @classmethod
    def __delCachedEquipment(cls, objID, _):
        if cls.vehObjsCache is not None:
            cls.vehObjsCache.pop(objID, None)
        return


class LSAccountEquipmentController(BigWorld.StaticScriptComponent):
    EMPTY_LAYOUT = [0, 0, 0]
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(LSAccountEquipmentController, self).__init__()
        LSInventorySessionCache.init()
        self._vehObject = None
        self._vehInvID = None
        return

    @property
    def inventory(self):
        return LSInventorySessionCache.inventory()

    def getVehicleLayout(self, vehInvID):
        return self.inventory.get('layout', {}).get(vehInvID, self.EMPTY_LAYOUT)

    def getVehicleInventory(self, vehInvID):
        return self.inventory.get('eqs', {}).get(vehInvID, [])

    def getVehicleSettings(self, vehInvID):
        return self.inventory.get('settings', {}).get(vehInvID, {})

    def isVehicleAutoEquipEnabled(self, vehInvID):
        return self.getVehicleSettings(vehInvID).get('autoMaintenance', last_stand_constants.LS_DEFAULT_AUTO_MAINTENANCE)

    def getExtConsumables(self, vehicle):
        return LSInventorySessionCache.getCachedEquipment(vehicle, self._createExtendedConsumables)

    def updateSelectedEquipment(self, vehInvID, eqList, callback=None):
        self.entity._doCmdIntArr(ls_account_commands.CMD_LS_UPDATE_SELECTED_EXT_EQUIPMENT, [vehInvID] + eqList, callback)

    def setAutoMaintenanceEnabled(self, vehInvID, isEnabled, callback=None):
        self.entity._doCmdInt2(ls_account_commands.CMD_LS_SET_EXT_EQUIPMENT_AUTO_MAINTENANCE, vehInvID, isEnabled, callback)

    def _createExtendedConsumables(self, vehicle):
        layout = self.getVehicleLayout(vehicle.invID)
        inventory = self.getVehicleInventory(vehicle.invID)
        result = _ExtConsumables(layout=_ExtExpendableEquipment(GUI_ITEM_TYPE.EQUIPMENT, len(layout), self.itemsCache.items, True, *layout), installed=_ExtExpendableEquipment(GUI_ITEM_TYPE.EQUIPMENT, len(layout), self.itemsCache.items, True, *[ (eq if eq in inventory else None) for eq in layout ]), isAutoEquip=self.isVehicleAutoEquipEnabled(vehicle.invID))
        return result

    def devSetLayout(self, layout, invID=None):
        if not IS_DEVELOPMENT:
            return
        else:
            self.updateSelectedEquipment(g_currentVehicle.invID if invID is None else invID, [ self.__devGetEqCompDescr(eq) for eq in layout ])
            return

    def devSetAutoMaintenanceEnabled(self, isEnabled, invID=None):
        if not IS_DEVELOPMENT:
            return
        else:
            self.setAutoMaintenanceEnabled(g_currentVehicle.invID if invID is None else invID, int(isEnabled))
            return

    def __devGetEqCompDescr(self, equipment):
        if not equipment:
            return 0
        else:
            if isinstance(equipment, str):
                equipment = vehicles.g_cache.equipmentIDs().get(equipment, None)
                if equipment is None:
                    return 0
            e = vehicles.g_cache.equipments().get(equipment, None)
            return 0 if e is None else e.compactDescr
