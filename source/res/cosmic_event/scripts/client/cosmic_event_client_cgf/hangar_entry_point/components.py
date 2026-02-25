# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event_client_cgf/hangar_entry_point/components.py
import CGF
from cgf_script.component_meta_class import registerComponent, CGFMetaTypes, ComponentProperty

class EventNames(object):
    COSMIC = 'cosmic_event'


@registerComponent
class Event3dEntryPointGoComponent(object):
    editorTitle = 'Event 3D Entry Point Game object'
    category = 'Events'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    eventName = ComponentProperty(type=CGFMetaTypes.STRING, value=EventNames.COSMIC, editorName='Event name', annotations={'comboBox': {EventNames.COSMIC: EventNames.COSMIC}})
    hoverOn = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Cursor hover sound')
    hoverOff = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Cursor hoverOff sound')
    click = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Click sound')


@registerComponent
class EventClickedComponent(object):
    eventName = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Event name')
