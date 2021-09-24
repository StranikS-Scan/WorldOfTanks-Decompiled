# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GeneratorActivator.py
import ArenaComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class GeneratorActivator(DynamicScriptComponent):

    def __init__(self):
        super(GeneratorActivator, self).__init__()
        go = self.entity.entityGameObject
        go.createComponent(ArenaComponents.TriggerComponent, 'captured')

    def onDestroy(self):
        go = self.entity.entityGameObject
        go.removeComponentByType(ArenaComponents.TriggerComponent)
        super(GeneratorActivator, self).onDestroy()
