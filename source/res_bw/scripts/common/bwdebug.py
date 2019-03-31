# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bwdebug.py
# Compiled at: 2010-05-25 20:46:16
import sys
printPath = False

def getClassName(f):
    try:
        selfClass = f.f_locals['self'].__class__
        try:
            mro = selfClass.__mro__
        except AttributeError:
            stack = [selfClass]
            mro = []
            while 1:
                curr = stack and stack.pop(0)
                mro.append(curr)
                stack += curr.__bases__

        funcName = f.f_code.co_name
        for c in mro:
            try:
                if funcName.startswith('__'):
                    method = c.__dict__['_' + c.__name__ + funcName]
                else:
                    method = c.__dict__[funcName]
                if method.func_code == f.f_code:
                    return c.__name__ + '.'
            except KeyError:
                pass

    except:
        pass


def printMessage(prefix, args, printPath):
    f = sys._getframe(2)
    if printPath:
        print f.f_code.co_filename + '(' + str(f.f_lineno) + ') :'
    print prefix, getClassName(f) + f.f_code.co_name + ':',
    for m in args:
        print m,

    print


def TRACE_MSG(*args):
    printMessage('Trace:', args, printPath)


def DEBUG_MSG(*args):
    printMessage('Debug:', args, printPath)


def INFO_MSG(*args):
    printMessage('Info:', args, printPath)


def NOTICE_MSG(*args):
    printMessage('Notice:', args, printPath)


def WARNING_MSG(*args):
    printMessage('Warning:', args, True)


def ERROR_MSG(*args):
    printMessage('Error:', args, True)


def CRITICAL_MSG(*args):
    printMessage('Critical:', args, True)


def HACK_MSG(*args):
    printMessage('Hack:', args, True)
