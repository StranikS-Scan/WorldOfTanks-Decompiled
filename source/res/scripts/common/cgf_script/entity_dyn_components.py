# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/entity_dyn_components.py


class BWEntitiyComponentTracker(object):

    def onDynamicComponentCreated(self, component):
        existing = self.entityGameObject.findComponentByType(type(component))
        if existing is None:
            self.entityGameObject.addComponent(component)
        supMethod = getattr(super(BWEntitiyComponentTracker, self), 'onDynamicComponentCreated', None)
        if supMethod is not None:
            supMethod(self, component)
        return

    def onDynamicComponentDestroyed(self, component):
        existing = self.entityGameObject.findComponentByType(type(component))
        if existing is component:
            self.entityGameObject.removeComponent(component)
        supMethod = getattr(super(BWEntitiyComponentTracker, self), 'onDynamicComponentDestroyed', None)
        if supMethod is not None:
            supMethod(self, component)
        return
