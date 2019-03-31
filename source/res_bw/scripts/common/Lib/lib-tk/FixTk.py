# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/FixTk.py
# Compiled at: 2010-05-25 20:46:16
import sys, os
try:
    import ctypes
    ctypes.windll.kernel32.GetFinalPathNameByHandleW
except (ImportError, AttributeError):

    def convert_path(s):
        return s


else:

    def convert_path(s):
        if isinstance(s, str):
            s = s.decode('mbcs')
        hdir = ctypes.windll.kernel32.CreateFileW(s, 128, 1, None, 3, 33554432, None)
        if hdir == -1:
            return s
        else:
            buf = ctypes.create_unicode_buffer(u'', 32768)
            res = ctypes.windll.kernel32.GetFinalPathNameByHandleW(hdir, buf, len(buf), 0)
            ctypes.windll.kernel32.CloseHandle(hdir)
            if res == 0:
                return s
            s = buf[:res]
            if s.startswith(u'\\\\?\\'):
                s = s[4:]
            return s


prefix = os.path.join(sys.prefix, 'tcl')
if not os.path.exists(prefix):
    prefix = os.path.join(sys.prefix, os.path.pardir, 'tcltk', 'lib')
    prefix = os.path.abspath(prefix)
if os.path.exists(prefix):
    prefix = convert_path(prefix)
    if not os.environ.has_key('TCL_LIBRARY'):
        for name in os.listdir(prefix):
            if name.startswith('tcl'):
                tcldir = os.path.join(prefix, name)
                if os.path.isdir(tcldir):
                    os.environ['TCL_LIBRARY'] = tcldir

    import _tkinter
    ver = str(_tkinter.TCL_VERSION)
    if not os.environ.has_key('TK_LIBRARY'):
        v = os.path.join(prefix, 'tk' + ver)
        if os.path.exists(os.path.join(v, 'tclIndex')):
            os.environ['TK_LIBRARY'] = v
    if not os.environ.has_key('TIX_LIBRARY'):
        for name in os.listdir(prefix):
            if name.startswith('tix'):
                tixdir = os.path.join(prefix, name)
                if os.path.isdir(tixdir):
                    os.environ['TIX_LIBRARY'] = tixdir
