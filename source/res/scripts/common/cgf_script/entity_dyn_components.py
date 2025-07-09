# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/entity_dyn_components.py
from cgf_network import processCreateDynamicComponent, processDestroyDynamicComponent

class BWEntitiyComponentTracker(object):

    def onDynamicComponentCreated(self, component):
        networkID = getattr(component, 'game_object_network_id', None)
        if networkID is not None:
            processCreateDynamicComponent(networkID, self.spaceID, component)
        else:
            existing = self.entityGameObject.findComponentByType(type(component))
            if existing is None:
                self.entityGameObject.addComponent(component)
        supMethod = getattr(super(BWEntitiyComponentTracker, self), 'onDynamicComponentCreated', None)
        if supMethod is not None:
            supMethod(self, component)
        return

    def onDynamicComponentDestroyed(self, component):
        networkID = getattr(component, 'game_object_network_id', None)
        if networkID is not None:
            processDestroyDynamicComponent(networkID, self.spaceID, component)
        else:
            existing = self.entityGameObject.findComponentByType(type(component))
            if existing is component:
                self.entityGameObject.removeComponent(component)
        supMethod = getattr(super(BWEntitiyComponentTracker, self), 'onDynamicComponentDestroyed', None)
        if supMethod is not None:
            supMethod(self, component)
        return
