# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_module.py
from __future__ import absolute_import
import CGF
import logging
from constants import IS_CLIENT, IS_EDITOR
from cgf_script.registration import registerModule
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_demo.test_bridge import TestBridgeSystem, TestBridge
from cgf_demo.test_movers import TestAxisRotatorSystem, TestScriptAxisRotator, TestScriptMover
from cgf_demo.test_triggers import TestComponentCreation, TestComponentCreationSystem, TestHealthTriggersComponent, TestPrefabSpawner, TestRotateWhileInTrigger, TestTriggersSystem, TestVehicleAreaTriggerComponent
if IS_CLIENT or IS_EDITOR:
    from cgf_demo.test_edge_drawer import TestEdgeDrawerComponentSystem
    from cgf_demo.test_edge_drawer import TestEdgeDrawerComponent
else:

    class TestEdgeDrawerComponentSystem(object):
        Reactions = CGF.Reactions()


    class TestEdgeDrawerComponent(object):
        pass


_logger = logging.getLogger(__name__)

@registerModule
class TestModule(object):
    name = 'Test Module'
    group = DEMO_CATEGORY
    systems = [CGF.RegisterSystem(TestBridgeSystem, updateBefore=(CGF.TransformUpdateSystem,), domain=CGF.Domain.ClientServer),
     CGF.RegisterSystem(TestAxisRotatorSystem, updateBefore=(CGF.TransformUpdateSystem,), domain=CGF.Domain.ClientServer),
     CGF.RegisterSystem(TestTriggersSystem, updateBefore=(CGF.TransformUpdateSystem,), domain=CGF.Domain.ClientServer),
     CGF.RegisterSystem(TestComponentCreationSystem, domain=CGF.Domain.ClientServer),
     CGF.RegisterSystem(TestEdgeDrawerComponentSystem, domain=CGF.Domain.Client)]
    components = [TestBridge,
     TestEdgeDrawerComponent,
     TestScriptAxisRotator,
     TestScriptMover,
     TestRotateWhileInTrigger,
     TestComponentCreation,
     TestPrefabSpawner,
     TestVehicleAreaTriggerComponent,
     TestHealthTriggersComponent]
