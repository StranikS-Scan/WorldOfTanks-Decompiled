# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TestReplicableComponent.py
from __future__ import absolute_import
import CGF
import GenericComponents
import GameplayDebug
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from cgf_demo.test_replicable import TestReplicableComponentDescriptor
from cgf_script.registration import registerReplicableComponent
from Event import Event

@registerReplicableComponent
class TestReplicableComponent(ReplicableDynamicScriptComponent, TestReplicableComponentDescriptor):

    def __init__(self):
        super(TestReplicableComponent, self).__init__()
        self.onReplicated = Event()

    def set_replicableInt(self, old):
        self.onReplicated(old, self.replicableInt)

    def set_replicableFloat(self, old):
        self.onReplicated(old, self.replicableFloat)

    def set_replicableString(self, old):
        self.onReplicated(old, self.replicableFloat)

    def set_replicableVector3(self, old):
        self.onReplicated(old, self.replicableFloat)

    def set_replicableStringList(self, old):
        self.onReplicated(old, self.replicableFloat)


class DisplayReplicableValuesSystem(CGF.System):
    ReplicableAdded = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(TestReplicableComponent))
    ReplicableIterate = CGF.IterateReaction(CGF.ActiveOnly, TestReplicableComponent, CGF.Rw(GameplayDebug.DebugTextComponent))
    Reactions = CGF.Reactions(ReplicableAdded, ReplicableIterate)

    def __init__(self):
        super(DisplayReplicableValuesSystem, self).__init__()
        self.totalReplicationCount = 0

    def update(self):
        q = CGF.CommandQueue(self.gom)
        for go, replicable in self.reaction(self.ReplicableAdded):
            replicable.onReplicated += self.__onReplicationDone
            q.removeComponent(go, GenericComponents.DynamicModelComponent)
            if replicable.assetIndex < len(replicable.assets):
                q.createComponent(go, GenericComponents.DynamicModelComponent, replicable.assets[replicable.assetIndex])

        for replicable, text in self.reaction(self.ReplicableIterate):
            text.addFrameText('Total Replication Count: {0}'.format(self.totalReplicationCount))
            text.addFrameText('int: {0}'.format(replicable.replicableInt))
            text.addFrameText('float: {0}'.format(replicable.replicableFloat))
            text.addFrameText('Vector3: {0}'.format(replicable.replicableVector3))
            text.addFrameText(replicable.replicableString)
            text.addFrameText('List: {0}'.format(replicable.replicableStringList))

    def __onReplicationDone(self, prev, new):
        self.totalReplicationCount += 1
