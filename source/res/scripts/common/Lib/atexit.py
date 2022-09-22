# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/atexit.py
# Compiled at: 2002-06-29 03:29:42
"""
atexit.py - allow programmer to define multiple exit functions to be executed
upon normal program termination.

One public function, register, is defined.
"""
__all__ = ['register']
import sys
_exithandlers = []

def _run_exitfuncs():
    """run any registered exit functions
    
    _exithandlers is traversed in reverse order so functions are executed
    last in, first out.
    """
    exc_info = None
    while _exithandlers:
        func, targs, kargs = _exithandlers.pop()
        try:
            func(*targs, **kargs)
        except SystemExit:
            exc_info = sys.exc_info()
        except:
            import traceback
            print >> sys.stderr, 'Error in atexit._run_exitfuncs:'
            traceback.print_exc()
            exc_info = sys.exc_info()

    if exc_info is not None:
        raise exc_info[0], exc_info[1], exc_info[2]
    return


def register(func, *targs, **kargs):
    """register a function to be executed upon normal program termination
    
    func - function to be called at exit
    targs - optional arguments to pass to func
    kargs - optional keyword arguments to pass to func
    
    func is returned to facilitate usage as a decorator.
    """
    _exithandlers.append((func, targs, kargs))
    return func


if hasattr(sys, 'exitfunc'):
    register(sys.exitfunc)
sys.exitfunc = _run_exitfuncs
if __name__ == '__main__':

    def x1():
        print 'running x1'


    def x2(n):
        print 'running x2(%r)' % (n,)


    def x3(n, kwd=None):
        print 'running x3(%r, kwd=%r)' % (n, kwd)


    register(x1)
    register(x2, 12)
    register(x3, 5, 'bar')
    register(x3, 'no kwd args')
