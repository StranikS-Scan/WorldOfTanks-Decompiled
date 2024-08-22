# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/renewable_subscription_common/optional_devices_usage_config.py
import logging
import typing
from collections import namedtuple
from enum import Enum
from items import vehicles
from renewable_subscription_common.settings_constants import OptionalDevicesUsageConst
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from typing import Dict, List
_logger = logging.getLogger(__name__)
VehicleLoadout = namedtuple('VehicleLoadout', ('devices', 'percentage'))
VehicleLevelClassRoleGroup = namedtuple('VehicleLevelClassRoleGroup', ('level', 'vehClass', 'role'))

class GenericOptionalDevice(Enum):
    STEREOSCOPE = 1
    TURBOCHARGER = 2
    ENHANCED_AIM_DRIVES = 3
    GROUSERS = 4
    AIMING_STABILIZER = 5
    ANTIFRAGMENTATION_LINING = 6
    CAMOUFLAGE_NET = 7
    IMPROVED_SIGHTS = 8
    VENTILATION = 9
    HEALTH_RESERVE = 10
    ROTATION_MECHANISM = 11
    RAMMER = 12
    COATED_OPTICS = 13
    ADDIT_INVISIBILITY_DEVICE = 14
    IMPROVED_CONFIGURATION = 15
    RADIO_COMMUNICATION = 16
    COMMANDERS_VIEW = 17


EQUIPMENT_NAME_TO_GENERIC_OPTIONAL_DEVICE_MAP = {'stereoscope': GenericOptionalDevice.STEREOSCOPE,
 'turbocharger': GenericOptionalDevice.TURBOCHARGER,
 'enhancedAimDrives': GenericOptionalDevice.ENHANCED_AIM_DRIVES,
 'grousers': GenericOptionalDevice.GROUSERS,
 'aimingStabilizer': GenericOptionalDevice.AIMING_STABILIZER,
 'antifragmentationLining': GenericOptionalDevice.ANTIFRAGMENTATION_LINING,
 'camouflageNet': GenericOptionalDevice.CAMOUFLAGE_NET,
 'improvedSights': GenericOptionalDevice.IMPROVED_SIGHTS,
 'ventilation': GenericOptionalDevice.VENTILATION,
 'healthReserve': GenericOptionalDevice.HEALTH_RESERVE,
 'rotationMechanism': GenericOptionalDevice.ROTATION_MECHANISM,
 'rammer': GenericOptionalDevice.RAMMER,
 'coatedOptics': GenericOptionalDevice.COATED_OPTICS,
 'additInvisibilityDevice': GenericOptionalDevice.ADDIT_INVISIBILITY_DEVICE,
 'improvedConfiguration': GenericOptionalDevice.IMPROVED_CONFIGURATION,
 'radioCommunication': GenericOptionalDevice.RADIO_COMMUNICATION,
 'commandersView': GenericOptionalDevice.COMMANDERS_VIEW}

def _readOptionalDevicesUsage(section):
    tempConfig = {}
    vehicleName = section.readString('vehicle')
    vehTypeCompDescr = _getVehicleTypeCompDescr(vehicleName)
    tempConfig[vehTypeCompDescr] = _parseDevicesLoadouts(section)
    return tempConfig


def _parseDevicesLoadouts(reader):
    section = reader['loadouts']
    loadouts = []
    for _, values in section.items():
        devices = []
        for device in values.readString('devices').split():
            device = device.strip()
            if device not in EQUIPMENT_NAME_TO_GENERIC_OPTIONAL_DEVICE_MAP:
                _logger.warning('Unknown device %s in optional device assistant config.' % device)
                continue
            devices.append(EQUIPMENT_NAME_TO_GENERIC_OPTIONAL_DEVICE_MAP.get(device).value)

        percentage = values.readFloat('percentage', 0.0)
        loadouts.append((devices, percentage))

    return loadouts


def _getVehicleTypeCompDescr(vehicleName):
    try:
        return vehicles.makeVehicleTypeCompDescrByName(vehicleName)
    except SoftException:
        _logger.warning('Vehicle %s does not exist! Check optional devices assistant configs to fix it.' % vehicleName)


def convertServerDiffToRichTypes(configDict):
    updateConfig = configDict.get(OptionalDevicesUsageConst.UPDATE, {})
    for vehicle, loadoutList in updateConfig.items():
        newLoadoutList = []
        for loadout in loadoutList:
            devicesList = map(GenericOptionalDevice, loadout[0])
            percentage = loadout[1]
            newLoadoutList.append(VehicleLoadout(devicesList, percentage))

        updateConfig[vehicle] = newLoadoutList

    return configDict


def _validateOverrideConfig(configDict):
    removedVehicles = set(configDict.get(OptionalDevicesUsageConst.REMOVE, []))
    updatedEquipmentUsages = set(configDict.get(OptionalDevicesUsageConst.UPDATE, {}).keys())
    copiedVehiclesFrom = configDict.get(OptionalDevicesUsageConst.COPY, {}).values()
    copiedVehiclesTo = configDict.get(OptionalDevicesUsageConst.COPY, {}).keys()
    if -1 in removedVehicles or -1 in updatedEquipmentUsages or -1 in copiedVehiclesFrom or -1 in copiedVehiclesTo:
        raise SoftException('There is at least one nonexistent vehicle in optional_devices_usage_override_config.xml. See warnings.')
    removedUpdated = removedVehicles.intersection(updatedEquipmentUsages)
    if removedUpdated:
        raise SoftException('There are removed AND updated vehicles in optional_devices_usage_override_config.xml. %s', [ vehicles.getVehicleType(removedVehicle).name for removedVehicle in removedUpdated ])
    removedCopied = removedVehicles.intersection(copiedVehiclesFrom)
    if removedCopied:
        raise SoftException('There are removed vehicles as "vehicleFrom" in copy config. %s', [ vehicles.getVehicleType(removedVehicle).name for removedVehicle in removedCopied ])
    wrongDeviceLenVehicles = []
    for vehicleCD, data in configDict.get(OptionalDevicesUsageConst.UPDATE, {}).items():
        if len(data) > 3:
            wrongDeviceLenVehicles.append(vehicleCD)

    if wrongDeviceLenVehicles:
        raise SoftException('Invalid number of popular setups for vehicles: %s', [ vehicles.getVehicleType(vehicle).name for vehicle in wrongDeviceLenVehicles ])
