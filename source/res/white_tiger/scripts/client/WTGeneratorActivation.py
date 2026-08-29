# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTGeneratorActivation.py
from __future__ import absolute_import
from script_component.DynamicScriptComponent import DynamicScriptComponent
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from white_tiger.cgf_components.generator_components import WTGeneratorActivationComponent

class WTGeneratorActivation(DynamicScriptComponent):

    def damaged(self):
        go = self.entity.entityGameObject
        activation = go.findWrite(WTGeneratorActivationComponent)
        if activation:
            activation.wasDamaged = True
