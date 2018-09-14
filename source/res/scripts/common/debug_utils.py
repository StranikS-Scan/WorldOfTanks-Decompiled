# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/debug_utils.py
import sys
import BigWorld
import excepthook
import time
import traceback
from GarbageCollectionDebug import gcDump, getGarbageGraph
from functools import wraps
from collections import defaultdict
from warnings import warn_explicit
from traceback import format_exception
from constants import IS_CLIENT, IS_CELLAPP, IS_BASEAPP, CURRENT_REALM, IS_DEVELOPMENT
from constants import LEAKS_DETECTOR_MAX_EXECUTION_TIME
_src_file_trim_to = ('res/wot/scripts/', len('res/wot/scripts/'))
_g_logMapping = {}
GCDUMP_CROWBAR_SWITCH = False

class LOG_LEVEL:
    DEV = 1
    ST = 2
    CT = 3
    SVR_RELEASE = 4
    RELEASE = 5


if CURRENT_REALM == 'DEV':
    _logLevel = LOG_LEVEL.DEV
elif CURRENT_REALM == 'ST':
    _logLevel = LOG_LEVEL.ST
elif CURRENT_REALM == 'CT':
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
            return lambda *args: None


class CriticalError(BaseException):
    pass


def init():
    global _g_logMapping
    if not IS_CLIENT:

        def splitMessageIntoChunks(prefix, msg, func):
            if prefix not in ('EXCEPTION', 'CRITICAL'):
                msg = msg[:8960]
            blockSize = 1792
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
     'HACK': BigWorld.logHack}
    excepthook.init(not IS_CLIENT and _logLevel < LOG_LEVEL.SVR_RELEASE, _src_file_trim_to)


@_LogWrapper(LOG_LEVEL.RELEASE)
def CRITICAL_ERROR(msg, *kargs):
    msg = '{0}:{1}:{2}'.format(_makeMsgHeader(sys._getframe(1)), msg, kargs)
    BigWorld.logCritical('CRITICAL', msg, None)
    if IS_CLIENT:
        import BigWorld
        BigWorld.quit()
    elif IS_CELLAPP or IS_BASEAPP:
        import BigWorld
        BigWorld.shutDownApp()
        raise CriticalError(msg)
    else:
        sys.exit()
    return


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_CURRENT_EXCEPTION():
    msg = _makeMsgHeader(sys._getframe(1)) + '\n'
    etype, value, tb = sys.exc_info()
    msg += ''.join(format_exception(etype, value, tb, None))
    BigWorld.logError('EXCEPTION', msg, None)
    extMsg = excepthook.extendedTracebackAsString(_src_file_trim_to, None, None, etype, value, tb)
    if extMsg:
        BigWorld.logError('EXCEPTION', extMsg, None)
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


@_LogWrapper(LOG_LEVEL.DEV)
def LOG_ERROR_DEV(msg, *kargs, **kwargs):
    _doLog('ERROR', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_WARNING(msg, *kargs, **kwargs):
    _doLog('WARNING', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_NOTE(msg, *kargs, **kwargs):
    _doLog('NOTE', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.SVR_RELEASE)
def LOG_DEBUG(msg, *kargs, **kwargs):
    _doLog('DEBUG', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.DEV)
def LOG_DEBUG_DEV(msg, *kargs, **kwargs):
    _doLog('DEBUG', msg, kargs, kwargs)


@_LogWrapper(LOG_LEVEL.CT)
def LOG_GUI(msg, *kargs):
    _doLog('GUI', msg, kargs)


@_LogWrapper(LOG_LEVEL.SVR_RELEASE)
def LOG_VOIP(msg, *kargs):
    _doLog('VOIP', msg, kargs)


def FLUSH_LOG():
    import BigWorld
    BigWorld.flushPythonLog()


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_UNEXPECTED(msg, *kargs):
    _doLog('LOG_UNEXPECTED', msg, kargs)


@_LogWrapper(LOG_LEVEL.RELEASE)
def LOG_WRONG_CLIENT(entity, *kargs):
    if hasattr(entity, 'id'):
        entity = entity.id
    BigWorld.logError('WRONG_CLIENT', ' '.join(map(str, [_makeMsgHeader(sys._getframe(1)), entity, kargs])), None)
    return


def _doLog(category, msg, args=None, kwargs={}):
    header = _makeMsgHeader(sys._getframe(2))
    logFunc = _g_logMapping.get(category, None)
    if not logFunc:
        logFunc = BigWorld.logDebug
    if args:
        output = ' '.join(map(str, [header, msg, args]))
    else:
        output = ' '.join(map(str, [header, msg]))
    logFunc(category, output, None)
    if kwargs.get('stack', False):
        traceback.print_stack()
    return


def _makeMsgHeader(frame):
    filename = frame.f_code.co_filename
    trim_to, trim_to_len = _src_file_trim_to
    idx = filename.find(trim_to)
    if idx != -1:
        filename = filename[idx + trim_to_len:]
    return '(%s, %d):' % (filename, frame.f_lineno)


def _doLogFmt(prefix, fmt, *args):
    msg = _makeMsgHeader(sys._getframe(2))
    msg += fmt.format(*args) if args else fmt
    BigWorld.logInfo(prefix, msg, None)
    return


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


def disabled_if(flag, msg=''):
    if flag:

        def disable_func(func):
            LOG_DEBUG_DEV('Method ({}) disabled. {} ', func.__name__, msg)
            return disabled(func)

    else:

        def disable_func(func):
            return func

    return disable_func


def dump_garbage(source=False):
    """
    show us what's the garbage about
    """
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
        print '========================================='
        print '##DUMPSTART'
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
            print '%d %s' % (cnt, t)

    d.clear()
    del gc.garbage[:]
    del d
    if verbose:
        print '##DUMPEND'
        print '========================================='
    return


def memoryLeaksSafeDump(id, _):
    curTime = time.time()
    if not GCDUMP_CROWBAR_SWITCH:
        gcDump()
    if time.time() - curTime > LEAKS_DETECTOR_MAX_EXECUTION_TIME or GCDUMP_CROWBAR_SWITCH:
        BigWorld.delTimer(id)


def initMemoryLeaksLogging(repeatOffset=300):

    def detectMemoryLeaksTimerCallback(id, userArg):
        if userArg == 0:
            BigWorld.addTimer(memoryLeaksSafeDump, 1, repeatOffset, 1)

    BigWorld.addTimer(detectMemoryLeaksTimerCallback, 1, 0, 0)


def createMemoryLeakFunctionWatcher():
    """
    register function watcher as command
    command can be executed remotely and return structure created by objgraph
    based on result of garbage collection
    """
    for app_type, flag_name in (('cellapp', 'EXPOSE_CELL_APPS'), ('baseapp', 'EXPOSE_BASE_APPS'), ('serviceapp', 'EXPOSE_SERVICE_APPS')):
        try:
            if not hasattr(BigWorld, flag_name):
                continue
            flag = getattr(BigWorld, flag_name)
            BigWorld.addFunctionWatcher('command/garbageCollect%s' % app_type, getGarbageGraph, [], flag, 'Colect %s garbage data and return objgraph result as dot data' % app_type)
        except:
            LOG_CURRENT_EXCEPTION()


def verify(expression):
    try:
        assert expression
    except AssertionError:
        LOG_CURRENT_EXCEPTION()


def traceCalls(func):
    if not IS_DEVELOPMENT:
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        LOG_DEBUG_DEV('%s.%s' % (func.im_class.__name__, func.im_func.__name__), args, kwargs)
        returned = func(*args, **kwargs)
        if returned is not None:
            LOG_DEBUG_DEV('%s.%s returned:' % (func.im_class.__name__, func.im_func.__name__), returned)
        return returned

    return wrapper


def traceMethodCalls(obj, *names):
    if not IS_DEVELOPMENT:
        return
    for name in names:
        func = getattr(obj, name)
        setattr(obj, name, traceCalls(func))


init()
