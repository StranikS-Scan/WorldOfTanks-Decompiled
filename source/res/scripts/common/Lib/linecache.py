# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/linecache.py
import sys
import os
__all__ = ['getline', 'clearcache', 'checkcache']

def getline(filename, lineno, module_globals=None):
    lines = getlines(filename, module_globals)
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1]
    else:
        return ''


cache = {}

def clearcache():
    global cache
    cache = {}


def getlines(filename, module_globals=None):
    if filename in cache:
        return cache[filename][2]
    try:
        return updatecache(filename, module_globals)
    except MemoryError:
        clearcache()
        return []


def checkcache(filename=None):
    if filename is None:
        filenames = cache.keys()
    elif filename in cache:
        filenames = [filename]
    else:
        return
    for filename in filenames:
        size, mtime, lines, fullname = cache[filename]
        if mtime is None:
            continue
        try:
            stat = os.stat(fullname)
        except os.error:
            del cache[filename]
            continue

        if size != stat.st_size or mtime != stat.st_mtime:
            del cache[filename]

    return


def updatecache(filename, module_globals=None):
    if filename in cache:
        del cache[filename]
    if not filename or filename.startswith('<') and filename.endswith('>'):
        return []
    else:
        fullname = filename
        try:
            stat = os.stat(fullname)
        except OSError:
            basename = filename
            if module_globals and '__loader__' in module_globals:
                name = module_globals.get('__name__')
                loader = module_globals['__loader__']
                get_source = getattr(loader, 'get_source', None)
                if name and get_source:
                    try:
                        data = get_source(name)
                    except (ImportError, IOError):
                        pass
                    else:
                        if data is None:
                            return []
                        cache[filename] = (len(data),
                         None,
                         [ line + '\n' for line in data.splitlines() ],
                         fullname)
                        return cache[filename][2]

            if os.path.isabs(filename):
                return []
            for dirname in sys.path:
                try:
                    fullname = os.path.join(dirname, basename)
                except (TypeError, AttributeError):
                    continue

                try:
                    stat = os.stat(fullname)
                    break
                except os.error:
                    pass

            else:
                return []

        try:
            with open(fullname, 'rU') as fp:
                lines = fp.readlines()
        except IOError:
            return []

        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
        size, mtime = stat.st_size, stat.st_mtime
        cache[filename] = (size,
         mtime,
         lines,
         fullname)
        return lines
