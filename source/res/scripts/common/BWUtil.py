# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BWUtil.py
from __future__ import absolute_import
import io
import os
import platform
import sys
from functools import partial
import BigWorld
import ResMgr
from bwdebug import TRACE_MSG
try:
    import builtins
except ImportError:
    import __builtin__ as builtins

try:
    _unicode = unicode
    _basestring = basestring
except NameError:
    _unicode = str
    _basestring = str

_PY2 = sys.version_info.major < 3

class _BuiltinsAccessor(object):

    def __init__(self, field_name):
        self._field_name = field_name
        self._original = None
        return

    @property
    def original(self):
        return self._original or self._get()

    def set(self, value):
        self._original = self._get()
        self._set(value)

    def get(self):
        return self._get()

    def _set(self, value):
        raise NotImplementedError

    def _get(self):
        raise NotImplementedError

    def revert(self):
        if self._original:
            self.set(self._original)
            self._original = None
        return


class _ItemAccessor(_BuiltinsAccessor):

    def _set(self, value):
        builtins[self._field_name] = value

    def _get(self):
        return builtins[self._field_name]


class _AttrAccessor(_BuiltinsAccessor):

    def _set(self, value):
        setattr(builtins, self._field_name, value)

    def _get(self):
        return getattr(builtins, self._field_name)


try:
    _ = builtins['open']
    _open_accessor = _ItemAccessor('open')
except TypeError:
    _open_accessor = _AttrAccessor('open')

class _BwFile(object):

    def __init__(self, path):
        self._content = ResMgr.openSection(path).asBinary.split('\n')

    def __enter__(self):
        return self._content

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return iter(self._content)


def bwResReplaceOpen(name, *args, **kwargs):
    return _BwFile(name)


def bwResRelativePatch(function, name, *args, **kwargs):
    try:
        absname = ResMgr.resolveToAbsolutePath(name)
    except Exception as e:
        raise IOError(2, 'Error = {}; name = {}'.format(str(e), name))

    absname = _unicode(absname)
    return function(absname, *args, **kwargs)


@partial
def bwResRelativeOpen(name, *args, **kwargs):
    if _PY2:
        kwargs.pop('encoding', None)
    return bwResRelativePatch(_open_accessor.original, name, *args, **kwargs)


@partial
def bwResRelativeIOOpen(name, *args, **kwargs):
    return bwResRelativePatch(io.open, name, *args, **kwargs)


def monkeyPatchOpen(full_replace=False):
    TRACE_MSG('BWUtil.monkeyPatchOpen: Patching open()', full_replace)
    if full_replace:
        new_open = bwResReplaceOpen
    else:
        new_open = bwResRelativeOpen
    _open_accessor.set(new_open)


def monkeyPatchFutureOpen():
    TRACE_MSG('BWUtil.monkeyPatchFutureOpen: Patching future open()')
    try:
        from future import builtins as future_builtins
        future_builtins.open = bwResRelativeIOOpen
    except ImportError:
        TRACE_MSG('BWUtil.monkeyPatchFutureOpen: Patching aborted since no future library')


def revertPatchedOpen():
    TRACE_MSG('BWUtil.revertPatchedOpen: Reverting open()')
    _open_accessor.revert()


def extendPath(path, name):
    from pkgutil import extend_path
    path = extend_path(path, name)
    if not isinstance(path, list):
        return path
    pname = os.path.join(*name.split('.'))
    init_py = '__init__' + os.extsep + 'py'
    path = path[:]
    for dir in sys.path:
        if not isinstance(dir, _basestring) or not ResMgr.isDir(dir):
            continue
        subdir = os.path.join(dir, pname)
        initfile = os.path.join(subdir, init_py)
        if subdir not in path and ResMgr.isFile(initfile):
            path.append(subdir)

    return path


def longDistroNameToShort(longDistroName):
    if longDistroName.startswith('Red Hat'):
        return 'rhel'
    return 'CentOS' if longDistroName.startswith('CentOS') else longDistroName


SHORT_NAME_ENTERPRISE_LINUX = 'el'
ENTERPRISE_LINUX_DISTROS = ['centos', 'rhel']
ALLOWED_DISTROS = ENTERPRISE_LINUX_DISTROS + ['fedora']

def finaliseShortNameFromReleaseInfo(longDistroName, versionStr, releaseName):
    majorVerStr = versionStr
    if '.' in versionStr:
        majorVerStr = versionStr[0:versionStr.index('.')]
    versionNum = int(majorVerStr)
    shortDistroName = longDistroNameToShort(longDistroName).lower()
    if shortDistroName not in ALLOWED_DISTROS:
        sys.stderr.write("Distribution '%s' is not supported\n" % shortDistroName)
        return None
    else:
        if shortDistroName in ENTERPRISE_LINUX_DISTROS:
            shortDistroName = SHORT_NAME_ENTERPRISE_LINUX
        return '%s%d' % (shortDistroName, versionNum)


def findPlatformName():
    if platform.system() == 'Windows':
        return 'win64'
    else:
        try:
            platformData = platform.linux_distribution()
        except AttributeError:
            sys.stderr.write('Unable to detect linux distribution. An old version of Python may be present. BigWorld requires Python 2.7.\n')
            return None

        return finaliseShortNameFromReleaseInfo(*platformData)


def getPlatformArchitecutre():
    try:
        return platform.processor()
    except:
        sys.stderr.write('Unable to detect platform architecture')
        return None

    return None


def getPlatformSuffix():
    platformName = findPlatformName()
    if not platformName:
        return None
    else:
        platformArchitecture = getPlatformArchitecutre()
        if not platformArchitecture:
            return None
        platformSuffix = platformName
        if platformName == 'el9':
            platformSuffix += '/' + platformArchitecture
        return platformSuffix


class AsyncReturn(StopIteration):
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


def if_only_component(*components):

    def _real_decorator(func):

        def _wrapper(*args, **kwargs):
            if BigWorld.component in components:
                func(*args, **kwargs)

        return _wrapper

    return _real_decorator


def if_only_not_component(*components):

    def _real_decorator(func):

        def _wrapper(*args, **kwargs):
            if BigWorld.component not in components:
                func(*args, **kwargs)

        return _wrapper

    return _real_decorator
