# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GeneratorActivation.py
from script_component.ScriptComponent import DynamicScriptComponent
from Generator import GeneratorActivationComponent

class GeneratorActivation(DynamicScriptComponent):

    def damaged(self):
        go = self.entity.entityGameObject
        activation = go.findComponentByType(GeneratorActivationComponent)
        if activation:
            activation.wasDamaged = True
