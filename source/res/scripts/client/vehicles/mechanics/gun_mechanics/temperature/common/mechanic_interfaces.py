# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/common/mechanic_interfaces.py
from __future__ import absolute_import
from vehicles.mechanics.mechanic_states import IMechanicState

class ITemperatureComponentParams(object):

    @property
    def coolingPerSec(self):
        raise NotImplementedError

    @property
    def maxTemperature(self):
        raise NotImplementedError


class ITemperatureMechanicState(IMechanicState):

    @property
    def state(self):
        raise NotImplementedError

    @property
    def currentTemperature(self):
        raise NotImplementedError

    @property
    def maxTemperature(self):
        raise NotImplementedError

    @property
    def temperatureProgress(self):
        raise NotImplementedError
