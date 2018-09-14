# Embedded file name: scripts/common/Lib/ctypes/test/test_array_in_pointer.py
import unittest
from ctypes import *
from binascii import hexlify
import re

def dump(obj):
    h = hexlify(memoryview(obj))
    return re.sub('(..)', '\\1-', h)[:-1]


class Value(Structure):
    _fields_ = [('val', c_byte)]


class Container(Structure):
    _fields_ = [('pvalues', POINTER(Value))]


class Test(unittest.TestCase):

    def test(self):
        val_array = (Value * 4)()
        c = Container()
        c.pvalues = val_array
        self.assertEqual('00-00-00-00', dump(val_array))
        for i in range(4):
            c.pvalues[i].val = i + 1

        values = [ c.pvalues[i].val for i in range(4) ]
        self.assertEqual((values, dump(val_array)), ([1,
          2,
          3,
          4], '01-02-03-04'))

    def test_2(self):
        val_array = (Value * 4)()
        self.assertEqual('00-00-00-00', dump(val_array))
        ptr = cast(val_array, POINTER(Value))
        for i in range(4):
            ptr[i].val = i + 1

        values = [ ptr[i].val for i in range(4) ]
        self.assertEqual((values, dump(val_array)), ([1,
          2,
          3,
          4], '01-02-03-04'))


if __name__ == '__main__':
    unittest.main()
