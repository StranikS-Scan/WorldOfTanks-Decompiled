# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_replicable.py
from __future__ import absolute_import
import Math
import CGF
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.registration import ComponentProperty

class TestReplicableComponentDescriptor(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Replication Types'
    replicableInt = ComponentProperty(type=CGF.PropertyType.Int, editorName='IntValue', value=777)
    replicableFloat = ComponentProperty(type=CGF.PropertyType.Float, editorName='Float Value', value=10.0)
    replicableString = ComponentProperty(type=CGF.PropertyType.String, editorName='States', value='Test String')
    replicableVector3 = ComponentProperty(type=CGF.PropertyType.Vector3, editorName='States', value=Math.Vector3(1.0, 2.0, 3.0))
    replicableStringList = ComponentProperty(type=CGF.PropertyType.StringList, editorName='States', value=('one', 'two', 'three'))
    assetIndex = ComponentProperty(type=CGF.PropertyType.Int, editorName='Default asset', value=0)
    assets = ComponentProperty(type=CGF.PropertyType.StringList, editorName='Models')
