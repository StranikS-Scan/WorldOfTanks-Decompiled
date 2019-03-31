# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_array_in_pointer.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *
from binascii import hexlify
import re

def dump(obj):
    h = hexlify(buffer(obj))
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
        self.failUnlessEqual('00-00-00-00', dump(val_array))
        for i in range(4):
            c.pvalues[i].val = i + 1

        values = [ c.pvalues[i].val for i in range(4) ]
        self.failUnlessEqual((values, dump(val_array)), ([1,
          2,
          3,
          4], '01-02-03-04'))

    def test_2(self):
        val_array = (Value * 4)()
        self.failUnlessEqual('00-00-00-00', dump(val_array))
        ptr = cast(val_array, POINTER(Value))
        for i in range(4):
            ptr[i].val = i + 1

        values = [ ptr[i].val for i in range(4) ]
        self.failUnlessEqual((values, dump(val_array)), ([1,
          2,
          3,
          4], '01-02-03-04'))


if __name__ == '__main__':
    unittest.main()
