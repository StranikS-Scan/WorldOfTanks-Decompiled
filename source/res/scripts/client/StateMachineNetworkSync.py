# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StateMachineNetworkSync.py
from __future__ import absolute_import
import CGF
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from cgf_script.registration import registerReplicableComponent
from CgfStateMachine import StateMachineComponent

@registerReplicableComponent
class StateMachineNetworkSync(ReplicableDynamicScriptComponent):
    editorTitle = 'CGF State Machine Network Sync'


class StateMachineNetworkSyncSystem(CGF.System):
    StateMachineIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(StateMachineComponent), CGF.Ro(StateMachineNetworkSync))
    Reactions = CGF.Reactions(StateMachineIterate)

    def update(self):
        for stateMachineComponent, networkSync in self.reaction(self.StateMachineIterate):
            if networkSync.replicableStateIndex is not None:
                stateMachineComponent.replicatedActiveStateIndex = networkSync.replicableStateIndex

        return
