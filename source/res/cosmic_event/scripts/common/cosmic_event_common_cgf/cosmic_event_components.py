# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common_cgf/cosmic_event_components.py
import CGF
import Math
import Triggers
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class CosmicEventImpulseComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Cosmic'
    editorTitle = 'Impulse'
    impulseDirection = ComponentProperty(type=CGFMetaTypes.VECTOR3, value=Math.Vector3(1, 0, 0), editorName='Impulse direction')
    massCoef = ComponentProperty(type=CGFMetaTypes.INT, editorName='Mass coefficient', value=1)
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.reactionID = None
        self.isActive = False
        return


@registerComponent
class CosmicEventNameComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Cosmic'
    editorTitle = 'Name'
    name = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Name', value='')
