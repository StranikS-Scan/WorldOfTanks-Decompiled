# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HealthComponent.py
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from cgf_components_common.state_components import HealthComponentDescriptor
from cgf_script.component_meta_class import registerReplicableComponent
from Event import Event

@registerReplicableComponent
class HealthComponent(ReplicableDynamicScriptComponent, HealthComponentDescriptor):

    def __init__(self):
        super(HealthComponent, self).__init__()
        self.onHealthChanged = Event()

    def set_health(self, oldHealth):
        self.onHealthChanged(oldHealth, self.health, self.maxHealth)
