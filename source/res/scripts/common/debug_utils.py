# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/debug_utils.py
import sys
import re
import subprocess
import BigWorld
import excepthook
import time
import traceback
from GarbageCollectionDebug import gcDump, getGarbageGraph
from functools import wraps
from collections import defaultdict
from warnings import warn_explicit
from traceback import format_exception
from constants import IS_CLIENT, IS_CELLAPP, IS_BASEAPP, CURRENT_REALM, IS_DEVELOPMENT, IS_BOT
from constants import LEAKS_DETECTOR_MAX_EXECUTION_TIME
from contextlib import contextmanager
from threading import RLock
from soft_exception import SoftException
_src_file_trim_to = re.compile('res/(?:wot|wot_ext)/(?:.*/)?scripts/')
_g_logMapping = {}
_g_logLock = RLock()
GCDUMP_CROWBAR_SWITCH = False

class LOG_LEVEL:
    DEV = 1
    ST = 2
    CT = 3
    SVR_RELEASE = 4
    RELEASE = 5


class LOG_TAGS:
    BOOTCAMP = '[BOOTCAMP]'
    STATISTIC = '[STATISTIC]'


if CURRENT_REALM == 'DEV':
    _logLevel = LOG_LEVEL.DEV
elif CURRENT_REALM == 'ST':
    _logLevel = LOG_LEVEL.ST
elif CURRENT_REALM in ('CT', 'SB'):
    _logLevel = LOG_LEVEL.CT
elif IS_CLIENT:
    _logLevel = LOG_LEVEL.RELEASE
else:
    _logLevel = LOG_LEVEL.SVR_RELEASE

class _LogWrapper(object):

    def __init__(self, logLevel):
        self.__lvl = logLevel

    def __call__(self, func):
        if self.__lvl >= _logLevel:
            return func
        else:
            return lambda *args, **kwargs: None


class CriticalError(BaseException):
    pass


@contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


def init():
    global _g_logMapping
    if not (IS_CLIENT or IS_BOT):

        def splitMessageIntoChunks(prefix, msg, func):
            if prefix not in ('EXCEPTION', 'CRITICAL'):
                msg = msg[:8960]
            blockSize = 1792
            with _g_logLock:
                for m in msg.splitlines(False)[:100]:
                    idx = 0
                    while idx < len(m):
                        func(prefix, m[idx:idx + blockSize], None)
                        idx += blockSize

            return

        bwLogTrace = BigWorld.logTrace
        BigWorld.logTrace = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogTrace)
        bwLogDebug = BigWorld.logDebug
        BigWorld.logDebug = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogDebug)
        bwLogInfo = BigWorld.logInfo
        BigWorld.logInfo = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogInfo)
        bwLogNotice = BigWorld.logNotice
        BigWorld.logNotice = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogNotice)
        bwLogWarning = BigWorld.logWarning
        BigWorld.logWarning = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogWarning)
        bwLogError = BigWorld.logError
        BigWorld.logError = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogError)
        bwLogCritical = BigWorld.logCritical
        BigWorld.logCritical = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogCritical)
        bwLogHack = BigWorld.logHack
        BigWorld.logHack = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogHack)
    _g_logMapping = {'TRACE': BigWorld.logTrace,
     'DEBUG': BigWorld.logDebug,
     'INFO': BigWorld.logInfo,
     'NOTE': BigWorld.logNotice,
     'NOTICE': BigWorld.logNotice,
     'WARNING': BigWorld.logWarning,
     'ERROR': BigWorld.logError,
     'CRITICAL': BigWorld.logCritical,
     'HACK': BigWorld.logHack,
     'OBSOLETE': BigWorld.logWarning}
    excepthook.init(not IS_CLIENT and _logLevel < LOG_LEVEL.SVR_RELEASE, _src_file_trim_to)


@_LogWrapper(LOG_LEVEL.RELEASE)
def CRITICAL_ERROR(msg, *kargs):
    msg = '{0}:{1}:{2}'.format(_makeMsgHeader(sys._getframe(1)), msg, kargs)
    BigWorld.logCritical('CRITICAL', msg, None)
    if IS_CLIENT:
        BigWorld.quit()
    elif IS_CELLAPP or IS_BASEAPP:
        BigWorld.shutDownApp()
        raise CriticalError(msg)
    else:
        sys.exit()
    return


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_CURRENT_EXCEPTION(tags=None, frame=1):
    msg = _makeMsgHeader(sys._getframe(frame)) + '\n'
    etype, value, tb = sys.exc_info()
    msg += ''.join(format_exception(etype, value, tb, None))
    with _g_logLock:
        BigWorld.logError('EXCEPTION', _addTagsToMsg(tags, msg), None)
        extMsg = excepthook.extendedTracebackAsString(_src_file_trim_to, None, None, etype, value, tb)
        if extMsg:
            BigWorld.logError('EXCEPTION', _addTagsToMsg(tags, extMsg), None)
    return


LOG_EXPECTED_EXCEPTION = LOG_CURRENT_EXCEPTION

@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_WRAPPED_CURRENT_EXCEPTION(wrapperName, orgName, orgSource, orgLineno):
    sys.stderr.write('[%s] (%s, %d):' % ('EXCEPTION', orgSource, orgLineno))
    from sys import exc_info
    from traceback import format_tb, format_exception_only
    etype, value, tb = exc_info()
    if tb:
        list = ['Traceback (most recent call last):\n']
        list = list + format_tb(tb)
    else:
        list = []
    list = list
    for ln in list:
        if ln.find(wrapperName) == -1:
            sys.stderr.write(ln)

    list = format_exception_only(etype, value)
    for ln in list:
        sys.stderr.write(ln.replace(wrapperName, orgName))

    extMsg = excepthook.extendedTracebackAsString(_src_file_trim_to, wrapperName, orgName, etype, value, tb)
    if extMsg:
        BigWorld.logError('EXCEPTION', extMsg, None)
    return


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_CODEPOINT_WARNING(*kargs):
    _doLog('WARNING', 'this code point should have never been reached', kargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_ERROR(msg, *kargs, **kwargs):
    _doLog('ERROR', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_SENTRY(msg, *kargs):
    try:
        raise SoftException('{} {}'.format(msg, kargs))
    except:
        LOG_CURRENT_EXCEPTION(frame=2)


@_LogWrapper(LOG_LEVEL.DEV)
def LOG_ERROR_DEV(msg, *kargs, **kwargs):
    _doLog('ERROR', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.DEV)
def LOG_ACHTUNG(msg, *kargs, **kwargs):
    _doLog('ACHTUNG', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_WARNING(msg, *kargs, **kwargs):
    _doLog('WARNING', msg, kargs, kwargs)


def LOG_OBSOLETE(msg, *kargs):
    _doLog('OBSOLETE', msg, kargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_NOTE(msg, *kargs, **kwargs):
    _doLog('NOTE', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.SVR_RELEASE)
def LOG_DEBUG(msg, *kargs, **kwargs):
    _doLog('DEBUG', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.DEV)
def LOG_DEBUG_DEV(msg, *kargs, **kwargs):
    _doLog('DEBUG', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.DEV)
def LOG_DEBUG_DEV_NICE(msg, *kargs, **kwargs):
    kwargs['nice'] = True
    _doLog('DEBUG', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_UNEXPECTED(msg, *kargs):
    _doLog('LOG_UNEXPECTED', msg, kargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_WRONG_CLIENT(entity, *kargs):
    if hasattr(entity, 'id'):
        entity = entity.id
    BigWorld.logError('WRONG_CLIENT', ' '.join(map(str, [_makeMsgHeader(sys._getframe(1)), entity, kargs])), None)
    return


def _doLog(category, msg, args=None, kwargs={}, frameDepth=2):
    header = _makeMsgHeader(sys._getframe(frameDepth))
    logFunc = _g_logMapping.get(category, None)
    if not logFunc:
        logFunc = BigWorld.logDebug
    if args:
        if kwargs.get('nice'):
            parts = [header, u' ', msg]
            parts.extend(args)
            output = u''.join(map(unicode, parts))
        else:
            output = u' '.join(map(unicode, [header, msg, args]))
    else:
        output = u' '.join(map(unicode, [header, msg]))
    tags = kwargs.pop('tags', None)
    logFunc(category, _addTagsToMsg(tags, output), None)
    if kwargs.get('stack', False):
        traceback.print_stack(file=sys.stdout)
    return


def _makeMsgHeader(frame):
    filename = frame.f_code.co_filename
    trim_match = _src_file_trim_to.findall(filename)
    if trim_match:
        trim_path = trim_match[0]
        idx = filename.find(trim_path)
        filename = filename[idx + len(trim_path):]
    return '(%s, %d):' % (filename, frame.f_lineno)


def _doLogFmt(prefix, fmt, *args):
    msg = _makeMsgHeader(sys._getframe(2))
    msg += fmt.format(*args) if args else fmt
    BigWorld.logInfo(prefix, msg, None)
    return


def _addTagsToMsg(tags, msg):
    return u'{0} {1}'.format(u' '.join(tags), msg) if tags else msg


def makeFuncLocationString(func):
    return excepthook.formatLocation(*excepthook.getLocationFromCode(_src_file_trim_to, func.func_code))


def trace(func):
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    frame = sys._getframe(1)

    @wraps(func)
    def wrapper(*args, **kwds):
        BigWorld.logDebug(' '.join('(%s, %d) call %s:' % (frame.f_code.co_filename, frame.f_lineno, fname), ':', ', '.join(('%s=%r' % entry for entry in zip(argnames, args) + kwds.items()))))
        ret = func(*args, **kwds)
        BigWorld.logDebug(' '.join('(%s, %d) return from %s:' % (frame.f_code.co_filename, frame.f_lineno, fname), ':', repr(ret)))
        return ret

    return wrapper


def deprecated(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        warn_explicit('Call to deprecated function %(funcname)s.' % {'funcname': func.__name__}, category=DeprecationWarning, filename=func.func_code.co_filename, lineno=func.func_code.co_firstlineno + 1)
        return func(*args, **kwargs)

    return wrapper


def disabled(func):

    def empty_func(*args, **kargs):
        pass

    return empty_func


def disabled_if(checker, msg=''):

    def disable_func(func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            return disabled(func) if checker() else func(*args, **kwargs)

        return wrapped

    return disable_func


def dump_garbage(source=False):
    import inspect
    import gc
    print '\nCollecting GARBAGE:'
    gc.collect()
    print '\nCollecting GARBAGE:'
    gc.collect()
    print '\nGARBAGE OBJECTS:'
    for x in gc.garbage:
        try:
            s = str(x)
            if len(s) > 80:
                s = '%s...' % s[:80]
            print '::', s
            print '        type:', type(x)
            print '   referrers:', len(gc.get_referrers(x))
            print '    is class:', inspect.isclass(type(x))
            print '      module:', inspect.getmodule(x)
            if source:
                lines, line_num = inspect.getsourcelines(type(x))
                print '    line num:', line_num
                for l in lines:
                    print '        line:', l.rstrip('\n')

        except:
            pass


def dump_garbage_2(verbose=True, generation=2):
    import gc
    from weakref import ProxyType, ReferenceType
    gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)
    if generation is None:
        gc.collect()
    elif generation in xrange(0, 3):
        gc.collect(generation)
    else:
        LOG_ERROR('Value of generation is invalid. Generation may be an integer specifying which generation to collect (from 0 to 2)')
        return
    if verbose:
        BigWorld.logInfo('', '=========================================', None)
        BigWorld.logInfo('', '##DUMPSTART', None)
    del gc.garbage[:]
    d = defaultdict(lambda : 0)
    for i in gc.get_objects():
        if not isinstance(i, ProxyType) and not isinstance(i, ReferenceType):
            if hasattr(i, '__class__'):
                t = i.__class__
            else:
                t = type(i)
            d[t] += 1

    if verbose:
        for t, cnt in d.iteritems():
            msg = '%d %s' % (cnt, t)
            if isinstance(msg, unicode):
                msg = msg.encode()
            BigWorld.logInfo('', msg, None)

    d.clear()
    del gc.garbage[:]
    del d
    if verbose:
        BigWorld.logInfo('', '##DUMPEND', None)
        BigWorld.logInfo('', '=========================================', None)
    return


def memoryLeaksSafeDump(id, _):
    curTime = time.time()
    if not GCDUMP_CROWBAR_SWITCH:
        gcDump()
    if time.time() - curTime > LEAKS_DETECTOR_MAX_EXECUTION_TIME or GCDUMP_CROWBAR_SWITCH:
        BigWorld.delTimer(id)


def printConnections(ports):
    portsRE = '\\|'.join(map(lambda p: str(p), ports))
    ns = subprocess.Popen(['netstat', '-atupn'], stdout=subprocess.PIPE)
    gr = subprocess.Popen(['grep', portsRE], stdin=ns.stdout, stdout=subprocess.PIPE)
    output = gr.communicate()[0].splitlines()
    for line in output:
        LOG_DEBUG('Connection: ', line)


def printProcesses():
    ps = subprocess.Popen(['ps',
     '-eo',
     'pid,etimes,args',
     '--sort',
     'start_time'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    procs = ps.communicate()[0].splitlines()
    procsCnt = 0
    for proc in procs:
        if 'app' in proc and 'bigworld' in proc:
            LOG_DEBUG('Process: ', proc)
            procsCnt += 1

    LOG_DEBUG('Total processes: ', procsCnt)


def initMemoryLeaksLogging(repeatOffset=300):

    def detectMemoryLeaksTimerCallback(id, userArg):
        if userArg == 0:
            BigWorld.addTimer(memoryLeaksSafeDump, 1, repeatOffset, 1)

    BigWorld.addTimer(detectMemoryLeaksTimerCallback, 1, 0, 0)


def verify(expression):
    try:
        pass
    except AssertionError:
        LOG_CURRENT_EXCEPTION()


def traceCalls(func):
    if not IS_DEVELOPMENT:
        return func
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    frame = sys._getframe(1)

    @wraps(func)
    def wrapper(*args, **kwds):
        entID = ' [id=%s]' % str(args[0].id) if len(args) > 0 and hasattr(args[0], 'id') else ''
        BigWorld.logDebug('traceCalls', '(%s, %d)%s call %s(%s)' % (frame.f_code.co_filename,
         frame.f_lineno,
         entID,
         fname,
         ', '.join(('%s=%r' % entry for entry in zip(argnames, args) + kwds.items()))), None)
        ret = func(*args, **kwds)
        BigWorld.logDebug('traceCalls', '%s returned %s' % (fname, repr(ret)), None)
        return ret

    return wrapper


def wg_extract_stack(f=None, limit=None):
    if f is None:
        f = sys._getframe().f_back
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list = []
    n = 0
    while f is not None and (limit is None or n < limit):
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        list.append((filename, lineno, name))
        f = f.f_back
        n = n + 1

    list.reverse()
    return list


def traceMethodCalls(obj, *names):
    if not IS_DEVELOPMENT:
        return
    for name in names:
        func = getattr(obj, name)
        setattr(obj, name, traceCalls(func))


init()
