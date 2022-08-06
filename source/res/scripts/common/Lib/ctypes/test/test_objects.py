# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_objects.py
import unittest, doctest, sys
import ctypes.test.test_objects

class TestCase(unittest.TestCase):

    def test(self):
        failures, tests = doctest.testmod(ctypes.test.test_objects)
        self.assertFalse(failures, 'doctests failed, see output above')


if __name__ == '__main__':
    doctest.testmod(ctypes.test.test_objects)
