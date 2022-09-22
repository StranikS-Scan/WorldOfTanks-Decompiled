# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ntpath.py
# Compiled at: 2003-04-20 02:11:33
"""Common pathname manipulations, WindowsNT/95 version.

Instead of importing this module directly, import os and refer to this
module as os.path.
"""
import os
import sys
import stat
import genericpath
import warnings
from genericpath import *
from genericpath import _unicode
__all__ = ['normcase',
 'isabs',
 'join',
 'splitdrive',
 'split',
 'splitext',
 'basename',
 'dirname',
 'commonprefix',
 'getsize',
 'getmtime',
 'getatime',
 'getctime',
 'islink',
 'exists',
 'lexists',
 'isdir',
 'isfile',
 'ismount',
 'walk',
 'expanduser',
 'expandvars',
 'normpath',
 'abspath',
 'splitunc',
 'curdir',
 'pardir',
 'sep',
 'pathsep',
 'defpath',
 'altsep',
 'extsep',
 'devnull',
 'realpath',
 'supports_unicode_filenames',
 'relpath']
curdir = '.'
pardir = '..'
extsep = '.'
sep = '\\'
pathsep = ';'
altsep = '/'
defpath = '.;C:\\bin'
if 'ce' in sys.builtin_module_names:
    defpath = '\\Windows'
elif 'os2' in sys.builtin_module_names:
    altsep = '/'
devnull = 'nul'

def normcase(s):
    """Normalize case of pathname.
    
    Makes all characters lowercase and all slashes into backslashes."""
    return s.replace('/', '\\').lower()


def isabs(s):
    """Test whether a path is absolute"""
    s = splitdrive(s)[1]
    return s != '' and s[:1] in '/\\'


def join(path, *paths):
    r"""Join two or more pathname components, inserting "\" as needed."""
    result_drive, result_path = splitdrive(path)
    for p in paths:
        p_drive, p_path = splitdrive(p)
        if p_path and p_path[0] in '\\/':
            if p_drive or not result_drive:
                result_drive = p_drive
            result_path = p_path
            continue
        elif p_drive and p_drive != result_drive:
            if p_drive.lower() != result_drive.lower():
                result_drive = p_drive
                result_path = p_path
                continue
            result_drive = p_drive
        if result_path and result_path[-1] not in '\\/':
            result_path = result_path + '\\'
        result_path = result_path + p_path

    return result_drive + sep + result_path if result_path and result_path[0] not in '\\/' and result_drive and result_drive[-1:] != ':' else result_drive + result_path


def splitdrive(p):
    """Split a pathname into drive/UNC sharepoint and relative path specifiers.
    Returns a 2-tuple (drive_or_unc, path); either part may be empty.
    
    If you assign
        result = splitdrive(p)
    It is always true that:
        result[0] + result[1] == p
    
    If the path contained a drive letter, drive_or_unc will contain everything
    up to and including the colon.  e.g. splitdrive("c:/dir") returns ("c:", "/dir")
    
    If the path contained a UNC path, the drive_or_unc will contain the host name
    and share up to but not including the fourth directory separator character.
    e.g. splitdrive("//host/computer/dir") returns ("//host/computer", "/dir")
    
    Paths cannot contain both a drive letter and a UNC path.
    
    """
    if len(p) > 1:
        normp = p.replace(altsep, sep)
        if normp[0:2] == sep * 2 and normp[2:3] != sep:
            index = normp.find(sep, 2)
            if index == -1:
                return ('', p)
            index2 = normp.find(sep, index + 1)
            if index2 == index + 1:
                return ('', p)
            if index2 == -1:
                index2 = len(p)
            return (p[:index2], p[index2:])
        if normp[1] == ':':
            return (p[:2], p[2:])
    return ('', p)


def splitunc(p):
    """Split a pathname into UNC mount point and relative path specifiers.
    
    Return a 2-tuple (unc, rest); either part may be empty.
    If unc is not empty, it has the form '//host/mount' (or similar
    using backslashes).  unc+rest is always the input path.
    Paths containing drive letters never have a UNC part.
    """
    if p[1:2] == ':':
        return ('', p)
    firstTwo = p[0:2]
    if firstTwo == '//' or firstTwo == '\\\\':
        normp = p.replace('\\', '/')
        index = normp.find('/', 2)
        if index <= 2:
            return ('', p)
        index2 = normp.find('/', index + 1)
        if index2 == index + 1:
            return ('', p)
        if index2 == -1:
            index2 = len(p)
        return (p[:index2], p[index2:])
    return ('', p)


def split(p):
    """Split a pathname.
    
    Return tuple (head, tail) where tail is everything after the final slash.
    Either part may be empty."""
    d, p = splitdrive(p)
    i = len(p)
    while i and p[i - 1] not in '/\\':
        i = i - 1

    head, tail = p[:i], p[i:]
    head2 = head
    while head2 and head2[-1] in '/\\':
        head2 = head2[:-1]

    head = head2 or head
    return (d + head, tail)


def splitext(p):
    return genericpath._splitext(p, sep, altsep, extsep)


splitext.__doc__ = genericpath._splitext.__doc__

def basename(p):
    """Returns the final component of a pathname"""
    return split(p)[1]


def dirname(p):
    """Returns the directory component of a pathname"""
    return split(p)[0]


def islink(path):
    """Test for symbolic link.
    On WindowsNT/95 and OS/2 always returns false
    """
    return False


lexists = exists

def ismount(path):
    """Test whether a path is a mount point (defined as root of drive)"""
    unc, rest = splitunc(path)
    if unc:
        return rest in ('', '/', '\\')
    p = splitdrive(path)[1]
    return len(p) == 1 and p[0] in '/\\'


def walk(top, func, arg):
    """Directory tree walk with callback function.
    
    For each directory in the directory tree rooted at top (including top
    itself, but excluding '.' and '..'), call func(arg, dirname, fnames).
    dirname is the name of the directory, and fnames a list of the names of
    the files and subdirectories in dirname (excluding '.' and '..').  func
    may modify the fnames list in-place (e.g. via del or slice assignment),
    and walk will only recurse into the subdirectories whose names remain in
    fnames; this can be used to implement a filter, or to impose a specific
    order of visiting.  No semantics are defined for, or required of, arg,
    beyond that arg is always passed to func.  It can be used, e.g., to pass
    a filename pattern, or a mutable object designed to accumulate
    statistics.  Passing None for arg is common."""
    warnings.warnpy3k('In 3.x, os.path.walk is removed in favor of os.walk.', stacklevel=2)
    try:
        names = os.listdir(top)
    except os.error:
        return

    func(arg, top, names)
    for name in names:
        name = join(top, name)
        if isdir(name):
            walk(name, func, arg)


def expanduser(path):
    """Expand ~ and ~user constructs.
    
    If user or $HOME is unknown, do nothing."""
    if path[:1] != '~':
        return path
    i, n = 1, len(path)
    while i < n and path[i] not in '/\\':
        i = i + 1

    if 'HOME' in os.environ:
        userhome = os.environ['HOME']
    elif 'USERPROFILE' in os.environ:
        userhome = os.environ['USERPROFILE']
    else:
        if 'HOMEPATH' not in os.environ:
            return path
        try:
            drive = os.environ['HOMEDRIVE']
        except KeyError:
            drive = ''

        userhome = join(drive, os.environ['HOMEPATH'])
    if i != 1:
        userhome = join(dirname(userhome), path[1:i])
    return userhome + path[i:]


def expandvars(path):
    """Expand shell variables of the forms $var, ${var} and %var%.
    
    Unknown variables are left unchanged."""
    if '$' not in path and '%' not in path:
        return path
    import string
    varchars = string.ascii_letters + string.digits + '_-'
    if isinstance(path, _unicode):
        encoding = sys.getfilesystemencoding()

        def getenv(var):
            return os.environ[var.encode(encoding)].decode(encoding)

    else:

        def getenv(var):
            return os.environ[var]

    res = ''
    index = 0
    pathlen = len(path)
    while index < pathlen:
        c = path[index]
        if c == "'":
            path = path[index + 1:]
            pathlen = len(path)
            try:
                index = path.index("'")
                res = res + "'" + path[:index + 1]
            except ValueError:
                res = res + c + path
                index = pathlen - 1

        elif c == '%':
            if path[index + 1:index + 2] == '%':
                res = res + c
                index = index + 1
            else:
                path = path[index + 1:]
                pathlen = len(path)
                try:
                    index = path.index('%')
                except ValueError:
                    res = res + '%' + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        res = res + getenv(var)
                    except KeyError:
                        res = res + '%' + var + '%'

        elif c == '$':
            if path[index + 1:index + 2] == '$':
                res = res + c
                index = index + 1
            elif path[index + 1:index + 2] == '{':
                path = path[index + 2:]
                pathlen = len(path)
                try:
                    index = path.index('}')
                    var = path[:index]
                    try:
                        res = res + getenv(var)
                    except KeyError:
                        res = res + '${' + var + '}'

                except ValueError:
                    res = res + '${' + path
                    index = pathlen - 1

            else:
                var = ''
                index = index + 1
                c = path[index:index + 1]
                while c != '' and c in varchars:
                    var = var + c
                    index = index + 1
                    c = path[index:index + 1]

                try:
                    res = res + getenv(var)
                except KeyError:
                    res = res + '$' + var

                if c != '':
                    index = index - 1
        else:
            res = res + c
        index = index + 1

    return res


def normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    backslash, dot = (u'\\', u'.') if isinstance(path, _unicode) else ('\\', '.')
    if path.startswith(('\\\\.\\', '\\\\?\\')):
        return path
    path = path.replace('/', '\\')
    prefix, path = splitdrive(path)
    if prefix == '':
        while path[:1] == '\\':
            prefix = prefix + backslash
            path = path[1:]

    elif path.startswith('\\'):
        prefix = prefix + backslash
        path = path.lstrip('\\')
    comps = path.split('\\')
    i = 0
    while i < len(comps):
        if comps[i] in ('.', ''):
            del comps[i]
        if comps[i] == '..':
            if i > 0 and comps[i - 1] != '..':
                del comps[i - 1:i + 1]
                i -= 1
            elif i == 0 and prefix.endswith('\\'):
                del comps[i]
            else:
                i += 1
        i += 1

    if not prefix and not comps:
        comps.append(dot)
    return prefix + backslash.join(comps)


try:
    from nt import _getfullpathname
except ImportError:

    def abspath(path):
        """Return the absolute version of a path."""
        if not isabs(path):
            if isinstance(path, _unicode):
                cwd = os.getcwdu()
            else:
                cwd = os.getcwd()
            path = join(cwd, path)
        return normpath(path)


else:

    def abspath(path):
        """Return the absolute version of a path."""
        if path:
            try:
                path = _getfullpathname(path)
            except WindowsError:
                pass

        elif isinstance(path, _unicode):
            path = os.getcwdu()
        else:
            path = os.getcwd()
        return normpath(path)


realpath = abspath
supports_unicode_filenames = hasattr(sys, 'getwindowsversion') and sys.getwindowsversion()[3] >= 2

def _abspath_split(path):
    abs = abspath(normpath(path))
    prefix, rest = splitunc(abs)
    is_unc = bool(prefix)
    if not is_unc:
        prefix, rest = splitdrive(abs)
    return (is_unc, prefix, [ x for x in rest.split(sep) if x ])


def relpath(path, start=curdir):
    """Return a relative version of a path"""
    if not path:
        raise ValueError('no path specified')
    start_is_unc, start_prefix, start_list = _abspath_split(start)
    path_is_unc, path_prefix, path_list = _abspath_split(path)
    if path_is_unc ^ start_is_unc:
        raise ValueError('Cannot mix UNC and non-UNC paths (%s and %s)' % (path, start))
    if path_prefix.lower() != start_prefix.lower():
        if path_is_unc:
            raise ValueError('path is on UNC root %s, start on UNC root %s' % (path_prefix, start_prefix))
        else:
            raise ValueError('path is on drive %s, start on drive %s' % (path_prefix, start_prefix))
    i = 0
    for e1, e2 in zip(start_list, path_list):
        if e1.lower() != e2.lower():
            break
        i += 1

    rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
    return curdir if not rel_list else join(*rel_list)


try:
    from nt import _isdir as isdir
except ImportError:
    pass
