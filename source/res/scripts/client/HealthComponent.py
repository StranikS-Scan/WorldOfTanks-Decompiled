# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HealthComponent.py
from Event import Event
from cgf_components_common.state_components import HealthComponentDescriptor
from cgf_script.component_meta_class import registerReplicableComponent
from constants import IS_EDITOR
if IS_EDITOR:

    class DynamicScriptComponent(object):
        pass


else:
    from BigWorld import DynamicScriptComponent

@registerReplicableComponent
class HealthComponent(DynamicScriptComponent, HealthComponentDescriptor):

    def __init__(self):
        super(HealthComponent, self).__init__()
        self.onHealthChanged = Event()

    def set_health(self, oldHealth):
        self.onHealthChanged(oldHealth, self.health, self.maxHealth)
