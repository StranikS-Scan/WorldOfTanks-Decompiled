# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/demo_rules.py
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_demo_client.test_hierarchy_modificator import ModelSwapperManager
from cgf_demo_client.test_state_machine_trigger import StateMachineActivatorManager
from cgf_demo_client.test_triggers import EntranceModifierManager
from cgf_script.managers_registrator import Rule, registerManager

class TestClientDemoRules(Rule):
    category = DEMO_CATEGORY

    @registerManager(EntranceModifierManager)
    def registerEntranceModifier(self):
        return None

    @registerManager(StateMachineActivatorManager)
    def registerStateActivator(self):
        return None

    @registerManager(ModelSwapperManager)
    def registerModelSwapper(self):
        return None
