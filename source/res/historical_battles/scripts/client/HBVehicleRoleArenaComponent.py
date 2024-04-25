# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleRoleArenaComponent.py
from typing import Optional, Dict
import BigWorld
import Event
from helpers import dependency
from historical_battles_common.hb_constants import VehicleRole
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import replaceHyphenToUnderscore

class HBVehicleRoleArenaComponent(BigWorld.DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    onRoleInfosUpdated = Event.Event()

    def set_roleInfos(self, _):
        self.onRoleInfosUpdated()

    def getRole(self, vehicleID):
        roleInfo = self.__getRoleInfoByID(vehicleID)
        return VehicleRole(roleInfo['role']) if roleInfo is not None else VehicleRole.regular

    def getRoleName(self, vehicleID):
        vehInfo = self._sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        role = self.getRole(vehicleID)
        if role.hasUniqueIcon():
            iconName = role.name
        elif role == VehicleRole.elite:
            iconName = '{}{}'.format(vehInfo.vehicleType.classTag, role.name.capitalize())
        else:
            iconName = vehInfo.vehicleType.classTag
        return iconName

    def getDamageLogIcon(self, vehicleID):
        vehInfo = self._sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        role = self.getRole(vehicleID)
        if role.hasUniqueIcon():
            iconName = role.name
        else:
            iconName = '{}_{}'.format(vehInfo.vehicleType.classTag, role.name)
        return 'damageLog_{}_16x16'.format(iconName)

    def getPostmortemIcon(self, vehicleID):
        vehInfo = self._sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        role = self.getRole(vehicleID)
        if role.hasUniqueIcon():
            iconName = role.name
        else:
            iconName = '{}_{}'.format(replaceHyphenToUnderscore(vehInfo.vehicleType.classTag), role.name)
        return backport.image(R.images.historical_battles.gui.maps.icons.vehicleTypes.big.dyn(iconName)())

    def __getRoleInfoByID(self, vehicleID):
        return next((roleInfo for roleInfo in self.roleInfos if roleInfo['id'] == vehicleID), None)
