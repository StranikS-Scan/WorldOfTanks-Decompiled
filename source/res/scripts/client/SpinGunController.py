# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SpinGunController.py
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import SpinGunState
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_wrappers import checkStateStatus
from vehicle_systems.spin_guns.spinning_events import SpinGunSpinningEvents
from vehicle_systems.entity_components.vehicle_mechanic_component import VehicleMechanicComponent
_MAX_SPIN_VALUE = 1.0

class SpinGunController(VehicleMechanicComponent):

    def __init__(self):
        super(SpinGunController, self).__init__()
        self.__maxValue = _MAX_SPIN_VALUE
        self.__minValue = self.__downSpeed = self.__upSpeed = 0.0
        self.__spinningEvents = SpinGunSpinningEvents(self)
        self._initMechanic()

    @property
    def spinningEvents(self):
        return self.__spinningEvents

    def isSpinningActive(self):
        return self.stateStatus is not None and self.stateStatus.state in SpinGunState.ACTIVE_STATES

    @checkStateStatus(states=SpinGunState.ACTIVE_STATES, abortAction='getSpinningMinValue')
    def getSpinningValue(self, stateStatus=None):
        if stateStatus.state not in SpinGunState.DYNAMIC_STATES:
            return stateStatus.spinFactor
        dt = max(BigWorld.serverTime() - stateStatus.stateActivationTime, 0.0)
        return min(stateStatus.spinFactor + dt * self.__upSpeed, self.__maxValue) if stateStatus.state == SpinGunState.SPIN_UP else max(stateStatus.spinFactor - dt * self.__downSpeed, self.__minValue)

    def getSpinningMinValue(self):
        return self.__minValue

    def set_stateStatus(self, _=None):
        self._updateMechanicAppearance()

    def onDestroy(self):
        self.__spinningEvents.destroy()
        super(SpinGunController, self).onDestroy()

    def _onAppearanceReady(self):
        params = self.entity.typeDescriptor.gun
        self.__minValue, self.__maxValue = params.spin.startFactor, _MAX_SPIN_VALUE
        self.__downSpeed = (self.__maxValue - self.__minValue) / params.spin.spinDownTimeout
        self.__upSpeed = (self.__maxValue - self.__minValue) / params.spin.spinUpTimeout

    def _onMechanicAppearanceUpdate(self):
        self.__spinningEvents.updateSpinningActiveStatus(self.isSpinningActive())
