# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DualAccuracy.py
import Event
from constants import DUAL_ACCURACY_STATE
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
_DEFAULT_ACCURACY_FACTOR = 1.0

@ReprInjector.withParent()
class DualAccuracy(VehicleDynamicComponent, IGunMechanicComponent):

    def __init__(self):
        super(DualAccuracy, self).__init__()
        self.__dualAccuracyFactor = _DEFAULT_ACCURACY_FACTOR
        self.__eManager = Event.EventManager()
        self.onSetDualAccState = Event.Event(self.__eManager)
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.DUAL_ACCURACY

    def isActive(self):
        return self.state == DUAL_ACCURACY_STATE.ACTIVE

    def getComponentParams(self):
        return self.getDualAccuracyFactor()

    def getCurrentDualAccuracyFactor(self):
        return self.__dualAccuracyFactor if self.isActive() else _DEFAULT_ACCURACY_FACTOR

    def getDualAccuracyFactor(self):
        return self.__dualAccuracyFactor

    def set_state(self, _=None):
        self._updateComponentAvatar()
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__eManager.clear()
        super(DualAccuracy, self).onDestroy()

    def _onComponentAvatarUpdate(self, player):
        super(DualAccuracy, self)._onComponentAvatarUpdate(player)
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(DualAccuracy, self)._onComponentAppearanceUpdate(**kwargs)
        self.onSetDualAccState(self.isActive())

    def _collectComponentParams(self, typeDescriptor):
        super(DualAccuracy, self)._collectComponentParams(typeDescriptor)
        params = typeDescriptor.gun
        self.__dualAccuracyFactor = params.dualAccuracy.afterShotDispersionAngle / params.shotDispersionAngle
