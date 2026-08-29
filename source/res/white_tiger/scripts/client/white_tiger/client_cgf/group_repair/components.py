# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/group_repair/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class WTRegenerationSoundComponent(object):
    category = 'White Tiger'
    editorTitle = 'Regeneration Sound Component'
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
    impulsEvent = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Sound impulse event', value='')
    interruptEvent = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Sound interrupt event', value='')
    completeEvent = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Sound complete event', value='')


@registerComponent
class WTRegenerationComponent(object):
    category = 'White Tiger'
    editorTitle = 'Regeneration Component'
    domain = CGF.DomainOption.DomainClient
