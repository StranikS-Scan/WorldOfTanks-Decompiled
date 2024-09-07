# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/vehicle_getter.py
from items.vehicle_items import CHASSIS_ITEM_TYPE
from items.vehicles import VEHICLE_TAGS, VehicleDescr
from collections import defaultdict
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.battle_control import avatar_getter
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.battle_control.battle_constants import VEHICLE_DEVICES, VEHICLE_GUI_ITEMS, VEHICLE_COMPLEX_ITEMS, VEHICLE_INDICATOR_TYPE, AUTO_ROTATION_FLAG, WHEELED_VEHICLE_DEVICES, WHEELED_VEHICLE_GUI_ITEMS, TRACK_WITHIN_TRACK_DEVICES, VEHICLE_CHASSIS_INDICATOR_POSTFIX
from debug_utils import LOG_WARNING
_COATED_OPTICS_TAG = 'coatedOptics'

def hasTurretRotator(vDesc):
    if vDesc is None:
        return False
    else:
        hasFakeTurret = vDesc.gun.turretYawLimits is not None and vDesc.hull.fakeTurrets.get('battle', ())
        return not hasFakeTurret


def isWheeledTech(vDesc):
    return False if vDesc is None else vDesc.type.isWheeledVehicle


def isTrackWithinTrackTech(vDesc):
    return False if vDesc is None else vDesc.isTrackWithinTrack


def isMultiTrackTech(vDesc):
    return False if vDesc is None else vDesc.isMultiTrack


def getYawLimits(vDesc):
    return None if vDesc is None else vDesc.gun.turretYawLimits


def hasYawLimits(vDesc):
    return getYawLimits(vDesc) is not None


def getNoTurretRotatorIndicatorType(vDesc):
    tags = vDesc.type.tags
    if VEHICLE_TAGS.FLAMETHROWER in tags:
        return VEHICLE_INDICATOR_TYPE.AT_SPG
    return VEHICLE_INDICATOR_TYPE.SPG if VEHICLE_CLASS_NAME.SPG in tags else VEHICLE_INDICATOR_TYPE.AT_SPG


def getChassisIndicatorType(indicatorType, vDesc):
    newIndicatorType = indicatorType + VEHICLE_CHASSIS_INDICATOR_POSTFIX.get(vDesc.chassisType, '')
    if not VEHICLE_INDICATOR_TYPE.hasValue(newIndicatorType):
        LOG_WARNING('Unknown indicatorType:', newIndicatorType)
    else:
        return newIndicatorType


def getVehicleIndicatorType(vDesc):
    if vDesc is None:
        return VEHICLE_INDICATOR_TYPE.DEFAULT
    elif vDesc.isWheeledVehicle:
        return VEHICLE_INDICATOR_TYPE.WHEEL
    else:
        indicatorType = getNoTurretRotatorIndicatorType(vDesc) if not hasTurretRotator(vDesc) else VEHICLE_INDICATOR_TYPE.DEFAULT
        indicatorType = getChassisIndicatorType(indicatorType, vDesc) if vDesc.chassisType != CHASSIS_ITEM_TYPE.MONOLITHIC else indicatorType
        return indicatorType


def getAutoRotationFlag(vDesc):
    flag = AUTO_ROTATION_FLAG.IGNORE_IN_UI
    if hasYawLimits(vDesc):
        aih = avatar_getter.getInputHandler()
        if aih is None or aih.getAutorotation():
            flag = AUTO_ROTATION_FLAG.TURN_ON
        else:
            flag = AUTO_ROTATION_FLAG.TURN_OFF
    return flag


def getOptionalDevicesByVehID(vehicleID, avatar=None):
    arena = avatar_getter.getArena(avatar=avatar)
    if arena is None:
        return []
    elif vehicleID not in arena.vehicles:
        return []
    else:
        vehicleType = arena.vehicles[vehicleID].get('vehicleType')
        return [] if vehicleType is None else vehicleType.optionalDevices


def getOptionalDevices(avatar=None):
    vehicleID = avatar_getter.getPlayerVehicleID(avatar=avatar)
    return [] if not vehicleID else getOptionalDevicesByVehID(vehicleID, avatar=avatar)


def isCoatedOpticsInstalled(avatar=None):
    for device in getOptionalDevices(avatar=avatar):
        if device is None:
            continue
        if _COATED_OPTICS_TAG in device.tags:
            return True

    return False


def getCrewMainRolesWoIndexes(crewRoles):
    order = TANKMEN_ROLES_ORDER_DICT['plain']
    default = len(order)
    return sorted([ roles[0] for roles in crewRoles ], key=lambda item: order.index(item) if item in order else default)


def getCrewMainRolesWithIndexes(crewRoles):
    indexes = defaultdict(lambda : 1)

    def _mapping(item):
        role = item[0]
        if role not in ('commander', 'driver'):
            ind = indexes[role]
            indexes[role] += 1
            role += str(ind)
        return role

    return map(_mapping, crewRoles)


class TankmenStatesIterator(object):

    def __init__(self, states=None, vDesc=None):
        super(TankmenStatesIterator, self).__init__()
        if vDesc is None:
            crewRoles = []
        else:
            crewRoles = vDesc.type.crewRoles
        self._rolesEnum = list(TANKMEN_ROLES_ORDER_DICT['enum'])
        self._mainRoles = getCrewMainRolesWithIndexes(crewRoles)
        self._states = defaultdict(lambda : 'normal', states or {})
        return

    def __iter__(self):
        return self

    def next(self):
        if self._rolesEnum:
            role = self._rolesEnum.pop(0)
            if role in self._mainRoles:
                state = self._states[role]
            else:
                state = None
            return (role, state)
        else:
            self._states.clear()
            raise StopIteration()
            return


class VehicleDeviceStatesIterator(object):

    def __init__(self, states=None, vDesc=None, devices=None):
        super(VehicleDeviceStatesIterator, self).__init__()
        self._states = defaultdict(lambda : 'normal', states or {})
        self._hasTurret = hasTurretRotator(vDesc)
        if isWheeledTech(vDesc):
            self._devices = list(devices or WHEELED_VEHICLE_DEVICES)
        elif isTrackWithinTrackTech(vDesc) or isMultiTrackTech(vDesc):
            self._devices = list(devices or TRACK_WITHIN_TRACK_DEVICES)
        else:
            self._devices = list(devices or VEHICLE_DEVICES)

    def __iter__(self):
        return self

    def next(self):
        if self._devices:
            name = self._devices.pop(0)
            if name == 'turretRotator' and not self._hasTurret:
                return (name, None)
            return (name, self._states[name])
        else:
            self._states.clear()
            raise StopIteration()
            return None

    def clear(self):
        self._states.clear()


class VehicleGUIItemStatesIterator(VehicleDeviceStatesIterator):

    def __init__(self, states=None, vDesc=None):
        super(VehicleGUIItemStatesIterator, self).__init__(states, vDesc, WHEELED_VEHICLE_GUI_ITEMS if isWheeledTech(vDesc) else VEHICLE_GUI_ITEMS)

    def next(self):
        itemName, deviceState = super(VehicleGUIItemStatesIterator, self).next()
        deviceName = itemName
        if itemName in VEHICLE_COMPLEX_ITEMS:
            for name in VEHICLE_COMPLEX_ITEMS[itemName]:
                state = self._states[name]
                if state == 'destroyed':
                    deviceState = state
                    deviceName = name
                    break
                if state == 'critical':
                    deviceState = state
                    deviceName = name

        return (itemName, deviceName, deviceState)
