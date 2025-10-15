# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/teleport/components.py
import CGF
import Triggers
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent, registerReplicableComponent

@registerComponent
class TeleportSystemComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Teleport system component'
    teleportTime = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Time for teleport process', value=5.0)
    teleportCooldown = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Teleport cooldown', value=10.0)
    forceCoef = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Pushing force coefficient', value=30.0)
    velocityLimit = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Velocity limit on push', value=100.0)


@registerComponent
class TeleportComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Teleport component'
    linkGO = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Destination go link', value=CGF.GameObject)


@registerComponent
class TeleportRequestLinkComponent(object):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Teleport request link component'


@registerReplicableComponent
class TeleportReplicableComponent(object):
    category = 'Portal'
    editorTitle = 'Teleport replicable component'


@registerComponent
class TeleportZoneControllerComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Teleport zone controller'
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Teleport area trigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return


@registerComponent
class ForceFieldControllerComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Force field controller component'
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Force field area trigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return


@registerComponent
class TeleportEffectComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Teleport effect component'
