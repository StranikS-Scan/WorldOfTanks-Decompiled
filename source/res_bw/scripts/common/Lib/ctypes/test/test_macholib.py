# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_macholib.py
# Compiled at: 2010-05-25 20:46:16
import os
import sys
import unittest
from ctypes.macholib.dyld import dyld_find

def find_lib(name):
    possible = ['lib' + name + '.dylib', name + '.dylib', name + '.framework/' + name]
    for dylib in possible:
        try:
            return os.path.realpath(dyld_find(dylib))
        except ValueError:
            pass

    raise ValueError('%s not found' % (name,))


class MachOTest(unittest.TestCase):
    if sys.platform == 'darwin':

        def test_find(self):
            self.failUnlessEqual(find_lib('pthread'), '/usr/lib/libSystem.B.dylib')
            result = find_lib('z')
            self.failUnless(result.startswith('/usr/lib/libz.1'))
            self.failUnless(result.endswith('.dylib'))
            self.failUnlessEqual(find_lib('IOKit'), '/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit')


if __name__ == '__main__':
    unittest.main()
