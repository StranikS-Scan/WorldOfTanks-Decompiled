# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/cgf/snowstorm.py
import CGF
import Triggers
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes

@registerComponent
class GrinchSnowstormTriggerComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionId = None
        self.exitReactionId = None
        return


@registerComponent
class GrinchSnowstormTarget(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
