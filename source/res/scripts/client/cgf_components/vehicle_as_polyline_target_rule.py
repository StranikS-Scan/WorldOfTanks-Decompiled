# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_as_polyline_target_rule.py
import CGF
from GameplayDebug import PolylineDebugTargetComponent
from cgf_script.managers_registrator import onAddedQuery, Rule, registerManager, registerRule
from constants import IS_CLIENT
if IS_CLIENT:
    from Vehicle import Vehicle
else:

    class Vehicle(object):
        pass


class VehicleAsPolylineTargetConfigurator(CGF.ComponentManager):

    @onAddedQuery(Vehicle, CGF.GameObject)
    def onVehicleAppeared(self, vehicle, go):
        if go.findComponentByType(PolylineDebugTargetComponent) is None:
            go.createComponent(PolylineDebugTargetComponent)
        return


@registerRule
class VehicleAsPolylineTargetRule(Rule):
    category = 'Fall Tanks'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    @registerManager(VehicleAsPolylineTargetConfigurator, domain=CGF.DomainOption.DomainClient)
    def constructConfigurator(self):
        return None
