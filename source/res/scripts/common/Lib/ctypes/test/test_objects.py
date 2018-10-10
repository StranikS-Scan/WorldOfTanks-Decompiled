# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_objects.py
import unittest, doctest, sys
import ctypes.test.test_objects

class TestCase(unittest.TestCase):
    if sys.hexversion > 33816576:

        def test(self):
            doctest.testmod(ctypes.test.test_objects)


if __name__ == '__main__':
    if sys.hexversion > 33816576:
        doctest.testmod(ctypes.test.test_objects)
