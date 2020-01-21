# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/example.py
from block import Block, Meta, InitParam, SLOT_TYPE

class Example(Meta):

    @classmethod
    def blockCategory(cls):
        pass


class HelloFromPython(Block, Example):

    def __init__(self, *args, **kwargs):
        super(HelloFromPython, self).__init__(*args, **kwargs)
        self._inSlot = self._makeDataInputSlot('project_name', SLOT_TYPE.STR)
        self._outSlot = self._makeDataOutputSlot('result', SLOT_TYPE.STR, HelloFromPython._execute)

    def _execute(self):
        res = ' '.join(('Hello', self._inSlot.getValue(), 'from python vse...'))
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
        self._arrayIn = self._makeDataInputSlot('array', SLOT_TYPE.INT_ARRAY)
        self._arrayOut = self._makeDataOutputSlot('res_array', SLOT_TYPE.INT_ARRAY, MulArray._execute)

    def _execute(self):
        array = self._arrayIn.getValue()
        mul = self._mulValue.getValue()
        array = map(lambda v: v * mul, array)
        self._arrayOut.setValue(array)


class SumArray(Block, Example):

    def __init__(self, *args, **kwargs):
        super(SumArray, self).__init__(*args, **kwargs)
        self._inArray = self._makeDataInputSlot('array', SLOT_TYPE.FLOAT_ARRAY)
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
