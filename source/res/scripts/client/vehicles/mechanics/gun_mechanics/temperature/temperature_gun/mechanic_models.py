# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/temperature_gun/mechanic_models.py
from __future__ import absolute_import, division
import typing
import BigWorld
from constants import TEMPERATURE_GUN_STATE
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from gui.shared.utils.decorators import ReprInjector
from vehicles.mechanics.gun_mechanics.temperature.common import TemperatureComponentParams, TemperatureMechanicState
from vehicles.mechanics.gun_mechanics.temperature.temperature_gun.mechanic_interfaces import ITemperatureGunComponentParamsLogic, ITemperatureGunMechanicStateLogic
if typing.TYPE_CHECKING:
    from items.components.shared_components import TemperatureGunParams

@ReprInjector.withParent('coolingDelay')
class TemperatureGunComponentParams(TemperatureComponentParams, ITemperatureGunComponentParamsLogic):

    def __init__(self, maxTemperature, coolingPerSec, coolingDelay):
        super(TemperatureGunComponentParams, self).__init__(maxTemperature, coolingPerSec)
        self.__coolingDelay = coolingDelay

    @classmethod
    def fromMechanicParams(cls, params):
        return cls(params.maxTemperature, params.coolingPerSec, params.coolingDelay)

    @property
    def coolingDelay(self):
        return self.__coolingDelay


@ReprInjector.withParent()
class TemperatureGunMechanicState(TemperatureMechanicState, ITemperatureGunMechanicStateLogic):

    @classmethod
    def fromComponentStatus(cls, status, params):
        return cls(status.state, status.thermalStateID, status.currentTemperature, status.updateTime, status.directionFactor, status.coolingPerSecFactor, status.state in TEMPERATURE_GUN_STATE.STATIC_STATES, params)

    def getCoolingTime(self, targetTemperature):
        coolingLeft = -1.0
        if self._state not in TEMPERATURE_GUN_STATE.COOLING_STATES:
            return coolingLeft
        coolingLeft = max(self.currentTemperature - targetTemperature, 0.0) / self._coolingSpeed
        if not self._isStaticTemperature:
            return coolingLeft
        coolingDelay = max(self._params.coolingDelay - max(BigWorld.serverTime() - self._updateTime, 0.0), 0.0)
        return coolingDelay + coolingLeft


class TemperatureGunAmmoState(DefaultComponentAmmoState):

    def __init__(self, mechanicState):
        self.__mechanicState = mechanicState

    @property
    def mechanicState(self):
        return self.__mechanicState
