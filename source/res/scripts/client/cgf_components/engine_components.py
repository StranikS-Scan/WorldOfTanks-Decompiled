# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/engine_components.py
import CGF
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from constants import IS_EDITOR
if IS_EDITOR:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle

@registerComponent
class DisableEngineExhaustComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class DisableEngineExhaustComponentManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, DisableEngineExhaustComponent)
    def onAdded(self, go, component):
        self.__setVehicleExhaust(go, False)

    @onRemovedQuery(CGF.GameObject, DisableEngineExhaustComponent)
    def onRemoved(self, go, component):
        self.__setVehicleExhaust(go, True)

    def __setVehicleExhaust(self, go, enabled):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        if not hierarchyManager:
            return
        else:
            vehicleGO = hierarchyManager.getTopMostParent(go)
            vehicle = vehicleGO.findComponentByType(Vehicle)
            if not vehicle:
                return
            appearance = vehicle.appearance
            if appearance is not None:
                appearance.enableExhaust = enabled
            return
