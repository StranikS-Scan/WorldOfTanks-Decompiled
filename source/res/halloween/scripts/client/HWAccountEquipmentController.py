# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWAccountEquipmentController.py
import copy
import logging
import BigWorld
import halloween_account_commands
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
_logger = logging.getLogger(__name__)

class _HWConsumables(object):

    def __init__(self, layout, installed, isAutoEquip):
        super(_HWConsumables, self).__init__()
        self.layout = layout
        self.installed = installed
        self.isAutoEquip = isAutoEquip


class _HWExpendableEquipment(_ExpendableEquipment):
    __slots__ = ()

    def _createItem(self, intCD):
        return None if not intCD else super(_HWExpendableEquipment, self)._createItem(intCD)


class HalloweenVehicle(object):
    __slots__ = ('__target__', 'hwConsumables')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, target):
        super(HalloweenVehicle, self).__init__()
        self.__target__ = target
        eqCtrl = BigWorld.player().HWAccountEquipmentController
        layout = eqCtrl.getVehicleLayout(target.invID)
        inventory = eqCtrl.getVehicleInventory(target.invID)
        self.hwConsumables = _HWConsumables(layout=_HWExpendableEquipment(GUI_ITEM_TYPE.EQUIPMENT, len(layout), self.itemsCache.items, True, *layout), installed=_HWExpendableEquipment(GUI_ITEM_TYPE.EQUIPMENT, len(layout), self.itemsCache.items, True, *[ (eq if eq in inventory else None) for eq in layout ]), isAutoEquip=eqCtrl.isVehicleAutoEquipEnabled(target.invID))
        return

    def __getattribute__(self, name):
        try:
            return super(HalloweenVehicle, self).__getattribute__(name)
        except AttributeError:
            return self.__target__.__getattribute__(name)

    def __setattr__(self, name, value):
        try:
            super(HalloweenVehicle, self).__setattr__(name, value)
        except AttributeError:
            self.__target__.__setattr__(name, value)

    def __copy__(self):
        targetCopy = copy.copy(self.__target__)
        return self.__class__(targetCopy)

    def __deepcopy__(self, memo):
        targetCopy = copy.deepcopy(self.__target__, memo)
        return self.__class__(targetCopy)

    @classmethod
    def fromVehicle(cls, item):
        return item if isinstance(item, HalloweenVehicle) else HalloweenVehicle(item)


class _HWInventorySessionCache(object):
    DATA_KEY = 'halloweenInventory'
    inventoryCache = None

    @classmethod
    def hwInventory(cls):
        return cls.inventoryCache.get(cls.DATA_KEY, {})

    @classmethod
    def init(cls):
        if cls.inventoryCache is not None:
            return
        else:
            cls.inventoryCache = {}
            g_playerEvents.onClientSynchronize += cls._onClientSynchronize
            connectionMgr = dependency.instance(IConnectionManager)
            connectionMgr.onDisconnected += cls.__deleteInstance
            return

    @classmethod
    def _onClientSynchronize(cls, isFullSync, diff):
        cache = cls.inventoryCache
        if isFullSync:
            cache.clear()
        dataResetKey = (cls.DATA_KEY, '_r')
        if dataResetKey in diff:
            cache[cls.DATA_KEY] = diff[dataResetKey]
        if cls.DATA_KEY in diff:
            synchronizeDicts(diff[cls.DATA_KEY], cache.setdefault(cls.DATA_KEY, {}))

    @classmethod
    def __deleteInstance(cls):
        cls.inventoryCache = None
        g_playerEvents.onClientSynchronize -= cls._onClientSynchronize
        connectionMgr = dependency.instance(IConnectionManager)
        connectionMgr.onDisconnected -= cls.__deleteInstance
        return


class HWAccountEquipmentController(BigWorld.StaticScriptComponent):
    EMPTY_LAYOUT = [0, 0, 0]

    def __init__(self):
        super(HWAccountEquipmentController, self).__init__()
        _HWInventorySessionCache.init()

    @property
    def hwInventory(self):
        return _HWInventorySessionCache.hwInventory()

    def getVehicleLayout(self, vehInvID):
        return self.hwInventory.get('layout', {}).get(vehInvID, self.EMPTY_LAYOUT)

    def getVehicleInventory(self, vehInvID):
        return self.hwInventory.get('eqs', {}).get(vehInvID, [])

    def getVehicleSettings(self, vehInvID):
        return self.hwInventory.get('settings', {}).get(vehInvID, {})

    def isVehicleAutoEquipEnabled(self, vehInvID):
        return self.getVehicleSettings(vehInvID).get('autoMaintenance', False)

    def makeVehicleHWAdapter(self, vehicle):
        return vehicle if isinstance(vehicle, HalloweenVehicle) else HalloweenVehicle.fromVehicle(vehicle)

    def updateSelectedEquipment(self, vehInvID, eqList, callback=None):
        self.entity._doCmdIntArr(halloween_account_commands.CMD_UPDATE_SELECTED_HW_EQUIPMENT, [vehInvID] + eqList, callback)

    def setHwAutoMaintenanceEnabled(self, vehInvID, isEnabled, callback=None):
        self.entity._doCmdInt2(halloween_account_commands.CMD_SET_HW_AUTO_MAINTENANCE_ENABLED, vehInvID, isEnabled, callback)

    def buyMore(self, _):
        from halloween.gui.shared.event_dispatcher import showHalloweenShop
        showHalloweenShop()

    def getVehicleIdealCrewParamsComparator(self, vehicle):
        from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_vehicle_params import HWVehicleParams
        from gui.shared.items_parameters.comparator import VehiclesComparator
        from gui.shared.items_parameters.params_cache import g_paramsCache
        hwEqCtrl = BigWorld.player().HWAccountEquipmentController
        vehicleParams = HWVehicleParams(hwEqCtrl.makeVehicleHWAdapter(vehicle))
        idealCrewVehicle = copy.copy(vehicle)
        idealCrewVehicle.crew = vehicle.getPerfectCrew()
        return VehiclesComparator(vehicleParams.getParamsDict(), HWVehicleParams(hwEqCtrl.makeVehicleHWAdapter(idealCrewVehicle)).getParamsDict(), g_paramsCache.getCompatibleArtefacts(vehicle), vehicleParams.getBonuses(vehicle), vehicleParams.getPenalties(vehicle))

    def devSetLayout(self, layout):
        if not IS_DEVELOPMENT:
            return
        self.updateSelectedEquipment(g_currentVehicle.invID, [ self.__devGetEqCompDescr(eq) for eq in layout ])

    def devSetAutoMaintenanceEnabled(self, isEnabled):
        if not IS_DEVELOPMENT:
            return
        self.setHwAutoMaintenanceEnabled(g_currentVehicle.invID, int(isEnabled))

    def __devGetEqCompDescr(self, equipment):
        if not equipment:
            return 0
        else:
            if isinstance(equipment, str):
                equipment = vehicles.g_cache.equipmentsIDs().get(equipment, None)
                if equipment is None:
                    return 0
            e = vehicles.g_cache.equipments().get(equipment, None)
            return 0 if e is None else e.compactDescr
