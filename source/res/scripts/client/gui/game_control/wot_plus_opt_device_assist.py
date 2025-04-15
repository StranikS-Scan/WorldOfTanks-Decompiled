# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus_opt_device_assist.py
import logging
from functools import partial
import typing
from account_helpers.optional_devices_assistant_config import readOptionalDevicesUsageFallbackConfig, readOptionalDevicesUsageConfig, _USAGE_CONFIG_FILE, _USAGE_CONFIG_FILE_LEGENDARY
from constants import OPTIONAL_DEVICES_USAGE_CONFIG, PREBATTLE_TYPE
from gui.game_control.wotlda.cache import EquipmentForSubscribersCache
from gui.game_control.wotlda.constants import SupportedWotldaLoadoutType, OptDeviceAssistType, SupportedWTRRange
from gui.game_control.wotlda.loadout_model import vehicleOptDeviceLoadoutsSchema
from gui.prb_control import prbEntityProperty
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_bus import SharedEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from renewable_subscription_common.optional_devices_usage_config import GenericOptionalDevice, VehicleLevelClassRoleGroup, VehicleLoadout, convertServerDiffToRichTypes, GENERIC_OPTIONAL_DEVICE_MAP_TO_EQUIPMENT_NAME
from renewable_subscription_common.settings_constants import OptionalDevicesUsageConst
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List, Any, Callable, Set, Optional, Union
    from gui.shared.gui_items.Vehicle import Vehicle
    _OptDevicePreset = Tuple[OptDeviceAssistType, int, List[VehicleLoadout]]
_logger = logging.getLogger(__name__)

class _IOptDeviceAssistDataProvider(object):

    def getPresets(self, vehicle):
        return tuple()

    def hasLoadout(self, vehicle):
        presets = self.getPresets(vehicle)
        for _, __, loadouts in presets:
            if bool(loadouts):
                return True

        return False


def _sortDevices(vehicle, loadout):
    if len(vehicle.optDevices.slots) != 3:
        return loadout.devices
    slotCategories = vehicle.optDevices.getSlot(1).item.categories
    loadoutDevicesCopy = list(loadout.devices)
    sortedDevices = [loadoutDevicesCopy.pop(0)]
    loadoutDevicesCopy.sort(key=partial(_sortComparator, slotCategories))
    sortedDevices.extend(loadoutDevicesCopy)
    return sortedDevices


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _sortComparator(categories, device, itemsCache=None):
    deviceKey = GENERIC_OPTIONAL_DEVICE_MAP_TO_EQUIPMENT_NAME[device]
    criteria = REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_BY_ARCHETYPE(deviceKey)
    modernizedDevices = itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
    if modernizedDevices:
        return 1001
    if categories:
        criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_TAGS({deviceKey}) | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_CATEGORIES(categories)
        optDevices = itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
        if not optDevices:
            return 1000
        categoriesSet = set().union(*(optDevice.descriptor.categories for optDevice in optDevices))
        return len(categoriesSet)


class _OptDevicesAssistLocalDataProvider(_IOptDeviceAssistDataProvider):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, evt):
        super(_OptDevicesAssistLocalDataProvider, self).__init__()
        self.__initialized = False
        self._removedVehicles = set()
        self._updatedEquipmentUsages = {}
        self._vehicleToVehicleMap = {}
        self._typeToVehicleMap = {}
        self._clientEquipmentUsages = {}
        self._clientEquipmentUsagesLegendary = {}
        self.__dataChangeEvent = evt

    def start(self):
        if not self.__initialized:
            self._typeToVehicleMap = readOptionalDevicesUsageFallbackConfig()
            self._clientEquipmentUsages = readOptionalDevicesUsageConfig(_USAGE_CONFIG_FILE)
            self._clientEquipmentUsagesLegendary = readOptionalDevicesUsageConfig(_USAGE_CONFIG_FILE_LEGENDARY)
            self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
            self._syncServerSettings(convertServerDiffToRichTypes(self._lobbyContext.getServerSettings().getOptionalDevicesUsageConfig()))
            self.__initialized = True

    def stop(self):
        pass

    def destroy(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._typeToVehicleMap.clear()
        self._clientEquipmentUsages.clear()
        self._clientEquipmentUsagesLegendary.clear()
        self.__dataChangeEvent = None
        return

    def getPresets(self, vehicle):
        return (self._searchVehicleLoadoutsInCache(vehicle), self._searchVehicleLoadoutsInCacheLegendary(vehicle))

    def getMostPopularLoadout(self, vehicle):
        presetData = self._searchVehicleLoadoutsInCache(vehicle)
        for loadout in presetData[2]:
            if loadout.devices:
                return loadout

        return None

    def _searchVehicleLoadoutsInCache(self, vehicle):
        vehIntCD = vehicle.intCD
        linkedVehicle = vehIntCD
        vehType = VehicleLevelClassRoleGroup(vehicle.level, vehicle.type, vehicle.role)
        optDevicesSource = OptDeviceAssistType.NODATA
        optDevicesLoadouts = self._getOptionalDevicesFromCache(vehIntCD)
        if vehIntCD in self._vehicleToVehicleMap:
            proxyVehicle = self._vehicleToVehicleMap[vehIntCD]
            optDevicesLoadouts = self._getOptionalDevicesFromCache(proxyVehicle)
            if optDevicesLoadouts:
                optDevicesSource = OptDeviceAssistType.LINKED
                linkedVehicle = proxyVehicle
            else:
                _logger.error('Attempt to retrieve copied vehicle %s as %s: No vehicle in cache. Invalid cache!', vehIntCD, proxyVehicle)
        elif optDevicesLoadouts:
            optDevicesSource = OptDeviceAssistType.NORMAL
        elif vehType in self._typeToVehicleMap:
            proxyVehicle = self._typeToVehicleMap[vehType]
            optDevicesLoadouts = self._getOptionalDevicesFromCache(proxyVehicle)
            if optDevicesLoadouts:
                optDevicesSource = OptDeviceAssistType.LINKED
                linkedVehicle = proxyVehicle
            else:
                _logger.error('Attempt to retrieve vehicle similar to %s as %s: No vehicle in cache. Invalid cache!', vehIntCD, proxyVehicle)
        return (OptDeviceAssistType.NODATA, vehIntCD, []) if optDevicesLoadouts and not self._checkOptionalDevicesCompatibilityWithVehicle(optDevicesLoadouts, vehicle) else (optDevicesSource, linkedVehicle, optDevicesLoadouts)

    def _searchVehicleLoadoutsInCacheLegendary(self, vehicle):
        vehIntCD = vehicle.intCD
        optDevicesSource = OptDeviceAssistType.NODATA
        optDevicesLoadouts = self._getOptionalDevicesFromCacheLegendary(vehIntCD)
        if optDevicesLoadouts:
            optDevicesSource = OptDeviceAssistType.NORMAL
        return (OptDeviceAssistType.NODATA, vehIntCD, []) if optDevicesLoadouts and not self._checkOptionalDevicesCompatibilityWithVehicle(optDevicesLoadouts, vehicle) else (optDevicesSource, vehIntCD, optDevicesLoadouts)

    def _syncServerSettings(self, serverDiff):
        self._removedVehicles = set(serverDiff.get(OptionalDevicesUsageConst.REMOVE, []))
        self._updatedEquipmentUsages = serverDiff.get(OptionalDevicesUsageConst.UPDATE, {})
        self._vehicleToVehicleMap.clear()
        for compDescrTo, compDescrFrom in serverDiff.get(OptionalDevicesUsageConst.COPY, {}).items():
            if self._getOptionalDevicesFromCache(compDescrFrom):
                self._vehicleToVehicleMap[compDescrTo] = compDescrFrom
            _logger.error('Attempt to copy %s vehicle: vehicle not present in cache', compDescrFrom)

    def _onServerSettingsChange(self, diff):
        serverDiff = diff.get(OPTIONAL_DEVICES_USAGE_CONFIG)
        if serverDiff is None:
            return
        else:
            self._syncServerSettings(convertServerDiffToRichTypes(serverDiff))
            self.__dataChangeEvent()
            return

    def _getOptionalDevicesFromCache(self, vehCompDescr):
        if vehCompDescr in self._removedVehicles:
            return []
        if vehCompDescr in self._updatedEquipmentUsages:
            loadouts = self._updatedEquipmentUsages[vehCompDescr]
            return [ VehicleLoadout(list(loadout.devices), loadout.percentage) for loadout in loadouts ]
        if vehCompDescr in self._clientEquipmentUsages:
            loadouts = self._clientEquipmentUsages[vehCompDescr]
            return [ VehicleLoadout(list(loadout.devices), loadout.percentage) for loadout in loadouts ]
        return []

    def _getOptionalDevicesFromCacheLegendary(self, vehCompDescr):
        loadouts = self._clientEquipmentUsagesLegendary.get(vehCompDescr, [])
        return [ VehicleLoadout(list(loadout.devices), loadout.percentage) for loadout in loadouts ]

    def _checkOptionalDevicesCompatibilityWithVehicle(self, vehicleLoadouts, vehicle):
        for vehicleLoadout in vehicleLoadouts:
            for device in vehicleLoadout.devices:
                deviceKey = GENERIC_OPTIONAL_DEVICE_MAP_TO_EQUIPMENT_NAME[device]
                criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_TAGS({deviceKey})
                optionalDevices = self._itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
                compatible = any([ optionalDevice.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)[0] for optionalDevice in optionalDevices ])
                if not compatible:
                    criteria = REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_BY_ARCHETYPE(deviceKey)
                    optionalDevices = self._itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
                    compatible = any([ optionalDevice.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)[0] for optionalDevice in optionalDevices ])
                    if not compatible:
                        return False

        return True


class _RemoteDataProvider(_IOptDeviceAssistDataProvider):

    def __init__(self):
        super(_RemoteDataProvider, self).__init__()
        self._initiated = False
        self._cache = EquipmentForSubscribersCache()

    def start(self):
        self._cache.onRead += self._onCacheRead
        self._cache.read()

    def stop(self, withDelete=False):
        self._cache.clearCache()
        if withDelete:
            self.deleteCacheFile()
        self._initiated = False

    def destroy(self):
        self._cache.clear()
        self._initiated = False

    def deleteCacheFile(self):
        self._cache.deleteCacheFile()

    @property
    def clientCacheUpdatedAt(self):
        return self._cache.getUpdatedAtTimestamp()

    @property
    def initiated(self):
        return self._initiated

    def fillPresets(self, loadouts):
        if not loadouts:
            _logger.warning('Trying to fill empty presets')
            return
        self._cache.update(loadouts)
        self._initiated = True

    def getPresetByLoadoutType(self, loadoutType, vehicle):
        if not self._initiated:
            return self._generateEmptyPreset(vehicle.intCD)
        rawPreset = self._getRawPreset(loadoutType, vehicle.intCD)
        return vehicleOptDeviceLoadoutsSchema.deserialize(rawPreset).convertToView()

    def _generateEmptyPreset(self, vehicleCD):
        return ((OptDeviceAssistType.NODATA, vehicleCD, []), (OptDeviceAssistType.NODATA, vehicleCD, []))

    def _getRawPreset(self, loadoutType, vehicleCD):
        rawPreset = {'vehicleId': vehicleCD}
        for wtrRange in SupportedWTRRange.allRanges():
            preset = self._cache.getLoadout(vehicleCD, loadoutType=loadoutType.value, wtrRange=wtrRange.value)
            rawPreset[wtrRange.value] = preset

        return rawPreset

    def _onCacheRead(self):
        self._cache.onRead -= self._onCacheRead
        if self._cache.isCacheEmpty():
            return
        self._initiated = True


class OptionalDevicesAssistantCtrl(object):
    OPT_DEVICE_ASSIST_DATA_CHANGED = 'optDeviceAssistDataChanged'
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _platoonCtrl = dependency.descriptor(IPlatoonController)
    _SUPPORTED_PREBATTLE_TYPES = {PREBATTLE_TYPE.SQUAD}
    _PREBATTLE_TYPES_TO_LOADOUT_TYPE = {PREBATTLE_TYPE.SQUAD: SupportedWotldaLoadoutType.RANDOM}

    def __init__(self):
        super(OptionalDevicesAssistantCtrl, self).__init__()
        self._localDataProvider = _OptDevicesAssistLocalDataProvider(self.__onOptDevAssistLocalDataChanged)
        self._remoteDataProvider = _RemoteDataProvider()

    @classmethod
    def addSupportedBattleType(cls, battleType, loadoutType):
        if battleType not in PREBATTLE_TYPE.RANGE:
            _logger.warning('Trying to add prebattle type %s which is not in PREBATTLE_TYPE', battleType)
            return
        cls._PREBATTLE_TYPES_TO_LOADOUT_TYPE[battleType] = loadoutType
        cls._SUPPORTED_PREBATTLE_TYPES.add(battleType)

    @property
    def remoteClientCacheUpdatedAt(self):
        return self._remoteDataProvider.clientCacheUpdatedAt

    @prbEntityProperty
    def prbEntity(self):
        return None

    def start(self):
        self._localDataProvider.start()

    def stop(self):
        self._localDataProvider.stop()
        self._remoteDataProvider.stop()

    def heatCache(self):
        self._remoteDataProvider.start()

    def destroy(self):
        self._localDataProvider.destroy()
        self._remoteDataProvider.destroy()

    def deleteClientCacheFile(self):
        self._remoteDataProvider.deleteCacheFile()

    def fillRemotePresets(self, presets):
        _logger.debug('Filling presets for remote data provider')
        self._remoteDataProvider.fillPresets(presets)

    def getMostPopularLoadout(self, vehicle):
        loadout = self._localDataProvider.getMostPopularLoadout(vehicle)
        if loadout:
            _sortDevices(vehicle, loadout)
        return loadout

    def getPopularOptDevicesPresets(self, vehicle):
        if not self.__isDataRetrievingAllowed():
            vehIntCD = vehicle.intCD
            return ((OptDeviceAssistType.NODATA, vehIntCD, []), (OptDeviceAssistType.NODATA, vehIntCD, []))
        if self._remoteDataProvider.initiated:
            loadoutType = self._PREBATTLE_TYPES_TO_LOADOUT_TYPE.get(self._platoonCtrl.getPrbEntityType())
            commonPreset, legendPreset = self._remoteDataProvider.getPresetByLoadoutType(loadoutType, vehicle)
            _logger.debug('Returning data from remote data provider')
            return (commonPreset, legendPreset)
        common, legendary = self._localDataProvider.getPresets(vehicle)
        for loadout in common[2]:
            _sortDevices(vehicle, loadout)

        for loadout in legendary[2]:
            _sortDevices(vehicle, loadout)

        return (common, legendary)

    def vehicleHasLoadout(self, vehicle):
        return False if not self.__isDataRetrievingAllowed() else self._localDataProvider.hasLoadout(vehicle)

    def __isDataRetrievingAllowed(self):
        if not self._lobbyContext.getServerSettings().isOptionalDevicesAssistantEnabled():
            return False
        return False if self._platoonCtrl.getPrbEntityType() not in self._SUPPORTED_PREBATTLE_TYPES else True

    def __onOptDevAssistLocalDataChanged(self):
        g_eventBus.handleEvent(SharedEvent(self.OPT_DEVICE_ASSIST_DATA_CHANGED), EVENT_BUS_SCOPE.LOBBY)
