# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/debug_utils.py
# Compiled at: 2019-03-27 02:48:07
import sys
from functools import wraps
from warnings import warn_explicit
from constants import IS_DEVELOPMENT, IS_CLIENT

def CRITICAL_ERROR(msg, *kargs):
    print _makeMsgHeader('CRITICAL ERROR', sys._getframe(1)), msg, kargs
    if IS_CLIENT:
        import BigWorld
        BigWorld.quit()
    sys.exit()


def LOG_CURRENT_EXCEPTION():
    print _makeMsgHeader('EXCEPTION', sys._getframe(1))
    from traceback import print_exc
    print_exc()


def LOG_TRACEBACK():
    if IS_DEVELOPMENT:
        print _makeMsgHeader('STACKTRACE', sys._getframe(1))
        from traceback import print_stack
        print_stack()


def LOG_WRAPPED_CURRENT_EXCEPTION(wrapperName, orgName, orgSource, orgLineno):
    print '[%s] (%s, %d):' % ('EXCEPTION', orgSource, orgLineno)
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


def LOG_CODEPOINT_WARNING(*kargs):
    _doLog('WARNING', 'see the source code for details', kargs)


def LOG_ERROR(msg, *kargs):
    _doLog('ERROR', msg, kargs)


def LOG_WARNING(msg, *kargs):
    _doLog('WARNING', msg, kargs)


def LOG_NOTE(msg, *kargs):
    _doLog('NOTE', msg, kargs)


def LOG_DEBUG(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('DEBUG', msg, kargs)


def LOG_DEBUG_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('DEBUG', msg, kargs)


def LOG_NESTE(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('NESTE', msg, kargs)


def LOG_MX(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('MX', msg, kargs)


def LOG_MX_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('MX', msg, kargs)


def LOG_DZ(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('DZ', msg, kargs)


def LOG_TU(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('TU', msg, kargs)


def LOG_RF(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('RF', msg, kargs)


def LOG_GUI(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('GUI', msg, kargs)


def LOG_UNEXPECTED(msg, *kargs):
    _doLog('LOG_UNEXPECTED', msg, kargs)


def LOG_WRONG_CLIENT(entity, *kargs):
    if hasattr(entity, 'id'):
        entity = entity.id
    print _makeMsgHeader('WRONG_CLIENT', sys._getframe(1)), entity, kargs


def _doLog(s, msg, args):
    header = _makeMsgHeader(s, sys._getframe(2))
    if args:
        print header, msg, args
    else:
        print header, msg


def _makeMsgHeader(s, frame):
    return '[%s] (%s, %d):' % (s, frame.f_code.co_filename, frame.f_lineno)


def trace(func):
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    frame = sys._getframe(1)

    @wraps(func)
    def wrapper(*args, **kwds):
        print '[%s] (%s, %d) call %s:' % ('DEBUG',
         frame.f_code.co_filename,
         frame.f_lineno,
         fname), ':', ', '.join(('%s=%r' % entry for entry in zip(argnames, args) + kwds.items()))
        ret = func(*args, **kwds)
        print '[%s] (%s, %d) return from %s:' % ('DEBUG',
         frame.f_code.co_filename,
         frame.f_lineno,
         fname), ':', repr(ret)
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


def dump_garbage(source=False):
    """
    show us what's the garbage about
    """
    import inspect, gc
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


def verify(expression):
    try:
        assert expression
    except AssertionError:
        LOG_CURRENT_EXCEPTION()
