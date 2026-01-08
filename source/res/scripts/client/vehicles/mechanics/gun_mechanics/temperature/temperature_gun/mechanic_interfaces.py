# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/temperature_gun/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.gun_mechanics.temperature.common import ITemperatureComponentParams, ITemperatureMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import TemperatureGunParams

class ITemperatureGunComponentParamsLogic(object):

    @classmethod
    def fromMechanicParams(cls, params):
        raise NotImplementedError

    @property
    def coolingDelay(self):
        raise NotImplementedError


class ITemperatureGunComponentParams(ITemperatureComponentParams, ITemperatureGunComponentParamsLogic):
    pass


class ITemperatureGunMechanicStateLogic(object):

    @classmethod
    def fromComponentStatus(cls, status, params):
        raise NotImplementedError

    def getCoolingTime(self, targetTemperature):
        raise NotImplementedError


class ITemperatureGunMechanicState(ITemperatureMechanicState, ITemperatureGunMechanicStateLogic):
    pass
