# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/events_core_cgf/entry_point/component.py
from enum import Enum
import CGF
from cgf_script.component_meta_class import registerComponent, CGFMetaTypes, ComponentProperty

class EventNames(Enum):
    COSMIC = 'Cosmic'
    HB = 'May'
    PORTAL = 'Portal'
    WT = 'White Tiger'

    @classmethod
    def toDict(cls):
        return {member.value:member.value for member in cls}


@registerComponent
class Event3dEntryPointGoComponent(object):
    editorTitle = 'Event 3D Entry Point Game object'
    category = 'Events Core'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    eventName = ComponentProperty(type=CGFMetaTypes.STRING, value=EventNames.COSMIC, editorName='Event name', annotations={'comboBox': EventNames.toDict()})


@registerComponent
class EventClickedComponent(object):
    eventName = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Event name')
