# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/common/mechanic_interfaces.py
from __future__ import absolute_import
from vehicles.components.component_interfaces import IVehicleGunSlotComponent
from vehicles.mechanics.common import IMechanicComponentLogic

class IGunMechanicComponent(IVehicleGunSlotComponent, IMechanicComponentLogic):
    pass
