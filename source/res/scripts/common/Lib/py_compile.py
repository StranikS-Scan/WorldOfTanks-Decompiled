# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/py_compile.py
import __builtin__
import imp
import marshal
import os
import sys
import traceback
MAGIC = imp.get_magic()
__all__ = ['compile', 'main', 'PyCompileError']

class PyCompileError(Exception):

    def __init__(self, exc_type, exc_value, file, msg=''):
        exc_type_name = exc_type.__name__
        if exc_type is SyntaxError:
            tbtext = ''.join(traceback.format_exception_only(exc_type, exc_value))
            errmsg = tbtext.replace('File "<string>"', 'File "%s"' % file)
        else:
            errmsg = 'Sorry: %s: %s' % (exc_type_name, exc_value)
        Exception.__init__(self, msg or errmsg, exc_type_name, exc_value, file)
        self.exc_type_name = exc_type_name
        self.exc_value = exc_value
        self.file = file
        self.msg = msg or errmsg

    def __str__(self):
        return self.msg


def wr_long(f, x):
    f.write(chr(x & 255))
    f.write(chr(x >> 8 & 255))
    f.write(chr(x >> 16 & 255))
    f.write(chr(x >> 24 & 255))


def compile(file, cfile=None, dfile=None, doraise=False):
    with open(file, 'U') as f:
        try:
            timestamp = long(os.fstat(f.fileno()).st_mtime)
        except AttributeError:
            timestamp = long(os.stat(file).st_mtime)

        codestring = f.read()
    try:
        codeobject = __builtin__.compile(codestring, dfile or file, 'exec')
    except Exception as err:
        py_exc = PyCompileError(err.__class__, err, dfile or file)
        if doraise:
            raise py_exc
        else:
            sys.stderr.write(py_exc.msg + '\n')
            return

    if cfile is None:
        cfile = file + (__debug__ and 'c' or 'o')
    with open(cfile, 'wb') as fc:
        fc.write('\x00\x00\x00\x00')
        wr_long(fc, timestamp)
        marshal.dump(codeobject, fc)
        fc.flush()
        fc.seek(0, 0)
        fc.write(MAGIC)
    return


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    rv = 0
    if args == ['-']:
        while True:
            filename = sys.stdin.readline()
            if not filename:
                break
            filename = filename.rstrip('\n')
            try:
                compile(filename, doraise=True)
            except PyCompileError as error:
                rv = 1
                sys.stderr.write('%s\n' % error.msg)
            except IOError as error:
                rv = 1
                sys.stderr.write('%s\n' % error)

    else:
        for filename in args:
            try:
                compile(filename, doraise=True)
            except PyCompileError as error:
                rv = 1
                sys.stderr.write('%s\n' % error.msg)

    return rv


if __name__ == '__main__':
    sys.exit(main())
