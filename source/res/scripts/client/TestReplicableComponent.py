# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TestReplicableComponent.py
import BigWorld
import CGF
import GenericComponents
import GameplayDebug
import cgf_demo.test_replicable
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery

class TestReplicableComponent(BigWorld.DynamicScriptComponent, cgf_demo.test_replicable.TestReplicableComponent):
    pass


class DisplayReplicableValuesManager(CGF.ComponentManager):

    def __init__(self):
        super(DisplayReplicableValuesManager, self).__init__()
        self.totalReplicationCount = 0

    @onAddedQuery(TestReplicableComponent, CGF.GameObject)
    def onAddedType(self, r, go):
        r.onReplicated += self.__onReplicationDone
        go.removeComponentByType(GenericComponents.DynamicModelComponent)
        if r.assetIndex < len(r.assets):
            go.createComponent(GenericComponents.DynamicModelComponent, r.assets[r.assetIndex])

    @onProcessQuery(TestReplicableComponent, GameplayDebug.DebugTextComponent)
    def displayValues(self, r, text):
        text.addFrameText('Total Replication Count: {0}'.format(self.totalReplicationCount))
        text.addFrameText('int: {0}'.format(r.replicableInt))
        text.addFrameText('float: {0}'.format(r.replicableFloat))
        text.addFrameText('Vector3: {0}'.format(r.replicableVector3))
        text.addFrameText(r.replicableString)
        text.addFrameText('List: {0}'.format(r.replicableStringList))

    def __onReplicationDone(self, prev, new):
        self.totalReplicationCount += 1
