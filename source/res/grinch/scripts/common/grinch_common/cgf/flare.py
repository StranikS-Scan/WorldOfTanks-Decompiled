# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/cgf/flare.py
import CGF
import Triggers
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes

@registerComponent
class GrinchFlareZoneTriggerComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.reactionId = None
        return


@registerComponent
class GrinchFlareConfigComponent(object):
    category = 'Grinch'
    editorTitle = 'Grinch Flare Config Component'
    domain = CGF.DomainOption.DomainAll
    team = ComponentProperty(type=CGFMetaTypes.INT, editorName='team', value=1)
    ownerId = ComponentProperty(type=CGFMetaTypes.INT, editorName='ownerId', value=1)
    debuffDuration = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='debuffDuration', value=10.0)
    receivedDamageFactor = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='receivedDamageFactor', value=1.5)
    blockers = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='blockers', value=-1)
    activationDelay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='activationDelay', value=0.0)
