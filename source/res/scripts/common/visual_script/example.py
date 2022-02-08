# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/example.py
import BigWorld
from block import Block, Meta, InitParam, buildStrKeysValue, makeResEditorData
from slot_types import SLOT_TYPE, arrayOf
from visual_script.misc import ASPECT, BLOCK_MODE, EDITOR_TYPE
from tunable_event_block import TunableEventBlock
from type import VScriptType, VScriptEnum, VScriptStruct, VScriptStructField
import weakref

class Example(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def mode(cls):
        return BLOCK_MODE.DEV


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
        res = sum(self._inArray.getValue(), 0.0)
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


class AnimalComplexKeySelect(Block, Example):
    animals = [('Carnivorous', ('Tiger', 'Lion', 'Cat')), ('Herbivorous', ('Moose', 'Deer', 'Cow'))]

    def __init__(self, *args, **kwargs):
        super(AnimalComplexKeySelect, self).__init__(*args, **kwargs)
        animal, count = self._getInitParams()
        type_, name = animal.split('.')
        self.a = self._makeDataOutputSlot('animalType', SLOT_TYPE.STR, None)
        self.a.setValue(type_)
        self.b = self._makeDataOutputSlot('animalName', SLOT_TYPE.STR, None)
        self.b.setValue(name)
        self.c = self._makeDataOutputSlot('count', SLOT_TYPE.INT, None)
        self.c.setValue(count)
        return

    @classmethod
    def initParams(cls):
        return [InitParam('Type, Name', SLOT_TYPE.STR, 'Herbivorous.Deer', EDITOR_TYPE.COMPLEX_KEY_SELECTOR, AnimalComplexKeySelect.animals), InitParam('Count', SLOT_TYPE.INT, 0)]


class TestTunableEvent(TunableEventBlock, Example):

    def __init__(self, *args, **kwargs):
        super(TestTunableEvent, self).__init__(*args, **kwargs)
        self._t = self._makeDataInputSlot('time', SLOT_TYPE.FLOAT)
        self._a = self._makeDataInputSlot('value', SLOT_TYPE.FLOAT)
        self._res = self._makeDataOutputSlot('sqr value', SLOT_TYPE.FLOAT, None)
        self._cbID = None
        return

    def onStartScript(self):
        from constants import IS_VS_EDITOR
        if not IS_VS_EDITOR:
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


class ModeBlock(Block, Example):

    def __init__(self, *args, **kwargs):
        super(ModeBlock, self).__init__(*args, **kwargs)
        self._out = self._makeDataOutputSlot('mode', SLOT_TYPE.INT, None)
        self._out.setValue(self.mode())
        return

    @classmethod
    def mode(cls):
        return BLOCK_MODE.UNIQUE | Example.mode()


class ClampedBlockEx(Block, Example):

    def __init__(self, *args, **kwargs):
        super(ClampedBlockEx, self).__init__(*args, **kwargs)
        self._int = self._makeDataInputSlot('int [0, 100]', SLOT_TYPE.INT)
        self._int.setEditorData([0, 100])
        self._float = self._makeDataInputSlot('float [0, 1]', SLOT_TYPE.FLOAT)
        self._float.setEditorData([0.0, 1.0])
        self._angle = self._makeDataInputSlot('angle [-45, 45]', SLOT_TYPE.ANGLE)
        self._angle.setEditorData([-45.0, 45.0])


class ClampedBlock(Block, Example):

    def __init__(self, *args, **kwargs):
        super(ClampedBlock, self).__init__(*args, **kwargs)
        value = self._getInitParams()
        self._int = self._makeDataOutputSlot('res', SLOT_TYPE.INT, None)
        self._int.setValue(value)
        return

    @classmethod
    def initParams(cls):
        return [InitParam('value [0, 100]', SLOT_TYPE.INT, 0, None, [0, 100])]


class TestStruct(VScriptStruct):
    name = VScriptStructField('name', SLOT_TYPE.STR)
    value = VScriptStructField('year', SLOT_TYPE.INT)

    def __repr__(self):
        return 'TestStruct(name = {}, year = {})'.format(self.name, self.value)


class TestType(VScriptType):

    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def vs_connectionColor(cls):
        pass


class TestEnum(VScriptEnum):
    A = 0
    B = 1
    C = 2


class MakeTestType(Block, Example):

    def __init__(self, *args, **kwargs):
        super(MakeTestType, self).__init__(*args, **kwargs)
        self._name = self._makeDataInputSlot('name', SLOT_TYPE.STR)
        self._age = self._makeDataInputSlot('age', SLOT_TYPE.INT)
        self._out = self._makeDataOutputSlot('data', TestType.slotType(), self._exec)

    def _exec(self):
        self._out.setValue(TestType(self._name.getValue(), self._age.getValue()))


class BreakTestType(Block, Example):

    def __init__(self, *args, **kwargs):
        super(BreakTestType, self).__init__(*args, **kwargs)
        self._in = self._makeDataInputSlot('in', TestType.slotType())
        self._name = self._makeDataOutputSlot('name', SLOT_TYPE.STR, self._execName)
        self._age = self._makeDataOutputSlot('age', SLOT_TYPE.INT, self._execAge)

    def _execName(self):
        self._name.setValue(self._in.getValue().name)

    def _execAge(self):
        self._age.setValue(self._in.getValue().age)


class MakeTestTypeArray(Block, Example):

    def __init__(self, *args, **kwargs):
        super(MakeTestTypeArray, self).__init__(*args, **kwargs)
        self._out = self._makeDataOutputSlot('data', arrayOf(TestType.slotType()), None)
        self._out.setValue([TestType('Bob', 1945), TestType('Marley', 1981)])
        return


class SelectTest(Block, Example):

    def __init__(self, *args, **kwargs):
        super(SelectTest, self).__init__(*args, **kwargs)
        self._enum = self._makeDataInputSlot('enumValue', TestEnum.slotType())
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.INT, self._exec)

    def _exec(self):
        v = self._enum.getValue()
        self._res.setValue(v)


class PrintTestStruct(Block, Example):

    def __init__(self, *args, **kwargs):
        super(PrintTestStruct, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._s = self._makeDataInputSlot('struct', TestStruct.slotType())
        self._ns = self._makeDataOutputSlot('changed', TestStruct.slotType(), None)
        return

    def _exec(self):
        self._writeLog('PrintTestStruct: {}'.format(self._s.getValue()))
        newStuct = TestStruct()
        newStuct.name = 'Metallica'
        newStuct.value = 1981
        self._ns.setValue(newStuct)
        self._out.call()
