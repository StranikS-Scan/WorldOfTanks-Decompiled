# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/qa_blocks.py
import BigWorld
from block import Block, Meta, InitParam, buildStrKeysValue, makeResEditorData
from slot_types import SLOT_TYPE, arrayOf
from misc import ASPECT, BLOCK_MODE, EDITOR_TYPE
from constants import IS_DEVELOPMENT

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


class Assert(Block, QAMeta):

    def __init__(self, *args, **kwargs):
        super(Assert, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', Assert._execute)
        self._value = self._makeDataInputSlot('value', SLOT_TYPE.BOOL)
        self._msg = self._makeDataInputSlot('msg', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self._out.call()


class AddTestResult(Block, QAMeta):

    def __init__(self, *args, **kwargs):
        super(AddTestResult, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._success = self._makeDataInputSlot('success', SLOT_TYPE.BOOL)
        self._msg = self._makeDataInputSlot('msg', SLOT_TYPE.STR)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._out = self._makeEventOutputSlot('out')

    @property
    def _storageKey(self):
        arena = self._arena.getValue()
        runnerID = arena.ai.gameMode.arenaInfo.runnerID
        return 'runnerID_%d' % runnerID

    def _execute(self):
        if not IS_DEVELOPMENT:
            return
        BigWorld.globalData[self._storageKey]['results'].append(dict(success=self._success.getValue(), message=self._msg.getValue()))
        BigWorld.globalData[self._storageKey] = BigWorld.globalData[self._storageKey]
        self._out.call()

    def onStartScript(self):
        if not IS_DEVELOPMENT:
            return
        arena = self._arena.getValue()
        BigWorld.globalData[self._storageKey] = dict(arenaID=arena.id, results=[])

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]


class TestCase(Block):

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', TestCase._execute)
        self._name = self._makeDataInputSlot('name', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self._out.call()
