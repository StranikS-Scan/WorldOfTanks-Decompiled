# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/anomaly/components.py
import CGF
import Triggers
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class AnomalySystemComponent(object):
    category = 'Portal'
    editorTitle = 'Anomaly System'
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor


@registerComponent
class AnomalyTriggerZoneComponent(object):
    category = 'Portal'
    editorTitle = 'Anomaly trigger zone component'
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Area trigger link', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return
