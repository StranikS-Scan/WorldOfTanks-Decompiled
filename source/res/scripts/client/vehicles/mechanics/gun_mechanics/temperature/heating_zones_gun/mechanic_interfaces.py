# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/heating_zones_gun/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.mechanic_states import IMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import HeatingZonesGunParams

class IHeatingZonesGunComponentParams(object):

    @classmethod
    def fromMechanicParams(cls, params):
        raise NotImplementedError

    @property
    def lowZonePercent(self):
        raise NotImplementedError

    @property
    def mediumZonePercent(self):
        raise NotImplementedError


class IHeatingZonesGunMechanicState(IMechanicState):

    @classmethod
    def fromComponentStatus(cls, heatingZoneState, params):
        raise NotImplementedError

    @property
    def isComfortZone(self):
        raise NotImplementedError

    @property
    def heatingZoneState(self):
        raise NotImplementedError
