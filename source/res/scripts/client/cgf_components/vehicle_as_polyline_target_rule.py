# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_as_polyline_target_rule.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import registerModule
from constants import IS_CLIENT, HAS_DEV_RESOURCES
if IS_CLIENT:
    from Vehicle import Vehicle
else:

    class Vehicle(object):
        pass


if HAS_DEV_RESOURCES:
    from GameplayDebug import PolylineDebugTargetComponent
else:

    class PolylineDebugTargetComponent(object):
        pass


class VehicleAsPolylineTargetConfiguratorSystem(CGF.System):
    VehicleCreated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(Vehicle))
    Reactions = CGF.Reactions(VehicleCreated)

    def update(self):
        queue = CGF.CommandQueue(self.spaceID)
        for go in self.reaction(self.VehicleCreated):
            if not go.hasComponent(PolylineDebugTargetComponent):
                queue.createComponent(go, PolylineDebugTargetComponent)


@registerModule
class VehicleAsPolylineTargetModule(object):
    name = 'PolyLine Debug Target'
    group = 'Fall Tanks'
    systems = [CGF.RegisterSystem(VehicleAsPolylineTargetConfiguratorSystem, domain=CGF.Domain.Client)]
