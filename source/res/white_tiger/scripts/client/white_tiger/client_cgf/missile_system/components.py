# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/missile_system/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class WTMissileFlyEffectComponent(object):
    category = 'White Tiger'
    editorTitle = 'Missile Fly Effect'
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
    effectPrefab = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Effect prefab path', value='')
