# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DualAccuracy.py
import typing
import Event
from constants import DUAL_ACCURACY_STATE
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleMechanic, getPlayerVehicleMechanic
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
_DEFAULT_ACCURACY_FACTOR = 1.0

def getVehicleDualAccuracy(vehicle):
    return getVehicleMechanic(VehicleMechanic.DUAL_ACCURACY, vehicle)


def getPlayerVehicleDualAccuracy():
    return getPlayerVehicleMechanic(VehicleMechanic.DUAL_ACCURACY)


class DualAccuracy(VehicleDynamicComponent):

    def __init__(self):
        super(DualAccuracy, self).__init__()
        self.__dualAccuracyFactor = _DEFAULT_ACCURACY_FACTOR
        self.__eManager = Event.EventManager()
        self.onSetDualAccState = Event.Event(self.__eManager)
        self._initComponent()

    def isActive(self):
        return self.state == DUAL_ACCURACY_STATE.ACTIVE

    def getDualAccuracyFactor(self):
        return self.__dualAccuracyFactor

    def getCurrentDualAccuracyFactor(self):
        return self.__dualAccuracyFactor if self.isActive() else _DEFAULT_ACCURACY_FACTOR

    def set_state(self, _=None):
        self._updateComponentAvatar()
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__eManager.clear()
        super(DualAccuracy, self).onDestroy()

    def _onComponentAvatarUpdate(self, player):
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _onComponentAppearanceUpdate(self):
        self.onSetDualAccState(self.isActive())

    def _collectComponentParams(self, typeDescriptor):
        params = typeDescriptor.gun
        self.__dualAccuracyFactor = params.dualAccuracy.afterShotDispersionAngle / params.shotDispersionAngle
