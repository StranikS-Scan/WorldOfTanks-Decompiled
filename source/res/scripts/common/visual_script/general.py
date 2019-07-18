# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/general.py
from component import Component, InputSlot, OutputSlot, SLOT_TYPE

class Assert(Component):

    @classmethod
    def componentColor(cls):
        pass

    def slotDefinitions(self):
        return [InputSlot('in', SLOT_TYPE.EVENT, Assert._execute),
         InputSlot('value', SLOT_TYPE.BOOL, None),
         InputSlot('msg', SLOT_TYPE.STR, None),
         OutputSlot('out', SLOT_TYPE.EVENT, None)]

    def _execute(self, value, msg):
        pass


class TestCase(Component):

    @classmethod
    def componentColor(cls):
        pass

    def slotDefinitions(self):
        return [InputSlot('in', SLOT_TYPE.EVENT, TestCase._execute), InputSlot('name', SLOT_TYPE.STR, None), OutputSlot('out', SLOT_TYPE.EVENT, None)]

    def _execute(self, name):
        pass
