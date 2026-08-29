# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/events_core_cgf/missile_system/components.py
import CGF
from Math import Vector3
from cgf_script.component_meta_class import registerComponent

@registerComponent
class ClientMissileComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'Events Core'

    def __init__(self, **kwargs):
        self.distanceToTarget = Vector3(0, 0, 0)


@registerComponent
class MissileReplicationDoneComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'Events Core'


@registerComponent
class MissileInputComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'Events Core'
    editorTitle = 'Client Missile Input'


@registerComponent
class FPVModeComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'Events Core'
    editorTitle = 'FPV Mode Comp'


@registerComponent
class ArcadeModeComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'Events Core'
    editorTitle = 'Arcade Mode Comp'
