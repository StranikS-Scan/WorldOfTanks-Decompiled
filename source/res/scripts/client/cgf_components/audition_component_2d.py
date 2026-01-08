# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/audition_component_2d.py
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery
from cgf_common.cgf_helpers import getVehicleEntityByGameObject
from Sound import Audition2D

@autoregister(presentInAllWorlds=True)
class AuditionsManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, Audition2D, tickGroup='preInitGroup')
    def onAuditionAdded(self, gameObject, audition):
        vehicle = getVehicleEntityByGameObject(gameObject)
        if vehicle is not None:
            audition.isPlayer = vehicle.isPlayerVehicle
        return
