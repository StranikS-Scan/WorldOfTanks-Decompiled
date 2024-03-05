# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/gun_shot_effect_component.py
import CGF
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent

@registerComponent
class GunShotEffectComponent(object):
    editorTitle = 'Gun Shot Effect Component'
    category = 'Animator Triggers'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    materialParam = ComponentProperty(type=CGFMetaTypes.STRING, editorName='material property', value='TintlColor')
    startValue = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='start value', value=0.0)
    endValue = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='end value', value=0.5)
