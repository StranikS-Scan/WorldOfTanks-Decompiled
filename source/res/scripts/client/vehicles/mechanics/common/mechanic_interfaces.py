# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/common/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from vehicles.components.component_interfaces import IVehicleSlotComponent
if typing.TYPE_CHECKING:
    from items.vehicle_mechanics_types import VehicleMechanicVariant, VehicleMechanicKey

class IMechanicComponentLogic(object):

    @property
    def isValid(self):
        raise NotImplementedError

    @property
    def vehicleMechanicKey(self):
        raise NotImplementedError


class IMechanicComponent(IVehicleSlotComponent, IMechanicComponentLogic):
    pass


class IMechanicWithVariants(object):

    @property
    def mechanicVariant(self):
        raise NotImplementedError
