# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/general.py
import BigWorld
from block import Block, makeResEditorData, InitParam
from constants import IS_DEVELOPMENT
from slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, BLOCK_MODE

class Assert(Block):

    def __init__(self, *args, **kwargs):
        super(Assert, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', Assert._execute)
        self._value = self._makeDataInputSlot('value', SLOT_TYPE.BOOL)
        self._msg = self._makeDataInputSlot('msg', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self._out.call()

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def mode(cls):
        return BLOCK_MODE.DEV


class AddTestResult(Block):

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

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass


class TestCase(Block):

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', TestCase._execute)
        self._name = self._makeDataInputSlot('name', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self._out.call()

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def mode(cls):
        return BLOCK_MODE.DEV


class ResourceSelector(Block):

    def __init__(self, *args, **kwargs):
        super(ResourceSelector, self).__init__(*args, **kwargs)
        root, ext = self._getInitParams()
        self._res = self._makeDataInputSlot('res', SLOT_TYPE.RESOURCE)
        self._res.setEditorData(makeResEditorData(root, ext))
        self._out = self._makeDataOutputSlot('out', SLOT_TYPE.RESOURCE, self._exec)

    def _exec(self):
        self._out.setValue(self._res.getValue())

    @classmethod
    def initParams(cls):
        return [InitParam('root', SLOT_TYPE.STR, 'wot'), InitParam('ext', SLOT_TYPE.STR, 'xml')]
