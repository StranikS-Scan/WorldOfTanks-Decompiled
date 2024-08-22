# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/optional_devices_assistant_config.py
import csv
import typing
from io import StringIO
import ResMgr
from constants import VEHICLE_CLASS_INDICES, ROLE_LABEL_TO_TYPE
from renewable_subscription_common.optional_devices_usage_config import VehicleLoadout, EQUIPMENT_NAME_TO_GENERIC_OPTIONAL_DEVICE_MAP, _getVehicleTypeCompDescr, VehicleLevelClassRoleGroup
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict
_USAGE_CONFIG_FILE = 'scripts/item_defs/optional_devices_assistance/optional_devices_usage.csv'
_FALLBACK_CONFIG_FILE = 'scripts/item_defs/optional_devices_assistance/optional_devices_fallback_usage.xml'
DEFAULT_ROLE = 'NotDefined'

def readOptionalDevicesUsageConfig():
    config = {}
    section = ResMgr.openSection(_USAGE_CONFIG_FILE)
    reader = csv.reader(StringIO(unicode(section.asString)), delimiter=';')
    next(reader)
    for row in reader:
        if not row:
            continue
        if len(row) != 5:
            raise SoftException('Wrong data in optional devices usage config. %s', row)
        loadouts = config.setdefault(_getVehicleTypeCompDescr(row[0]), [])
        devices = []
        for device in row[1:4]:
            if not device:
                continue
            mappedDevice = EQUIPMENT_NAME_TO_GENERIC_OPTIONAL_DEVICE_MAP.get(device, None)
            if not mappedDevice:
                raise SoftException('Cannot map device from optional devices usage config. Unknown device. %s', device)
            devices.append(mappedDevice)

        percentage = float(row[4])
        loadouts.append(VehicleLoadout(devices, percentage))

    return config


def readOptionalDevicesUsageFallbackConfig():
    config = {}
    section = ResMgr.openSection(_FALLBACK_CONFIG_FILE)['']
    if section is None:
        return config
    else:
        for _, subsection in section.items():
            config.update(_readOptionalDevicesFallbackUsage(subsection))

        return config


def _readOptionalDevicesFallbackUsage(section):
    tempConfig = {}
    level = section.readInt('level')
    type = section.readString('type')
    role = section.readString('role', DEFAULT_ROLE)
    vehicleName = section.readString('vehicleFrom')
    vehTypeCompDescr = _getVehicleTypeCompDescr(vehicleName)
    configKey = VehicleLevelClassRoleGroup(level, type, ROLE_LABEL_TO_TYPE.get(role))
    tempConfig[configKey] = vehTypeCompDescr
    return tempConfig
