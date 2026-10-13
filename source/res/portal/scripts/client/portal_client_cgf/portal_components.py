# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/portal_components.py
import CGF
from cgf_script.component_meta_class import registerComponent, CGFMetaTypes, ComponentProperty

@registerComponent
class SuperBossFightEffectComponent(object):
    category = 'Portal'
    editorTitle = 'Super Boss Fight Effect'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


@registerComponent
class SpawnSound3DOnRemove(object):
    category = 'Portal'
    editorTitle = 'Spawn Sound3D On Remove'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab', annotations={'path': '*.prefab'})


@registerComponent
class BossHPMarkerComponent(object):
    category = 'Portal'
    editorTitle = 'Boss HP Marker'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
