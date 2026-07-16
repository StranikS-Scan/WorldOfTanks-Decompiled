# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/demo_module.py
from __future__ import absolute_import
import CGF
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_demo_client.test_gun_effects_controller import EntranceSingleShotSystem, EntranceContinuousBurstSystem
from cgf_script.registration import registerModule
from cgf_demo_client.test_hierarchy_modificator import HierarchyModifier, HierarchyModifier2, ModelSwapperSystem, TestHierarchyModifierSystem, TestMaterialManipulatorSystem, TestMaterialParamManipulator, TestModelSwapper
from cgf_demo_client.test_state_machine_trigger import StateMachineActivatorSystem, TestStateMachineStatesActivator
from cgf_demo_client.test_triggers import EntranceModifierSystem, ShowHealthInfoComponent, TestEntranceNotifier, TestHealthMonitoringSystem
from cgf_demo_client.test_physical_debris_spawner import EntranceSpawnerSystem, TestEntranceSpawner
from cgf_demo_client.test_death_triggers import TestAddDeathByTrigger, TestDeathByTriggerSystem, TestRemoveDeathByTrigger
from cgf_demo_client.test_client_component import ClientTestSystem, ClientTestComponent
from constants import IS_CLIENT
if IS_CLIENT:
    from TestReplicableComponent import DisplayReplicableValuesSystem
else:

    class DisplayReplicableValuesSystem(object):
        Reactions = CGF.Reactions()


@registerModule
class TestClientDemoModule(object):
    name = 'Test Client Demo Module'
    group = DEMO_CATEGORY
    systems = [CGF.RegisterSystem(EntranceModifierSystem),
     CGF.RegisterSystem(StateMachineActivatorSystem),
     CGF.RegisterSystem(ModelSwapperSystem, updateBefore=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(DisplayReplicableValuesSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(EntranceSpawnerSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(TestHealthMonitoringSystem, updateBefore=(CGF.TransformUpdateSystem,), domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(TestHierarchyModifierSystem, updateBefore=(CGF.TransformUpdateSystem,), domain=CGF.Domain.Client),
     CGF.RegisterSystem(TestMaterialManipulatorSystem, updateBefore=(CGF.TransformUpdateSystem,), domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(TestDeathByTriggerSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(ClientTestSystem, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(EntranceSingleShotSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(EntranceContinuousBurstSystem, domain=CGF.Domain.Client)]
    components = [ClientTestComponent,
     TestAddDeathByTrigger,
     TestRemoveDeathByTrigger,
     TestMaterialParamManipulator,
     HierarchyModifier,
     HierarchyModifier2,
     TestModelSwapper,
     TestEntranceSpawner,
     TestStateMachineStatesActivator,
     ShowHealthInfoComponent,
     TestEntranceNotifier]
