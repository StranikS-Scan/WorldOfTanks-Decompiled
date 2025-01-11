# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/visual_script_client/ability_context.py
from visual_script import ASPECT
from visual_script.context import vse_get_property
from visual_script.slot_types import SLOT_TYPE
from visual_script_client import AbilityContextClient

class StackableAbilityContextClient(AbilityContextClient):

    def __init__(self, *args, **kwargs):
        super(StackableAbilityContextClient, self).__init__(*args, **kwargs)
        self.stacks = 0

    def updateStacks(self, stacks):
        self.stacks = stacks

    @vse_get_property(SLOT_TYPE.INT, display_name='GetAbilityStacks', description='returns available ability stacks', aspects=[ASPECT.CLIENT])
    def getAbilityStacks(self):
        return int(self.stacks)
