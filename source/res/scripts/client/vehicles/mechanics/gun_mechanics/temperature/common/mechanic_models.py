# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/common/mechanic_models.py
from __future__ import absolute_import, division
import typing
import BigWorld
from cache import last_cached_method
from constants import SERVER_TICK_LENGTH
from gui.shared.utils.decorators import ReprInjector
from math_utils import clamp
from vehicles.mechanics.gun_mechanics.temperature.common.mechanic_interfaces import ITemperatureComponentParams, ITemperatureMechanicState

@ReprInjector.simple('maxTemperature', 'coolingPerSec')
class TemperatureComponentParams(ITemperatureComponentParams):

    def __init__(self, maxTemperature, coolingPerSec):
        self.__maxTemperature = maxTemperature
        self.__coolingPerSec = coolingPerSec

    @property
    def coolingPerSec(self):
        return self.__coolingPerSec

    @property
    def maxTemperature(self):
        return self.__maxTemperature


@ReprInjector.simple(('_state', 'state'), ('_updateTime', 'updateTime'), ('_temperature', 'temperature'), ('_directionFactor', 'directionFactor'))
class TemperatureMechanicState(ITemperatureMechanicState):

    def __init__(self, state, thermalStateID, temperature, updateTime, directionFactor, coolingPerSecFactor, isStaticTemperature, params):
        self._state = state
        self._thermalStateID = thermalStateID
        self._temperature = temperature
        self._updateTime = updateTime
        self._directionFactor = directionFactor / SERVER_TICK_LENGTH
        self._coolingSpeed = params.coolingPerSec * coolingPerSecFactor
        self._isStaticTemperature = isStaticTemperature
        self._params = params

    @property
    def state(self):
        return self._state

    @property
    def currentTemperature(self):
        return self._temperature if self._isStaticTemperature else self.__getCurrentTemperature(BigWorld.serverTime())

    @property
    def maxTemperature(self):
        return self._params.maxTemperature

    @property
    def temperatureProgress(self):
        return self.currentTemperature / self.maxTemperature

    def isTransition(self, other):
        return self.getTransitionKey() != other.getTransitionKey()

    def getTransitionKey(self):
        return (self._state,)

    @last_cached_method()
    def __getCurrentTemperature(self, serverTime):
        return clamp(0.0, self._params.maxTemperature, self._temperature + max(serverTime - self._updateTime, 0.0) * self._directionFactor)
