# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BWUtil.py
import ResMgr
from bwdebug import TRACE_MSG
from functools import partial, wraps
import sys, os
from types import GeneratorType
import BigWorld
try:
    orig_open = __builtins__['open']
except TypeError as e:
    orig_open = __builtins__.open

@partial
def bwResRelativeOpen(name, *args):
    """
    This method has been decorated with 'partial' to avoid using a function as 
    a bound method when stored as a class attribute (see WOWP-638). """
    try:
        absname = ResMgr.resolveToAbsolutePath(name)
    except Exception as e:
        raise IOError(2, str(e))

    absname = unicode(absname)
    return orig_open(absname, *args)


def monkeyPatchOpen():
    TRACE_MSG('BWUtil.monkeyPatchOpen: Patching open()')
    try:
        __builtins__['open'] = bwResRelativeOpen
    except TypeErorr as e:
        __builtins__.open = bwResRelativeOpen


def extendPath(path, name):
    """Extend path, this method is based on pkgutil.extend_path and will
    allow aid on supporting inheriting resource paths.
    
    Example usage:
    from BWUtil import extendPath
    __path__ = extendPath(__path__, __name__)
    """
    from pkgutil import extend_path
    path = extend_path(path, name)
    if not isinstance(path, list):
        return path
    pname = os.path.join(*name.split('.'))
    init_py = '__init__' + os.extsep + 'py'
    path = path[:]
    for dir in sys.path:
        if not isinstance(dir, basestring) or not ResMgr.isDir(dir):
            continue
        subdir = os.path.join(dir, pname)
        initfile = os.path.join(subdir, init_py)
        if subdir not in path and ResMgr.isFile(initfile):
            path.append(subdir)

    return path


class AsyncReturn(StopIteration):
    __slots__ = ['value']

    def __init__(self, value):
        self.value = value


def async(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        assert isinstance(gen, GeneratorType)
        promise = BigWorld.Promise()

        def stepGen(result):
            assert isinstance(result, BigWorld.Future)
            result.then(handleResult)

        def handle(func, *args):
            try:
                stepGen(func(*args))
            except AsyncReturn as r:
                promise.set_value(r.value)
            except StopIteration:
                promise.set_value(None)
            except BaseException as e:
                promise.set_exception(*sys.exc_info())

            return

        def handleResult(result):
            try:
                result = result.get()
            except BaseException as e:
                handle(gen.throw, *sys.exc_info())
            else:
                handle(gen.send, result)

        handle(gen.send, None)
        return promise.get_future()

    return wrapper
