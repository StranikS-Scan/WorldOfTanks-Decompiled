# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/async.py
import sys
import weakref
from collections import deque
from soft_exception import SoftException
import BigWorld
from BWUtil import AsyncReturn
from functools import wraps, partial
from constants import IS_DEVELOPMENT
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING, LOG_DEBUG, LOG_DEBUG_DEV

def async(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        promise = _Promise()
        executor = _AsyncExecutor(gen, promise)
        executor.start()
        return promise.get_future()

    return wrapper


def await(future, timeout=None):
    if timeout is not None:
        future.set_timeout(timeout)
    return future


def await_callback(func, timeout=None):

    def wrapper(*args, **kwargs):
        promise = _Promise()

        def callback(*args):
            if len(args) == 1:
                args = args[0]
            promise.set_value(args)

        kwargs['callback'] = callback
        func(*args, **kwargs)
        return await(promise.get_future(), timeout)

    return wrapper


def await_deferred(d):
    promise = _Promise()

    def callback(value):
        promise.set_value(value)

    def errback(failure):
        try:
            failure.raiseException()
        except:
            promise.set_exception(*sys.exc_info())

    futureCallback = getattr(d, 'addCallback', None)
    if futureCallback is not None:
        futureCallback(callback)
        futureErrback = getattr(d, 'addErrback', None)
        if futureErrback is not None:
            futureErrback(errback)
    else:
        callback(d)
    return promise.get_future()


def resignTickIfRequired(timeout=0.1):
    if BigWorld.isNextTickPending():
        return delay(timeout)
    else:
        promise = _Promise()
        promise.set_value(None)
        return promise.get_future()
        return


def delay(timeout):
    promise = _Promise()

    def onTimer(timerID, userArg):
        promise.set_value(None)
        return

    timerID = BigWorld.addTimer(onTimer, timeout)
    promise.set_cancel_handler(partial(BigWorld.delTimer, timerID))
    return promise.get_future()


def _isNextTickPending():
    return BigWorld.isNextTickPending()


@async
def delayWhileTickPending(maxTicksToDelay=1, timeout=0.1, logID=None):
    for n in xrange(maxTicksToDelay):
        if not _isNextTickPending():
            LOG_DEBUG_DEV('delayWhileTickPending', logID, n)
            break
        yield await(delay(timeout))
    else:
        LOG_DEBUG('delayWhileTickPending reached maxTicksToDelay', logID, maxTicksToDelay)


def delayable(maxTicksToDelay=1, timeout=0.1):

    def decorator(func):

        @wraps(func)
        @async
        def wrapper(*args, **kwargs):
            yield delayWhileTickPending(maxTicksToDelay, timeout, logID=func)
            func(*args, **kwargs)

        return wrapper

    return decorator


@async
def distributeLoopOverTicks(loopIterator, minPerTick=None, maxPerTick=None, logID=None, tickLength=0.1):
    numStatements = 0
    countInTick = 0
    delayedCount = 0
    for _ in loopIterator:
        countInTick += 1
        numStatements += 1
        reachedMin = minPerTick is None or countInTick >= minPerTick
        reachedMax = maxPerTick is not None and countInTick >= maxPerTick
        if reachedMax or reachedMin and _isNextTickPending():
            yield await(delay(tickLength))
            countInTick = 0
            delayedCount += 1

    if logID is not None:
        LOG_DEBUG('distributeLoopOverTicks logID/numStatements/delayedCount', logID, numStatements, delayedCount)
    return


class TimeoutError(SoftException):
    pass


class BrokenPromiseError(SoftException):
    pass


class _Future(object):

    def __init__(self, promise):
        self.__promise = weakref.proxy(promise)
        self.__callback = None
        self.__callback_set = False
        self.__result = None
        self.__result_set = False
        self.__timerID = None
        self.__expired = False
        return

    def __del__(self):
        self.__cancel_timeout()
        if self.__result_set and self.__result is not None:
            try:
                self.__result.get()
            except:
                LOG_CURRENT_EXCEPTION()

        return

    def set_result(self, result):
        if self.__expired:
            try:
                result.get()
            except:
                LOG_CURRENT_EXCEPTION()

            return
        else:
            self.__cancel_timeout()
            self.__result_set = True
            if self.__callback is not None:
                callback = self.__callback
                self.__callback = None
                callback(result)
            else:
                self.__result = result
            return

    def then(self, callback):
        self.__callback_set = True
        if self.__result_set:
            result = self.__result
            self.__result = None
            callback(result)
        else:
            self.__callback = callback
        return

    def cancel(self):
        if self.__result_set:
            return
        self.__promise.cancel()

    def _confirm_cancel(self):
        self.__result_set = True
        self.__callback = None
        self.__cancel_timeout()
        return

    def set_timeout(self, timeout):
        if not self.__result_set:
            self.__timerID = BigWorld.addTimer(self.__expire, timeout)

    def __cancel_timeout(self):
        if self.__timerID is not None:
            BigWorld.delTimer(self.__timerID)
            self.__timerID = None
        return

    def __expire(self, timerID, userArg):
        try:
            self.set_result(_ExpiredPromiseResult())
        finally:
            self.__expired = True
            self.__promise.cancel()


class _Promise(object):

    def __init__(self):
        self.__value_set = self.__future_set = False
        self.__exc_info = self.__value = None
        self.__future = None
        self.__cancelled = False
        self.__cancel = None
        return

    def __del__(self):
        if not self.__value_set:
            if self.__future_set:
                if self.__cancelled:
                    self.__future._confirm_cancel()
                else:
                    self.__future.set_result(_BrokenPromiseResult())
        elif not self.__future_set and self.__exc_info is not None:
            try:
                raise self.__exc_info[0], self.__exc_info[1], self.__exc_info[2]
            except:
                LOG_CURRENT_EXCEPTION()

        return

    def set_value(self, value):
        self.__value_set = True
        self.__cancel = None
        future = self.__future
        if future is not None:
            self.__future = None
            future.set_result(_FulfilledPromiseResult(value, None))
        else:
            self.__value = value
        return

    def set_exception(self, type, value=None, traceback=None):
        self.__value_set = True
        self.__cancel = None
        future = self.__future
        exc_info = (type, value, traceback)
        if future is not None:
            self.__future = None
            future.set_result(_FulfilledPromiseResult(None, exc_info))
        else:
            self.__exc_info = exc_info
        return

    def set_cancel_handler(self, func):
        if not self.__value_set:
            self.__cancel = func
            if self.__cancelled:
                self.cancel()

    def cancel(self):
        if self.__value_set:
            return
        self.__cancelled = True
        cancel = self.__cancel
        if cancel:
            cancel()
        elif IS_DEVELOPMENT:
            LOG_WARNING('Promise is not cancellable', self)
            import traceback
            traceback.print_stack()

    def get_future(self):
        self.__future_set = True
        future = _Future(self)
        if self.__value_set:
            future.set_result(_FulfilledPromiseResult(self.__value, self.__exc_info))
            self.__value = self.__exc_info = None
            return future
        else:
            self.__future = future
            return future
            return


class _FulfilledPromiseResult(object):

    def __init__(self, value, exc_info):
        self.__value = value
        self.__exc_info = exc_info

    def get(self):
        exc_info = self.__exc_info
        if exc_info is not None:
            raise exc_info[0], exc_info[1], exc_info[2]
        return self.__value


class _ExpiredPromiseResult(object):

    def get(self):
        raise TimeoutError()


class _BrokenPromiseResult(object):

    def get(self):
        raise BrokenPromiseError()


class _AsyncExecutor(object):

    def __init__(self, gen, promise):
        self.__gen = gen
        self.__promise = promise

    def start(self):
        self.__step(self.__gen.send, None)
        return

    def __step(self, next, *args):
        try:
            future = next(*args)
            future.then(self.__resume)
            handler = getattr(future, 'cancel', None)
            self.__promise.set_cancel_handler(handler)
        except AsyncReturn as r:
            self.__promise.set_value(r.value)
        except StopIteration:
            self.__promise.set_value(None)
        except BaseException:
            self.__promise.set_exception(*sys.exc_info())

        return

    def __resume(self, result):
        gen = self.__gen
        try:
            result = result.get()
            self.__step(gen.send, result)
        except BaseException:
            self.__step(gen.throw, *sys.exc_info())


class AsyncScope(object):

    def __init__(self):
        self.__objects = weakref.WeakSet()

    def __del__(self):
        self.destroy()

    def registerObject(self, obj):
        self.__objects.add(obj)
        return obj

    def destroy(self):
        if self.__objects:
            for lock in self.__objects:
                lock.destroy()

        self.__objects = None
        return


class AsyncObject(object):

    def __init__(self, scope=None):
        if scope:
            scope.registerObject(self)

    def _register_cancel(self, promise):
        cancel = type(self)._cancel
        self_ref = weakref.ref(self)
        promise_ref = weakref.ref(promise)
        promise.set_cancel_handler(lambda : cancel(self_ref(), promise_ref()))

    def _cancel(self, promise):
        pass


class AsyncEvent(AsyncObject):

    def __init__(self, state=False, scope=None):
        super(AsyncEvent, self).__init__(scope)
        self.__state = state
        self.__promises = []

    def is_set(self):
        return self.__state

    def set(self):
        self.__state = True
        promises = self.__promises
        self.__promises = []
        for promise in promises:
            promise.set_value(None)

        return

    def clear(self):
        self.__state = False

    def wait(self):
        promise = _Promise()
        if self.__state:
            promise.set_value(None)
        else:
            self.__promises.append(promise)
            self._register_cancel(promise)
        return promise.get_future()

    def _cancel(self, promise):
        self.__promises.remove(promise)

    def destroy(self):
        del self.__promises
        del self.__state


class AsyncSemaphore(AsyncObject):

    def __init__(self, value=1, scope=None):
        super(AsyncSemaphore, self).__init__(scope)
        self.__value = value
        self.__promises = deque()

    def release(self):
        if self.__promises:
            promise = self.__promises.popleft()
            promise.set_value(None)
        else:
            self.__value += 1
        return

    def acquire(self):
        promise = _Promise()
        if self.__value != 0:
            promise.set_value(None)
            self.__value -= 1
        else:
            self.__promises.append(promise)
            self._register_cancel(promise)
        return promise.get_future()

    def _cancel(self, promise):
        self.__promises.remove(promise)

    def destroy(self):
        del self.__promises
        del self.__value


class AsyncQueue(AsyncObject):

    def __init__(self, scope=None):
        super(AsyncQueue, self).__init__(scope)
        self.__promises = deque()
        self.__values = deque()

    def dequeue(self):
        promise = _Promise()
        if self.__values:
            value, exc_info = self.__values.popleft()
            if exc_info is None:
                promise.set_value(value)
            else:
                promise.set_exception(*exc_info)
        else:
            self.__promises.append(promise)
            self._register_cancel(promise)
        return promise.get_future()

    def enqueue(self, value):
        if self.__promises:
            promise = self.__promises.popleft()
            promise.set_value(value)
        else:
            self.__values.append((value, None))
        return

    def throw(self, type, value=None, traceback=None):
        exc_info = (type, value, traceback)
        if self.__promises:
            promise = self.__promises.popleft()
            promise.set_exception(*exc_info)
        else:
            self.__values.append((None, exc_info))
        return

    def _cancel(self, promise):
        self.__promises.remove(promise)

    def destroy(self):
        del self.__promises
        del self.__values
