# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/ls_vehicle_role_helper.py
from last_stand_common.last_stand_constants import ENEMY_ROLE_TAG_PREFIX
_LSROLE_PREFIX_LEN = len(ENEMY_ROLE_TAG_PREFIX)
g_vehicleRoleHelper = None

def getVehicleRole(vehicleType):
    return g_vehicleRoleHelper.getVehicleRole(vehicleType)


class LSVehicleRoleHelper(object):

    def __init__(self, *args, **kwargs):
        super(LSVehicleRoleHelper, self).__init__(*args, **kwargs)
        self.__vehicleRoles = {}

    def getVehicleRole(self, vehicleType):
        compactDescr = vehicleType.compactDescr
        role = self.__vehicleRoles.get(compactDescr)
        if role is not None:
            return self.__getReturnValue(role)
        else:
            role = self.__extractVehicleRole(vehicleType)
            self.__vehicleRoles[compactDescr] = role
            return self.__getReturnValue(role)

    def __extractVehicleRole(self, vehicleType):
        for tag in vehicleType.tags:
            if tag.startswith(ENEMY_ROLE_TAG_PREFIX):
                return tag[_LSROLE_PREFIX_LEN:]

    def __getReturnValue(self, role):
        return None if role is None or role == '' else role


g_vehicleRoleHelper = LSVehicleRoleHelper()
