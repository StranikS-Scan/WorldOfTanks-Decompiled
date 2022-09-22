# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/bomb_components.py
import Triggers
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes

class BombAbsorptionAreaComponent(CGFComponent):
    category = 'GameLogic'
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Trigger', value=Triggers.AreaTriggerComponent)
