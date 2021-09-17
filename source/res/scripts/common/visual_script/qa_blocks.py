# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/qa_blocks.py
from block import Block, Meta, InitParam, buildStrKeysValue, EDITOR_TYPE
from slot_types import SLOT_TYPE, arrayOf
from misc import BLOCK_MODE

class QAMeta(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def mode(cls):
        return BLOCK_MODE.DEV


class TestIdentifier(Block, QAMeta):

    def __init__(self, *args, **kwargs):
        super(TestIdentifier, self).__init__(*args, **kwargs)
        self._nameType = self._getInitParams()
        if self._nameType == 'single id':
            self.inInt = self._makeDataInputSlot('test_id', SLOT_TYPE.INT)
            self.outID = self._makeDataOutputSlot('Identifier', SLOT_TYPE.ID, self._execute)
        elif self._nameType == 'array of IDs':
            self.inInt = self._makeDataInputSlot('multiple_test_ids', arrayOf(SLOT_TYPE.INT))
            self.outID = self._makeDataOutputSlot('Array of Identifiers', arrayOf(SLOT_TYPE.ID), self._execute)

    def _execute(self):
        res = self.inInt.getValue()
        self.outID.setValue(res)

    @classmethod
    def initParams(cls):
        return [InitParam('amount of test IDs', SLOT_TYPE.STR, buildStrKeysValue('single id', 'array of IDs'), EDITOR_TYPE.STR_KEY_SELECTOR)]


class TestSlotPyObjectToArrayVSEBlock(Block, QAMeta):

    def __init__(self, *args, **kwargs):
        super(TestSlotPyObjectToArrayVSEBlock, self).__init__(*args, **kwargs)
        self._res = self._makeDataOutputSlot('res', arrayOf(SLOT_TYPE.STR), self._exec)

    def _exec(self):
        self._res.setValue(set([1, 2, 3]))
