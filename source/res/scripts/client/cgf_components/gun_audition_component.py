# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/gun_audition_component.py
from __future__ import absolute_import
import CGF
from Vehicular import GunAudition
from constants import IS_EDITOR, IS_CGF_DUMP
if IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle

class GunAuditionsSystem(CGF.System):
    GunAuditionActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(GunAudition))
    VehicleAccess = CGF.AccessReaction(CGF.Ro(Vehicle))
    Reactions = CGF.Reactions(GunAuditionActivated, VehicleAccess)

    def update(self):
        vehicleAccess = self.reaction(self.VehicleAccess)
        for gameObject, gunAudition in self.reaction(self.GunAuditionActivated):
            self.onGunAuditionAdded(gameObject, gunAudition, vehicleAccess)

    def onGunAuditionAdded(self, gameObject, gunAudition, vehicleAccess):
        vehicle = CGF.findParentWithReaction(gameObject, vehicleAccess)
        if vehicle is not None:
            gunAudition.isPlayer = vehicle.isPlayerVehicle
        return
