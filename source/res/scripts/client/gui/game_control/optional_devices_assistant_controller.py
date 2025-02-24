# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/optional_devices_assistant_controller.py
import logging
import typing
from Event import Event
from account_helpers.optional_devices_assistant_config import readOptionalDevicesUsageFallbackConfig, readOptionalDevicesUsageConfig, _USAGE_CONFIG_FILE, _USAGE_CONFIG_FILE_LEGENDARY
from constants import OPTIONAL_DEVICES_USAGE_CONFIG
from constants import QUEUE_TYPE
from gui.impl.lobby.tank_setup.optional_devices_assistant.hangar import _sortDevices, _GENERIC_INT_TYPE_TO_UI_ENUM, OptDeviceAssistType, _ARCHETYPE_TO_TAG_ENUM
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from renewable_subscription_common.optional_devices_usage_config import GenericOptionalDevice, VehicleLevelClassRoleGroup, VehicleLoadout, convertServerDiffToRichTypes, GENERIC_OPTIONAL_DEVICE_MAP_TO_EQUIPMENT_NAME
from renewable_subscription_common.settings_constants import OptionalDevicesUsageConst
from skeletons.gui.game_control import IOptionalDevicesAssistantController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List, Any, Callable
    from gui.shared.gui_items.Vehicle import Vehicle
    _OptDevicePreset = Tuple[OptDeviceAssistType, int, List[VehicleLoadout]]
_SUPPORTED_QUEUE_TYPES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.COMP7)
_logger = logging.getLogger(__name__)

class _IOptDeviceAssistDataProvider(object):

    def getPresets(self, vehicle, queueType):
        return tuple()

    def hasLoadout(self, vehicle, queueType):
        presets = self.getPresets(vehicle, queueType)
        for _, __, loadouts in presets:
            if bool(loadouts):
                return True

        return False

    def searchVehicleLoadoutsInCache(self, vehicle):
        return (OptDeviceAssistType.NODATA, vehicle.intCD, [])


class _OptDevicesAssistLocalDataProvider(_IOptDeviceAssistDataProvider):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusController = dependency.descriptor(IWotPlusController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, evt):
        super(_OptDevicesAssistLocalDataProvider, self).__init__()
        self.__settingsHasBeenSynced = False
        self._removedVehicles = set()
        self._updatedEquipmentUsages = {}
        self._vehicleToVehicleMap = {}
        self._typeToVehicleMap = {}
        self._clientEquipmentUsages = {}
        self._clientEquipmentUsagesLegendary = {}
        self.__dataChangeEvent = evt

    def start(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self._wotPlusController.onEnabledStatusChanged += self._onWotPlusEnabled
        self._typeToVehicleMap = readOptionalDevicesUsageFallbackConfig()
        self._clientEquipmentUsages = readOptionalDevicesUsageConfig(_USAGE_CONFIG_FILE)
        self._clientEquipmentUsagesLegendary = readOptionalDevicesUsageConfig(_USAGE_CONFIG_FILE_LEGENDARY)
        self._onWotPlusEnabled(self._wotPlusController.isEnabled())
        if not self.__settingsHasBeenSynced:
            self._syncServerSettings(convertServerDiffToRichTypes(self._lobbyContext.getServerSettings().getOptionalDevicesUsageConfig()))
            self.__settingsHasBeenSynced = True

    def stop(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._wotPlusController.onEnabledStatusChanged -= self._onWotPlusEnabled

    def destroy(self):
        self.__dataChangeEvent = None
        return

    def getPresets(self, vehicle, qt):
        isOptionalDevicesAssistantEnabled = self._lobbyContext.getServerSettings().isOptionalDevicesAssistantEnabled()
        if not (isOptionalDevicesAssistantEnabled and self._wotPlusController.isEnabled()) or qt != QUEUE_TYPE.RANDOMS:
            vehIntCD = vehicle.intCD
            return ((OptDeviceAssistType.NODATA, vehIntCD, []), (OptDeviceAssistType.NODATA, vehIntCD, []))
        return (self.searchVehicleLoadoutsInCache(vehicle), self._searchVehicleLoadoutsInCacheLegendary(vehicle))

    def searchVehicleLoadoutsInCache(self, vehicle):
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
        if OPTIONAL_DEVICES_USAGE_CONFIG not in diff:
            return
        serverDiff = diff[OPTIONAL_DEVICES_USAGE_CONFIG]
        self._syncServerSettings(convertServerDiffToRichTypes(serverDiff))
        self.__dataChangeEvent()

    def _onWotPlusEnabled(self, _):
        self.__dataChangeEvent()

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
                criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_TAGS({deviceKey}) | REQ_CRITERIA.OPTIONAL_DEVICE.IS_COMPATIBLE_WITH_VEHICLE(vehicle)
                optionalDevices = self._itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria, nationID=vehicle.nationID).values()
                if not optionalDevices:
                    criteria = REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_BY_ARCHETYPE(deviceKey) | REQ_CRITERIA.OPTIONAL_DEVICE.IS_COMPATIBLE_WITH_VEHICLE(vehicle)
                    optionalDevices = self._itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria, nationID=vehicle.nationID).values()
                    if not optionalDevices:
                        return False

        return True


class OptionalDevicesAssistantController(IOptionalDevicesAssistantController):

    def __init__(self):
        super(OptionalDevicesAssistantController, self).__init__()
        self.onConfigChanged = Event()
        self._localDataProvider = _OptDevicesAssistLocalDataProvider(self.__onOptDevAssistV5DataChanged)

    def fini(self):
        super(OptionalDevicesAssistantController, self).fini()
        self._localDataProvider.destroy()

    def onLobbyStarted(self, ctx):
        self._localDataProvider.start()

    def onAccountBecomeNonPlayer(self):
        self._localDataProvider.stop()

    def onDisconnected(self):
        self._localDataProvider.stop()

    def getPopularOptDevicesPresets(self, vehicle, queueType):
        if queueType not in _SUPPORTED_QUEUE_TYPES:
            vehIntCD = vehicle.intCD
            return ((OptDeviceAssistType.NODATA, vehIntCD, []), (OptDeviceAssistType.NODATA, vehIntCD, []))
        return self._localDataProvider.getPresets(vehicle, queueType)

    def vehicleHasLoadout(self, vehicle, qt):
        return self._localDataProvider.hasLoadout(vehicle, qt)

    def getTheMostPopularOptDevicesTagsList(self, vehicle):
        _, __, optDevicesLoadouts = self._localDataProvider.searchVehicleLoadoutsInCache(vehicle)
        devicesTag = []
        if optDevicesLoadouts:
            sortedDevices = _sortDevices(vehicle, optDevicesLoadouts[0])
            for device in sortedDevices:
                if device in _ARCHETYPE_TO_TAG_ENUM:
                    value = _ARCHETYPE_TO_TAG_ENUM[device].value
                else:
                    value = _GENERIC_INT_TYPE_TO_UI_ENUM[device].value
                devicesTag.append(value)

        return devicesTag

    def __onOptDevAssistV5DataChanged(self):
        self.onConfigChanged()
