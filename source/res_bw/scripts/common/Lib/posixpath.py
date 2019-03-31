# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/posixpath.py
# Compiled at: 2010-05-25 20:46:16
"""Common operations on Posix pathnames.

Instead of importing this module directly, import os and refer to
this module as os.path.  The "os.path" name is an alias for this
module on Posix systems; on other systems (e.g. Mac, Windows),
os.path provides the same operations in a manner specific to that
platform, and is an alias to another module (e.g. macpath, ntpath).

Some of this can actually be useful on non-Posix systems too, e.g.
for manipulation of the pathname component of URLs.
"""
import os
import stat
import genericpath
import warnings
from genericpath import *
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
 'samefile',
 'sameopenfile',
 'samestat',
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
sep = '/'
pathsep = ':'
defpath = ':/bin:/usr/bin'
altsep = None
devnull = '/dev/null'

def normcase(s):
    """Normalize case of pathname.  Has no effect under Posix"""
    return s


def isabs(s):
    """Test whether a path is absolute"""
    return s.startswith('/')


def join(a, *p):
    """Join two or more pathname components, inserting '/' as needed.
    If any component is an absolute path, all previous path components
    will be discarded."""
    path = a
    for b in p:
        if b.startswith('/'):
            path = b
        elif path == '' or path.endswith('/'):
            path += b
        else:
            path += '/' + b

    return path


def split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty."""
    i = p.rfind('/') + 1
    head, tail = p[:i], p[i:]
    if head and head != '/' * len(head):
        head = head.rstrip('/')
    return (head, tail)


def splitext(p):
    return genericpath._splitext(p, sep, altsep, extsep)


splitext.__doc__ = genericpath._splitext.__doc__

def splitdrive(p):
    """Split a pathname into drive and path. On Posix, drive is always
    empty."""
    return ('', p)


def basename(p):
    """Returns the final component of a pathname"""
    i = p.rfind('/') + 1
    return p[i:]


def dirname(p):
    """Returns the directory component of a pathname"""
    i = p.rfind('/') + 1
    head = p[:i]
    if head and head != '/' * len(head):
        head = head.rstrip('/')
    return head


def islink(path):
    """Test whether a path is a symbolic link"""
    try:
        st = os.lstat(path)
    except (os.error, AttributeError):
        return False

    return stat.S_ISLNK(st.st_mode)


def lexists(path):
    """Test whether a path exists.  Returns True for broken symbolic links"""
    try:
        st = os.lstat(path)
    except os.error:
        return False

    return True


def samefile(f1, f2):
    """Test whether two pathnames reference the same actual file"""
    s1 = os.stat(f1)
    s2 = os.stat(f2)
    return samestat(s1, s2)


def sameopenfile(fp1, fp2):
    """Test whether two open file objects reference the same file"""
    s1 = os.fstat(fp1)
    s2 = os.fstat(fp2)
    return samestat(s1, s2)


def samestat(s1, s2):
    """Test whether two stat buffers reference the same file"""
    return s1.st_ino == s2.st_ino and s1.st_dev == s2.st_dev


def ismount(path):
    """Test whether a path is a mount point"""
    try:
        s1 = os.lstat(path)
        s2 = os.lstat(join(path, '..'))
    except os.error:
        return False

    dev1 = s1.st_dev
    dev2 = s2.st_dev
    if dev1 != dev2:
        return True
    ino1 = s1.st_ino
    ino2 = s2.st_ino
    if ino1 == ino2:
        return True
    return False


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
        try:
            st = os.lstat(name)
        except os.error:
            continue

        if stat.S_ISDIR(st.st_mode):
            walk(name, func, arg)


def expanduser(path):
    """Expand ~ and ~user constructions.  If user or $HOME is unknown,
    do nothing."""
    if not path.startswith('~'):
        return path
    i = path.find('/', 1)
    if i < 0:
        i = len(path)
    if i == 1:
        if 'HOME' not in os.environ:
            import pwd
            userhome = pwd.getpwuid(os.getuid()).pw_dir
        else:
            userhome = os.environ['HOME']
    else:
        import pwd
        try:
            pwent = pwd.getpwnam(path[1:i])
        except KeyError:
            return path

        userhome = pwent.pw_dir
    userhome = userhome.rstrip('/') or userhome
    return userhome + path[i:]


_varprog = None

def expandvars(path):
    """Expand shell variables of form $var and ${var}.  Unknown variables
    are left unchanged."""
    global _varprog
    if '$' not in path:
        return path
    if not _varprog:
        import re
        _varprog = re.compile('\\$(\\w+|\\{[^}]*\\})')
    i = 0
    while 1:
        if True:
            m = _varprog.search(path, i)
            if not m:
                break
            i, j = m.span(0)
            name = m.group(1)
            if name.startswith('{') and name.endswith('}'):
                name = name[1:-1]
            tail = name in os.environ and path[j:]
            path = path[:i] + os.environ[name]
            i = len(path)
            path += tail
        else:
            i = j

    return path


def normpath--- This code section failed: ---

 310       0	LOAD_FAST         'path'
           3	LOAD_CONST        ''
           6	COMPARE_OP        '=='
           9	JUMP_IF_FALSE     '16'

 311      12	LOAD_CONST        '.'
          15	RETURN_END_IF     ''

 312      16	LOAD_FAST         'path'
          19	LOAD_ATTR         'startswith'
          22	LOAD_CONST        '/'
          25	CALL_FUNCTION_1   ''
          28	STORE_FAST        'initial_slashes'

 315      31	LOAD_FAST         'initial_slashes'
          34	JUMP_IF_FALSE     '77'

 316      37	LOAD_FAST         'path'
          40	LOAD_ATTR         'startswith'
          43	LOAD_CONST        '//'
          46	CALL_FUNCTION_1   ''
          49	JUMP_IF_FALSE     '77'
          52	LOAD_FAST         'path'
          55	LOAD_ATTR         'startswith'
          58	LOAD_CONST        '///'
          61	CALL_FUNCTION_1   ''
          64	UNARY_NOT         ''
        65_0	COME_FROM         '34'
        65_1	COME_FROM         '49'
          65	JUMP_IF_FALSE     '77'

 317      68	LOAD_CONST        2
          71	STORE_FAST        'initial_slashes'
          74	JUMP_FORWARD      '77'
        77_0	COME_FROM         '74'

 318      77	LOAD_FAST         'path'
          80	LOAD_ATTR         'split'
          83	LOAD_CONST        '/'
          86	CALL_FUNCTION_1   ''
          89	STORE_FAST        'comps'

 319      92	BUILD_LIST_0      ''
          95	STORE_FAST        'new_comps'

 320      98	SETUP_LOOP        '216'
         101	LOAD_FAST         'comps'
         104	GET_ITER          ''
         105	FOR_ITER          '215'
         108	STORE_FAST        'comp'

 321     111	LOAD_FAST         'comp'
         114	LOAD_CONST        ('', '.')
         117	COMPARE_OP        'in'
         120	JUMP_IF_FALSE     '129'

 322     123	CONTINUE          '105'
         126	JUMP_FORWARD      '129'
       129_0	COME_FROM         '126'

 323     129	LOAD_FAST         'comp'
         132	LOAD_CONST        '..'
         135	COMPARE_OP        '!='
         138	JUMP_IF_TRUE      '177'
         141	LOAD_FAST         'initial_slashes'
         144	UNARY_NOT         ''
         145	JUMP_IF_FALSE     '155'
         148	LOAD_FAST         'new_comps'
         151	UNARY_NOT         ''
       152_0	COME_FROM         '145'
         152	JUMP_IF_TRUE      '177'

 324     155	LOAD_FAST         'new_comps'
         158	JUMP_IF_FALSE     '193'
         161	LOAD_FAST         'new_comps'
         164	LOAD_CONST        -1
         167	BINARY_SUBSCR     ''
         168	LOAD_CONST        '..'
         171	COMPARE_OP        '=='
       174_0	COME_FROM         '138'
       174_1	COME_FROM         '152'
       174_2	COME_FROM         '158'
         174	JUMP_IF_FALSE     '193'

 325     177	LOAD_FAST         'new_comps'
         180	LOAD_ATTR         'append'
         183	LOAD_FAST         'comp'
         186	CALL_FUNCTION_1   ''
         189	POP_TOP           ''
         190	JUMP_BACK         '105'

 326     193	LOAD_FAST         'new_comps'
         196	JUMP_IF_FALSE     '212'

 327     199	LOAD_FAST         'new_comps'
         202	LOAD_ATTR         'pop'
         205	CALL_FUNCTION_0   ''
         208	POP_TOP           ''
         209	JUMP_BACK         '105'
         212	JUMP_BACK         '105'
         215	POP_BLOCK         ''
       216_0	COME_FROM         '98'

 328     216	LOAD_FAST         'new_comps'
         219	STORE_FAST        'comps'

 329     222	LOAD_CONST        '/'
         225	LOAD_ATTR         'join'
         228	LOAD_FAST         'comps'
         231	CALL_FUNCTION_1   ''
         234	STORE_FAST        'path'

 330     237	LOAD_FAST         'initial_slashes'
         240	JUMP_IF_FALSE     '260'

 331     243	LOAD_CONST        '/'
         246	LOAD_FAST         'initial_slashes'
         249	BINARY_MULTIPLY   ''
         250	LOAD_FAST         'path'
         253	BINARY_ADD        ''
         254	STORE_FAST        'path'
         257	JUMP_FORWARD      '260'
       260_0	COME_FROM         '257'

 332     260	LOAD_FAST         'path'
         263	JUMP_IF_TRUE      '269'

Syntax error at or near 'LOAD_FAST' token at offset 260


def abspath(path):
    """Return an absolute path."""
    if not isabs(path):
        path = join(os.getcwd(), path)
    return normpath(path)


def realpath(filename):
    """Return the canonical path of the specified filename, eliminating any
    symbolic links encountered in the path."""
    if isabs(filename):
        bits = ['/'] + filename.split('/')[1:]
    else:
        bits = [''] + filename.split('/')
    for i in range(2, len(bits) + 1):
        component = join(*bits[0:i])
        if islink(component):
            resolved = _resolve_link(component)
            if resolved is None:
                return abspath(join(*([component] + bits[i:])))
            else:
                newpath = join(*([resolved] + bits[i:]))
                return realpath(newpath)

    return abspath(filename)


def _resolve_link(path):
    """Internal helper function.  Takes a path and follows symlinks
    until we either arrive at something that isn't a symlink, or
    encounter a path we've seen before (meaning that there's a loop).
    """
    paths_seen = []
    while 1:
        if islink(path):
            if path in paths_seen:
                return None
            paths_seen.append(path)
            resolved = os.readlink(path)
            dir = isabs(resolved) or dirname(path)
            path = normpath(join(dir, resolved))
        else:
            path = normpath(resolved)

    return path


supports_unicode_filenames = False

def relpath(path, start=curdir):
    """Return a relative version of a path"""
    if not path:
        raise ValueError('no path specified')
    start_list = abspath(start).split(sep)
    path_list = abspath(path).split(sep)
    i = len(commonprefix([start_list, path_list]))
    rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)