# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/excepthook.py
import BigWorld
import sys
import linecache
from functools import partial
from traceback import format_exception_only
from constants import IS_BASEAPP
_MAX_OBJECT_SIZE = 16384
_MAX_DEPTH = 10
_SEQUENCE_TYPES = (list, set, tuple)
_LINE_LIMIT = 25
_ENABLE_EXTENDED_TRACEBACK = False

def getLocationFromCode(fileNameToTrim, code, lineno=None):
    filename = code.co_filename
    trim_to, trim_to_len = fileNameToTrim
    idx = filename.find(trim_to)
    if idx != -1:
        filename = filename[idx + trim_to_len:]
    if lineno is None:
        lineno = code.co_firstlineno
    name = code.co_name
    return (filename, lineno, name)


def formatLocation(filename, lineno, name):
    return 'File "%s", line %d, in %s' % (filename, lineno, name)


def extendedTracebackAsString(fileNameToTrim, wrapperName, orgName, etype, value, tb):
    return '\n'.join(extendedTracebackAsList(fileNameToTrim, wrapperName, orgName, etype, value, tb))


def extendedTracebackAsList(fileNameToTrim, wrapperName, orgName, exctype, value, traceback):
    global _ENABLE_EXTENDED_TRACEBACK
    if not _ENABLE_EXTENDED_TRACEBACK:
        return []
    else:
        try:
            lines = ['[TRACEBACK EXT]']
            localsProcessorCache = {}
            parent = traceback
            n = 0
            while parent and n < _LINE_LIMIT:
                fm = parent.tb_frame
                filename, lineno, name = getLocationFromCode(fileNameToTrim, fm.f_code, parent.tb_lineno)
                parent = parent.tb_next
                n += 1
                linecache.checkcache(filename)
                line = linecache.getline(filename, lineno, fm.f_globals)
                if wrapperName is not None:
                    if line.find(wrapperName) != -1:
                        continue
                lines.append('  %s' % formatLocation(filename, lineno, name))
                line = line.strip()
                if line:
                    lines.append('    ' + line)
                lines.append('    locals: {0}'.format(__processLocals(fm.f_locals, localsProcessorCache)))

            for line in format_exception_only(exctype, value):
                line = line.strip()
                if wrapperName is not None and orgName is not None:
                    line.replace(wrapperName, orgName)
                lines.append(line)

            lines.append('[/TRACEBACK EXT]')
        except:
            lines = []

        return lines


def __processVar(k, v, localsProcessorCache):
    varID = id(v)
    if varID in localsProcessorCache:
        return localsProcessorCache[varID]
    if k == 'self' or IS_BASEAPP and (isinstance(v, BigWorld.Base) or isinstance(v, BigWorld.Proxy)):
        res = {'className': v.__class__.__name__}
        for field, alias in (('id', 'id'), ('databaseID', 'dbID'), ('className', 'entityType')):
            if hasattr(v, field):
                res[alias] = getattr(v, field)

    else:
        meta = {'depth': 0,
         'size': 0,
         'cycleReferences': set()}
        isSizeOK = __checkObjectSize(v, meta)
        if not isSizeOK:
            res = '...skipped...'
        else:
            res = v
    localsProcessorCache[varID] = res
    return res


def __checkObjectSize(d, meta):
    try:
        meta['depth'] += 1
        if meta['depth'] >= _MAX_DEPTH:
            return False
        if id(d) in meta['cycleReferences']:
            return True
        meta['size'] += sys.getsizeof(d, 0)
        if meta['size'] >= _MAX_OBJECT_SIZE:
            return False
        meta['cycleReferences'].add(id(d))
        if isinstance(d, dict):
            for v in d.itervalues():
                if not __checkObjectSize(v, meta):
                    return False

        elif isinstance(d, _SEQUENCE_TYPES):
            for v in d:
                if not __checkObjectSize(v, meta):
                    return False

        return True
    finally:
        meta['depth'] -= 1


def __processLocals(locals, localsProcessorCache):
    return {k:__processVar(k, v, localsProcessorCache) for k, v in locals.iteritems()}


def __excepthook(originalExceptHook, fileNameToTrim, exctype, value, traceback):
    originalExceptHook(exctype, value, traceback)
    extMsg = extendedTracebackAsString(fileNameToTrim, None, None, exctype, value, traceback)
    BigWorld.logError('EXCEPTION', extMsg, None)
    return


def init(enableExtendedTraceBack, fileNameToTrim):
    global _ENABLE_EXTENDED_TRACEBACK
    _ENABLE_EXTENDED_TRACEBACK = enableExtendedTraceBack
    if _ENABLE_EXTENDED_TRACEBACK:
        sys.excepthook = partial(__excepthook, sys.excepthook, fileNameToTrim)
