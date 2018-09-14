# Embedded file name: scripts/client/gui/battle_control/vehicle_getter.py
from collections import defaultdict
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_DEVICES, VEHICLE_GUI_ITEMS, VEHICLE_COMPLEX_ITEMS, VEHICLE_INDICATOR_TYPE

def hasTurretRotator(vDesc):
    if vDesc is None:
        return False
    else:
        result = True
        tags = vDesc.type.tags
        if tags & {'SPG', 'AT-SPG'} and vDesc.gun['turretYawLimits'] is not None:
            if len(vDesc.hull.get('fakeTurrets', {}).get('battle', ())) > 0:
                result = False
        return result


def getYawLimits(vDesc):
    if vDesc is None:
        return
    else:
        return vDesc.gun['turretYawLimits']


def hasYawLimits(vDesc):
    return getYawLimits(vDesc) is not None


def getVehicleIndicatorType(vDesc):
    if vDesc is None:
        return VEHICLE_INDICATOR_TYPE.DEFAULT
    else:
        iType = VEHICLE_INDICATOR_TYPE.DEFAULT
        if not hasTurretRotator(vDesc):
            tags = vDesc.type.tags
            if 'SPG' in tags:
                iType = VEHICLE_INDICATOR_TYPE.SPG
            elif 'AT-SPG' in tags:
                iType = VEHICLE_INDICATOR_TYPE.AT_SPG
        return iType


def isAutoRotationOn(vDesc):
    isOn = None
    if hasYawLimits(vDesc):
        aih = avatar_getter.getInputHandler()
        isOn = False
        if aih is not None:
            isOn = aih.getAutorotation()
    return isOn


def getCrewMainRolesWoIndexes(crewRoles):
    order = TANKMEN_ROLES_ORDER_DICT['plain']
    default = len(order)
    return sorted(map(lambda roles: roles[0], crewRoles), key=lambda item: (order.index(item) if item in order else default))


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

    def __init__(self, states = None, vDesc = None):
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
        if len(self._rolesEnum):
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

    def __init__(self, states = None, vDesc = None, devices = None):
        super(VehicleDeviceStatesIterator, self).__init__()
        self._states = defaultdict(lambda : 'normal', states or {})
        self._hasTurret = hasTurretRotator(vDesc)
        self._devices = list(devices or VEHICLE_DEVICES)

    def __iter__(self):
        return self

    def next(self):
        if len(self._devices):
            name = self._devices.pop(0)
            if name == 'turretRotator' and not self._hasTurret:
                return (name, None)
            else:
                return (name, self._states[name])
        else:
            self._states.clear()
            raise StopIteration()
        return None

    def clear(self):
        self._states.clear()


class VehicleGUIItemStatesIterator(VehicleDeviceStatesIterator):

    def __init__(self, states = None, vDesc = None):
        super(VehicleGUIItemStatesIterator, self).__init__(states, vDesc, VEHICLE_GUI_ITEMS)

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
                elif state == 'critical':
                    deviceState = state
                    deviceName = name

        return (itemName, deviceName, deviceState)
