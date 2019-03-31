# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/wotdecorators.py
# Compiled at: 2011-11-02 18:32:17
from debug_utils import LOG_WRAPPED_CURRENT_EXCEPTION

def noexcept(func):

    def wrapper(*args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except:
            LOG_WRAPPED_CURRENT_EXCEPTION(wrapper.__name__, func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1)

    return wrapper


def nofail(func):

    def wrapper(*args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except:
            LOG_WRAPPED_CURRENT_EXCEPTION(wrapper.__name__, func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1)
            import sys
            sys.exit()

    return wrapper
