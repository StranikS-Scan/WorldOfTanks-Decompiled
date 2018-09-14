# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_find.py
import unittest
import sys
from ctypes import *
from ctypes.util import find_library
from ctypes.test import is_resource_enabled
if sys.platform == 'win32':
    lib_gl = find_library('OpenGL32')
    lib_glu = find_library('Glu32')
    lib_gle = None
elif sys.platform == 'darwin':
    lib_gl = lib_glu = find_library('OpenGL')
    lib_gle = None
else:
    lib_gl = find_library('GL')
    lib_glu = find_library('GLU')
    lib_gle = find_library('gle')
if is_resource_enabled('printing'):
    if lib_gl or lib_glu or lib_gle:
        print 'OpenGL libraries:'
        for item in (('GL', lib_gl), ('GLU', lib_glu), ('gle', lib_gle)):
            print '\t', item

class Test_OpenGL_libs(unittest.TestCase):

    def setUp(self):
        self.gl = self.glu = self.gle = None
        if lib_gl:
            self.gl = CDLL(lib_gl, mode=RTLD_GLOBAL)
        if lib_glu:
            self.glu = CDLL(lib_glu, RTLD_GLOBAL)
        if lib_gle:
            try:
                self.gle = CDLL(lib_gle)
            except OSError:
                pass

        return

    if lib_gl:

        def test_gl(self):
            if self.gl:
                self.gl.glClearIndex

    if lib_glu:

        def test_glu(self):
            if self.glu:
                self.glu.gluBeginCurve

    if lib_gle:

        def test_gle(self):
            if self.gle:
                self.gle.gleGetJoinStyle


if __name__ == '__main__':
    unittest.main()
