# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/VehicleWTGeneratorActivation.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from EntityWTGeneratorComponent import GeneratorActivationComponent

class VehicleWTGeneratorActivation(DynamicScriptComponent):

    def damaged(self):
        go = self.entity.entityGameObject
        activation = go.findComponentByType(GeneratorActivationComponent)
        if activation:
            activation.wasDamaged = True
