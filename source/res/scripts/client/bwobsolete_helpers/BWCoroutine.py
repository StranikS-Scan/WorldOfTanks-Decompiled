# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/BWCoroutine.py
import BigWorld
from functools import partial
import types
import exceptions

def BWCoroutine(coroutineFunction):
    return _BWCoroutineFunction(coroutineFunction)


def BWMemberCoroutine(coroutineFunction):
    return _BWCoroutineMemberDescriptor(coroutineFunction)


class BWCoroutineTimeoutException(Exception):
    pass


class _BWCoroutineThread:

    def __init__(self, generator, completionCallback=None):
        self._generator = generator
        self._completionCallback = completionCallback
        self._waitObject = None
        return

    def run(self):
        self._tick()

    def _tick(self):
        self._waitObject = None
        try:
            self._waitObject = self._generator.next()
            self._waitObject.doWait(self)
        except StopIteration:
            if self._completionCallback is not None:
                self._completionCallback()
            return

        return

    def stop(self):
        self._waitObject.onStop()
        self._generator.close()

    def onContinue(self):
        self._tick()

    def raiseTimeout(self):
        try:
            self._waitObject = self._generator.throw(BWCoroutineTimeoutException)
        except StopIteration:
            pass


class _BWCoroutineFunction(object):

    def __init__(self, coroutineFunction):
        self._function = coroutineFunction

    def __call__(self, *args, **kwds):
        return _BWCoroutineThread(self._function(*args, **kwds))


class _BWCoroutineMemberFunction(object):

    def __init__(self, instance, coroutineFunction):
        self._instance = instance
        self._function = coroutineFunction

    def __call__(self, *args, **kwds):
        return _BWCoroutineThread(self._function(self._instance, *args, **kwds))


class _BWCoroutineMemberDescriptor(object):

    def __init__(self, coroutineFunction):
        self.coroutineFunction = coroutineFunction

    def __get__(self, instance, type):
        return _BWCoroutineMemberFunction(instance, self.coroutineFunction)


class _BWWaitObject:

    def __init__(self):
        pass

    def doWait(self, coroutineThread):
        pass

    def onStop(self):
        pass


class BWWaitForPeriod(_BWWaitObject):

    def __init__(self, waitTime):
        _BWWaitObject.__init__(self)
        self.waitTime = waitTime

    def doWait(self, coroutineThread):
        BigWorld.callback(self.waitTime, coroutineThread.onContinue)


class BWWaitForCondition(_BWWaitObject):

    def __init__(self, condition, timeout=None, checkFrequency=0.01):
        _BWWaitObject.__init__(self)
        self._condition = condition
        self._checkFrequency = checkFrequency
        if timeout is not None:
            self._timeoutTime = BigWorld.time() + timeout
        else:
            self._timeoutTime = None
        self._stopped = False
        return

    def doWait(self, coroutineThread):
        self._thread = coroutineThread
        self._tick()

    def _tick(self):
        if self._stopped:
            return
        else:
            if self._condition():
                self._thread.onContinue()
            elif self._timeoutTime is not None and BigWorld.time() >= self._timeoutTime:
                self._thread.raiseTimeout()
            else:
                BigWorld.callback(self._checkFrequency, self._tick)
            return

    def onStop(self):
        self._stopped = True


class BWWaitForCoroutine(_BWWaitObject):

    def __init__(self, waitThread, timeout=None):
        _BWWaitObject.__init__(self)
        self._waitThread = waitThread
        self._hostThread = None
        self._waitThread._completionCallback = self.handleCompletionCallback
        if timeout is not None:
            BigWorld.callback(timeout, self.handleTimeout)
        return

    def doWait(self, coroutineThread):
        self._hostThread = coroutineThread
        self._waitThread.run()

    def onStop(self):
        self._waitThread.stop()

    def handleCompletionCallback(self):

        def timeout_noop():
            pass

        self._onTimeout = timeout_noop
        self._hostThread.onContinue()

    def handleTimeout(self):
        self._onTimeout()

    def _onTimeout(self):
        self._waitThread.stop()
        self._hostThread.raiseTimeout()


def _niceFunctionString(f):
    if isinstance(f, partial):
        return 'partial %s %s %s:%d' % (f.func.func_name,
         f.args,
         f.func.func_code.co_filename,
         f.func.func_code.co_firstlineno)
    elif isinstance(f, types.LambdaType):
        return 'lambda %s:%d' % (f.func_code.co_filename, f.func_code.co_firstlineno)
    elif isinstance(f, types.FunctionType):
        return 'function %s %s:%d' % (f.func_name, f.func_code.co_filename, f.func_code.co_firstlineno)
    elif isinstance(f, types.GeneratorType):
        return 'generator %s %s:%d' % (f.gi_frame.f_code.co_name, f.gi_frame.f_code.co_filename, f.gi_frame.f_lineno)
    elif isinstance(f, _BWCoroutineFunction):
        return _niceFunctionString(f.coroutineFunction)
    elif isinstance(f, _BWCoroutineMemberFunction):
        return _niceFunctionString(f.coroutineFunction)
    else:
        return str(f)
