# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/optional_devices_assistant_controller.py
import logging
import typing
from functools import partial
from Event import Event
from account_helpers.optional_devices_assistant_config import readOptionalDevicesUsageFallbackConfig, readOptionalDevicesUsageConfig
from constants import OPTIONAL_DEVICES_USAGE_CONFIG
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_item import OptionalDevicesAssistantItem
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_model import OptionalDevicesAssistantType, OptionalDevicesAssistantItemType
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from renewable_subscription_common.optional_devices_usage_config import GenericOptionalDevice, VehicleLevelClassRoleGroup, VehicleLoadout, convertServerDiffToRichTypes
from renewable_subscription_common.settings_constants import OptionalDevicesUsageConst
from skeletons.gui.game_control import IOptionalDevicesAssistantController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List, Any, Set
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
GENERIC_OPTIONAL_DEVICE_TO_OPT_DEVICES_ASSISTANT_ITEM_TYPE_MAP = {GenericOptionalDevice.STEREOSCOPE: OptionalDevicesAssistantItemType.STEREOSCOPE,
 GenericOptionalDevice.TURBOCHARGER: OptionalDevicesAssistantItemType.TURBOCHARGER,
 GenericOptionalDevice.ENHANCED_AIM_DRIVES: OptionalDevicesAssistantItemType.ENHANCEDAIMDRIVES,
 GenericOptionalDevice.GROUSERS: OptionalDevicesAssistantItemType.GROUSERS,
 GenericOptionalDevice.AIMING_STABILIZER: OptionalDevicesAssistantItemType.AIMINGSTABILIZER,
 GenericOptionalDevice.ANTIFRAGMENTATION_LINING: OptionalDevicesAssistantItemType.ANTIFRAGMENTATIONLINING,
 GenericOptionalDevice.CAMOUFLAGE_NET: OptionalDevicesAssistantItemType.CAMOUFLAGENET,
 GenericOptionalDevice.IMPROVED_SIGHTS: OptionalDevicesAssistantItemType.IMPROVEDSIGHTS,
 GenericOptionalDevice.VENTILATION: OptionalDevicesAssistantItemType.VENTILATION,
 GenericOptionalDevice.HEALTH_RESERVE: OptionalDevicesAssistantItemType.HEALTHRESERVE,
 GenericOptionalDevice.ROTATION_MECHANISM: OptionalDevicesAssistantItemType.ROTATIONMECHANISM,
 GenericOptionalDevice.RAMMER: OptionalDevicesAssistantItemType.RAMMER,
 GenericOptionalDevice.COATED_OPTICS: OptionalDevicesAssistantItemType.COATEDOPTICS,
 GenericOptionalDevice.ADDIT_INVISIBILITY_DEVICE: OptionalDevicesAssistantItemType.ADDITINVISIBILITYDEVICE,
 GenericOptionalDevice.IMPROVED_CONFIGURATION: OptionalDevicesAssistantItemType.IMPROVEDCONFIGURATION,
 GenericOptionalDevice.RADIO_COMMUNICATION: OptionalDevicesAssistantItemType.RADIOCOMMUNICATION,
 GenericOptionalDevice.COMMANDERS_VIEW: OptionalDevicesAssistantItemType.COMMANDERSVIEW}
LAST_ORDER_VALUE = 1000

class OptionalDevicesAssistantController(IOptionalDevicesAssistantController):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)
    _wotPlusController = dependency.descriptor(IWotPlusController)

    def __init__(self):
        super(OptionalDevicesAssistantController, self).__init__()
        self.onConfigChanged = Event()
        self.settingsHasBeenSynced = False
        self._removedVehicles = set()
        self._updatedEquipmentUsages = {}
        self._vehicleToVehicleMap = {}
        self._typeToVehicleMap = {}
        self._clientEquipmentUsages = {}

    def onLobbyStarted(self, ctx):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self._wotPlusController.onDataChanged += self._onWotPlusDataChanged
        self._onWotPlusDataChanged({})
        if not self.settingsHasBeenSynced:
            self._syncServerSettings(convertServerDiffToRichTypes(self._lobbyContext.getServerSettings().getOptionalDevicesUsageConfig()))
            self.settingsHasBeenSynced = True

    def onAccountBecomeNonPlayer(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._wotPlusController.onDataChanged -= self._onWotPlusDataChanged

    def onDisconnected(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._wotPlusController.onDataChanged -= self._onWotPlusDataChanged

    def getPopularOptDevicesList(self, vehicle):
        vehIntCD = vehicle.intCD
        if not self._lobbyContext.getServerSettings().isOptionalDevicesAssistantEnabled():
            return (OptionalDevicesAssistantType.NODATA, vehIntCD, [])
        optDevicesSource, linkedVehicle, optDevicesLoadouts = self._searchVehicleLoadoutsInCache(vehicle)
        popularItemsData = self._fillVehicleLoadoutsData(vehicle, optDevicesLoadouts)
        return (optDevicesSource, linkedVehicle, popularItemsData)

    def _searchVehicleLoadoutsInCache(self, vehicle):
        vehIntCD = vehicle.intCD
        linkedVehicle = vehIntCD
        vehType = VehicleLevelClassRoleGroup(vehicle.level, vehicle.type, vehicle.role)
        optDevicesSource = OptionalDevicesAssistantType.NODATA
        optDevicesLoadouts = self._getVehicleOptionalDevicesFromCache(vehIntCD)
        if vehIntCD in self._vehicleToVehicleMap:
            proxyVehicle = self._vehicleToVehicleMap[vehIntCD]
            optDevicesLoadouts = self._getVehicleOptionalDevicesFromCache(proxyVehicle)
            if optDevicesLoadouts:
                optDevicesSource = OptionalDevicesAssistantType.LINKED
                linkedVehicle = proxyVehicle
            else:
                _logger.error('Attempt to retrieve copied vehicle %s as %s: No vehicle in cache. Invalid cache!', vehIntCD, proxyVehicle)
        elif optDevicesLoadouts:
            optDevicesSource = OptionalDevicesAssistantType.NORMAL
        elif vehType in self._typeToVehicleMap:
            proxyVehicle = self._typeToVehicleMap[vehType]
            optDevicesLoadouts = self._getVehicleOptionalDevicesFromCache(proxyVehicle)
            if optDevicesLoadouts:
                optDevicesSource = OptionalDevicesAssistantType.LINKED
                linkedVehicle = proxyVehicle
            else:
                _logger.error('Attempt to retrieve vehicle similar to %s as %s: No vehicle in cache. Invalid cache!', vehIntCD, proxyVehicle)
        return (OptionalDevicesAssistantType.NODATA, vehIntCD, []) if optDevicesLoadouts and not self._checkOptionalDevicesCompatibilityWithVehicle(optDevicesLoadouts, vehicle) else (optDevicesSource, linkedVehicle, optDevicesLoadouts)

    def _fillVehicleLoadoutsData(self, vehicle, loadouts):
        popularItemsData = []
        for loadout in loadouts:
            sortedDevices = self._sortDevices(vehicle, loadout)
            popularItem = OptionalDevicesAssistantItem()
            popularItem.setPopularity(loadout.percentage)
            loadoutItems = popularItem.getItems()
            loadoutItems.reserve(len(sortedDevices))
            for device in sortedDevices:
                loadoutItems.addString(GENERIC_OPTIONAL_DEVICE_TO_OPT_DEVICES_ASSISTANT_ITEM_TYPE_MAP[device].value)

            popularItemsData.append(popularItem)

        return popularItemsData

    def _syncServerSettings(self, serverDiff):
        self._removedVehicles = set(serverDiff.get(OptionalDevicesUsageConst.REMOVE, []))
        self._updatedEquipmentUsages = serverDiff.get(OptionalDevicesUsageConst.UPDATE, {})
        self._vehicleToVehicleMap.clear()
        for compDescrTo, compDescrFrom in serverDiff.get(OptionalDevicesUsageConst.COPY, {}).items():
            if self._getVehicleOptionalDevicesFromCache(compDescrFrom):
                self._vehicleToVehicleMap[compDescrTo] = compDescrFrom
            _logger.error('Attempt to copy %s vehicle: vehicle not present in cache', compDescrFrom)

    def _onServerSettingsChange(self, diff):
        if OPTIONAL_DEVICES_USAGE_CONFIG not in diff:
            return
        serverDiff = diff[OPTIONAL_DEVICES_USAGE_CONFIG]
        self._syncServerSettings(convertServerDiffToRichTypes(serverDiff))
        self.onConfigChanged()

    def _onWotPlusDataChanged(self, _):
        if self._wotPlusController.isEnabled():
            self._typeToVehicleMap = readOptionalDevicesUsageFallbackConfig()
            self._clientEquipmentUsages = readOptionalDevicesUsageConfig()
        else:
            self._typeToVehicleMap.clear()
            self._clientEquipmentUsages.clear()

    def _getVehicleOptionalDevicesFromCache(self, vehCompDescr):
        if vehCompDescr in self._removedVehicles:
            return []
        if vehCompDescr in self._updatedEquipmentUsages:
            loadouts = self._updatedEquipmentUsages[vehCompDescr]
            return [ VehicleLoadout(list(loadout.devices), loadout.percentage) for loadout in loadouts ]
        if vehCompDescr in self._clientEquipmentUsages:
            loadouts = self._clientEquipmentUsages[vehCompDescr]
            return [ VehicleLoadout(list(loadout.devices), loadout.percentage) for loadout in loadouts ]
        return []

    def _sortDevices(self, vehicle, loadout):
        if len(vehicle.optDevices.slots) != 3:
            return loadout.devices
        slotCategories = vehicle.optDevices.getSlot(1).item.categories
        if not slotCategories:
            return loadout.devices
        loadoutDevicesCopy = list(loadout.devices)
        sortedDevices = [loadoutDevicesCopy.pop(0)]
        loadoutDevicesCopy.sort(key=partial(self._hasTagWithCategory, slotCategories))
        sortedDevices.extend(loadoutDevicesCopy)
        return sortedDevices

    def _hasTagWithCategory(self, categories, device):
        deviceTag = GENERIC_OPTIONAL_DEVICE_TO_OPT_DEVICES_ASSISTANT_ITEM_TYPE_MAP[device].value
        criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_TAGS({deviceTag}) | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_CATEGORIES(categories)
        optDevices = self._itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
        if not optDevices:
            return LAST_ORDER_VALUE
        categoriesSet = set().union(*(optDevice.descriptor.categories for optDevice in optDevices))
        return len(categoriesSet)

    def _checkOptionalDevicesCompatibilityWithVehicle(self, vehicleLoadouts, vehicle):
        for vehicleLoadout in vehicleLoadouts:
            for device in vehicleLoadout.devices:
                deviceTag = GENERIC_OPTIONAL_DEVICE_TO_OPT_DEVICES_ASSISTANT_ITEM_TYPE_MAP[device].value
                criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_TAGS({deviceTag})
                optionalDevices = self._itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
                compatible = any([ optionalDevice.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)[0] for optionalDevice in optionalDevices ])
                if not compatible:
                    return False

        return True
