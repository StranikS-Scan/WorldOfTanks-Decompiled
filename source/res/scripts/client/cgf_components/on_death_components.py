# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/on_death_components.py
import CGF
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent

@registerComponent
class ChangeModelOnDeathComponent(object):
    category = 'Death'
    editorTitle = 'Change Model On Death Component'
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
    modelPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Model path', annotations={'path': '*.model'})
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0.0)

    def __init__(self):
        self.initialModel = None
        return


@registerComponent
class SoundOnDeathComponent(object):
    category = 'Death'
    editorTitle = 'Sound On Death Component'
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
    soundPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Sound Prefab', annotations={'path': '*.prefab'})
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0.0)
    attachToGO = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Attach to GO', value=True)


@registerComponent
class EffectOnDeathComponent(object):
    category = 'Death'
    editorTitle = 'Effect On Death Component'
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
    effectPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Effect Prefab', annotations={'path': '*.prefab'})
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0.0)
    attachToGO = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Attach to GO', value=True)
