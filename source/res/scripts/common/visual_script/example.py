# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/example.py
import BigWorld
from block import Block, Meta, InitParam, EDITOR_TYPE, buildStrKeysValue
from slot_types import SLOT_TYPE, arrayOf
from visual_script.misc import ASPECT
from tunable_event_block import TunableEventBlock
import weakref

class Example(Meta):

    @classmethod
    def blockCategory(cls):
        pass


class HelloFromPython(Block, Example):

    def __init__(self, *args, **kwargs):
        super(HelloFromPython, self).__init__(*args, **kwargs)
        self._inSlot = self._makeDataInputSlot('project_name', SLOT_TYPE.STR)
        self._outSlot = self._makeDataOutputSlot('result', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        res = ' '.join(('Hello', self._inSlot.getValue(), 'from python vse...'))
        self._outSlot.setValue(res)


class HelloFromPythonOverride(HelloFromPython):

    def _execute(self):
        res = ' '.join(('(Override) Hello', self._inSlot.getValue(), 'from python vse...'))
        self._outSlot.setValue(res)


class StringSelectorExample(Block, Example):

    def __init__(self, *args, **kwargs):
        super(StringSelectorExample, self).__init__(*args, **kwargs)
        self._inSlot = self._makeDataInputSlot('in_slot', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._inSlot.setEditorData(['my string 1', 'my string 2', 'my string 3'])
        self._outSlot = self._makeDataOutputSlot('result', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        res = ' '.join(('String', self._inSlot.getValue(), 'was selected'))
        self._outSlot.setValue(res)


class GetProjectName(Block, Example):

    def __init__(self, *args, **kwargs):
        super(GetProjectName, self).__init__(*args, **kwargs)
        self._outSlot = self._makeDataOutputSlot('result', SLOT_TYPE.STR, GetProjectName._execute)

    def _execute(self):
        self._outSlot.setValue('Wot')


class PrintToTerminal(Block, Example):

    def __init__(self, *args, **kwargs):
        super(PrintToTerminal, self).__init__(*args, **kwargs)
        self._inSlot = self._makeEventInputSlot('in', PrintToTerminal._execute)
        self._outSlot = self._makeEventOutputSlot('out')
        self._msgSlot = self._makeDataInputSlot('msg', SLOT_TYPE.STR)

    def _execute(self):
        self._writeLog('PrintToTerminal:MSG = ' + self._msgSlot.getValue())
        self._outSlot.call()


class MulArray(Block, Example):

    def __init__(self, *args, **kwargs):
        super(MulArray, self).__init__(*args, **kwargs)
        self._mulValue = self._makeDataInputSlot('mulVal', SLOT_TYPE.INT)
        self._arrayIn = self._makeDataInputSlot('array', arrayOf(SLOT_TYPE.INT))
        self._arrayOut = self._makeDataOutputSlot('res_array', arrayOf(SLOT_TYPE.INT), MulArray._execute)

    def _execute(self):
        array = self._arrayIn.getValue()
        mul = self._mulValue.getValue()
        array = map(lambda v: v * mul, array)
        self._arrayOut.setValue(array)


class SumArray(Block, Example):

    def __init__(self, *args, **kwargs):
        super(SumArray, self).__init__(*args, **kwargs)
        self._inArray = self._makeDataInputSlot('array', arrayOf(SLOT_TYPE.FLOAT))
        self._out = self._makeDataOutputSlot('res', SLOT_TYPE.FLOAT, SumArray._execute)

    def _execute(self):
        res = sum(self._inArray.getValue())
        self._out.setValue(res)


class WeightSequence(Block, Example):

    def __init__(self, *args, **kwargs):
        super(WeightSequence, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', WeightSequence._execute)
        n = self._getInitParams()
        self._weightSlots = [ self._makeDataInputSlot('w' + str(i), SLOT_TYPE.FLOAT) for i in xrange(n) ]
        self._outSlots = [ self._makeEventOutputSlot('out' + str(i)) for i in xrange(n) ]

    def _execute(self):
        iterData = ((slot.getValue(), idx) for idx, slot in enumerate(self._weightSlots))
        for _, idx in sorted(iterData, key=lambda data: data[0], reverse=True):
            self._outSlots[idx].call()

    @classmethod
    def initParams(cls):
        return [InitParam('outCount', SLOT_TYPE.INT, 1)]


class SelectProjectID(Block, Example):
    convert = {'WoT': 0,
     'WoP': 1,
     'WoS': 2}

    def __init__(self, *args, **kwargs):
        super(SelectProjectID, self).__init__(*args, **kwargs)
        self.outSlot = self._makeDataOutputSlot('get', SLOT_TYPE.INT, None)
        self._name = self._getInitParams()
        self.outSlot.setValue(SelectProjectID.convert[self._name])
        return

    @classmethod
    def initParams(cls):
        return [InitParam('Names', SLOT_TYPE.STR, buildStrKeysValue(*cls.convert.keys()), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def captionText(self):
        return ' : '.join((self.__class__.__name__, self._name))


class TestTunableEvent(TunableEventBlock, Example):

    def __init__(self, *args, **kwargs):
        super(TestTunableEvent, self).__init__(*args, **kwargs)
        self._t = self._makeDataInputSlot('time', SLOT_TYPE.FLOAT)
        self._a = self._makeDataInputSlot('value', SLOT_TYPE.FLOAT)
        self._res = self._makeDataOutputSlot('sqr value', SLOT_TYPE.FLOAT, None)
        self._cbID = None
        return

    def onStartScript(self):
        from constants import IS_EDITOR
        if not IS_EDITOR:
            self._cbID = BigWorld.callback(self._t.getValue(), self._exec)

    def onFinishScript(self):
        if self._cbID is not None:
            BigWorld.cancelCallback(self._cbID)
            self._cbID = None
        return

    @TunableEventBlock.eventProcessor
    def _exec(self):
        a = self._a.getValue()
        self._res.setValue(a * a)
        self._cbID = BigWorld.callback(self._t.getValue(), self._exec)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
