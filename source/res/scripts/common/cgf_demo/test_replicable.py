# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_replicable.py
import CGF
import Math
from Event import Event
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerReplicableComponent

@registerReplicableComponent
class TestReplicableComponent(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Replication Types'
    replicableInt = ComponentProperty(type=CGFMetaTypes.INT, editorName='IntValue', value=777)
    replicableFloat = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Float Value', value=10.0)
    replicableString = ComponentProperty(type=CGFMetaTypes.STRING, editorName='States', value='Test String')
    replicableVector3 = ComponentProperty(type=CGFMetaTypes.VECTOR3, editorName='States', value=Math.Vector3(1.0, 2.0, 3.0))
    replicableStringList = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='States', value=('one', 'two', 'three'))
    assetIndex = ComponentProperty(type=CGFMetaTypes.INT, editorName='Default asset', value=0)
    assets = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='Models')

    def __init__(self):
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
