# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/qa_education_blocks.py
import math
from block import Block
from slot_types import SLOT_TYPE
from qa_blocks import QAMeta

class CheckTriangleLesson1(Block, QAMeta):

    def __init__(self, *args, **kwargs):
        super(CheckTriangleLesson1, self).__init__(*args, **kwargs)
        self._a = self._makeDataInputSlot('a', SLOT_TYPE.FLOAT)
        self._b = self._makeDataInputSlot('b', SLOT_TYPE.FLOAT)
        self._c = self._makeDataOutputSlot('c', SLOT_TYPE.FLOAT, self._ex_c)
        self._S = self._makeDataOutputSlot('S', SLOT_TYPE.FLOAT, self._ex_s)

    def _ex_c(self):
        self._c.setValue(math.sqrt(self._a.getValue() ** 2 + self._b.getValue() ** 2))

    def _ex_s(self):
        self._S.setValue(0.5 * self._a.getValue() * self._b.getValue())

    def validate(self):
        if not self._a.hasValue():
            return 'a value is required'
        return 'b value is required' if not self._b.hasValue() else None

    @classmethod
    def blockCategory(cls):
        pass


class CheckTriangleLesson2(Block, QAMeta):

    def __init__(self, *args, **kwargs):
        super(CheckTriangleLesson2, self).__init__(*args, **kwargs)
        self._r = self._makeDataInputSlot('r', SLOT_TYPE.FLOAT)
        self._S = self._makeDataInputSlot('S', SLOT_TYPE.FLOAT)
        self._a = self._makeDataOutputSlot('a', SLOT_TYPE.FLOAT, self._ex_a)
        self._b = self._makeDataOutputSlot('b', SLOT_TYPE.FLOAT, self._ex_b)
        self._c = self._makeDataOutputSlot('c', SLOT_TYPE.FLOAT, self._ex_c)

    def _ex_a(self):
        self._a.setValue(0.5 * (self._r.getValue() + self._S.getValue() / self._r.getValue() - math.sqrt(self._r.getValue() ** 2 - 6 * self._S.getValue() + self._S.getValue() ** 2 / self._r.getValue() ** 2)))

    def _ex_b(self):
        self._b.setValue(0.5 * (self._r.getValue() + self._S.getValue() / self._r.getValue() + math.sqrt(self._r.getValue() ** 2 - 6 * self._S.getValue() + self._S.getValue() ** 2 / self._r.getValue() ** 2)))

    def _ex_c(self):
        self._c.setValue(self._S.getValue() / self._r.getValue() - self._r.getValue())

    def validate(self):
        if not self._r.hasValue():
            return 'r value is required'
        return 'S value is required' if not self._S.hasValue() else None

    @classmethod
    def blockCategory(cls):
        pass
