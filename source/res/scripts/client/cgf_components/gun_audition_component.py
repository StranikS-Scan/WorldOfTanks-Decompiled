# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/gun_audition_component.py
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery
from vehicle_systems.cgf_helpers import getVehicleEntityByGameObject
from Vehicular import GunAudition

@autoregister(presentInAllWorlds=True)
class GunAuditionsManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GunAudition, tickGroup='preInitGroup')
    def onGunAuditionAdded(self, gameObject, gunAudition):
        vehicle = getVehicleEntityByGameObject(gameObject)
        if vehicle is not None:
            gunAudition.isPlayer = vehicle.isPlayerVehicle
        return
