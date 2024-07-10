# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DualAccuracy.py
import typing
import Event
from constants import DUAL_ACCURACY_STATE
from vehicle_systems.entity_components.vehicle_mechanic_component import getPlayerVehicleMechanic, VehicleMechanicComponent
_DEFAULT_ACCURACY_FACTOR = 1.0

def getPlayerVehicleDualAccuracy():
    return getPlayerVehicleMechanic('dualAccuracy')


class DualAccuracy(VehicleMechanicComponent):

    def __init__(self):
        super(DualAccuracy, self).__init__()
        self.__dualAccuracyFactor = _DEFAULT_ACCURACY_FACTOR
        self.__eManager = Event.EventManager()
        self.onSetDualAccState = Event.Event(self.__eManager)
        self._initMechanic()

    def isActive(self):
        return self.state == DUAL_ACCURACY_STATE.ACTIVE

    def getDualAccuracyFactor(self):
        return self.__dualAccuracyFactor

    def getCurrentDualAccuracyFactor(self):
        return self.__dualAccuracyFactor if self.isActive() else _DEFAULT_ACCURACY_FACTOR

    def set_state(self, _=None):
        self._updateMechanicAvatar()
        self._updateMechanicAppearance()

    def onDestroy(self):
        self.__eManager.clear()
        super(DualAccuracy, self).onDestroy()

    def _onAppearanceReady(self):
        self.__collectDualAccuracyParams()

    def _onMechanicAvatarUpdate(self, player):
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _onMechanicAppearanceUpdate(self):
        self.onSetDualAccState(self.isActive())

    def _onSiegeStateUpdate(self, typeDescriptor):
        self.__collectDualAccuracyParams(typeDescriptor)

    def __collectDualAccuracyParams(self, typeDescriptor=None):
        typeDescriptor = typeDescriptor or self.entity.typeDescriptor
        params = typeDescriptor.gun
        self.__dualAccuracyFactor = params.dualAccuracy.afterShotDispersionAngle / params.shotDispersionAngle
