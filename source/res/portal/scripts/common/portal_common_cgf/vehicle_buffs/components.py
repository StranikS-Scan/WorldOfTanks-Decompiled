# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/vehicle_buffs/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent, registerReplicableComponent

@registerReplicableComponent
class PortalAuraComponent(object):
    category = 'Portal'
    editorTitle = 'Portal Aura Component'
    applyAlliesComponents = {}
    applyEnemiesComponents = {}

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return


@registerComponent
class AuraGOFollower(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Aura GO Follower'
    target = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Target', value=CGF.GameObject)

    def __init__(self):
        self.owner = None
        return
