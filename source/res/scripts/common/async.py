# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/async.py
"""This module is used for simplifying code based on callbacks, and can be used to write code
like this:

import BigWorld
from async import *

@async
def notify(entityID):
    entity = yield await(BigWorld.baseApp.lookUpBaseByDBID('Entity', entityID))
    if not isinstance(entity, bool):
        entity.notify()

The @async function is invoked as usual, but it's execution may suspend at yield to wait when results
are available to continue. @async function can be used in another @async function like this:
@async
def asyncFunction1():
  yield await(asyncFunction2())

Due to python 2.7 limitations, generators are not allowed to return value. If this is desired,
@async functions can use raise AsyncReturn(value) statement to return value.

This module is not safe to use in multithreaded environment. All callbacks are assumed to run
in the same thread as async function calls.
"""
import sys
import weakref
from collections import deque
import BigWorld
from BWUtil import AsyncReturn
from functools import wraps
from constants import IS_DEVELOPMENT
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING

def async(func):
    """
    Decorator for indicating that function is executed asynchronously. It means that function has
    certain points when execution is suspended and wait for some external event to continue.
    Function must be implemented as generator, which yields Future objects. Future objects are
    typically obtained from calls to other @async functions, or by using objects such as AsyncEvent.
    The result of yield expression will be the result set to Future object on completion.
    Result can also be an exception, which will thrown from yield.
    yield can also throw BrokenPromiseException if the system detects that yielded Future cannot be
    completed because owner lost reference to it.
    @async function returns Future object, which is completed when function returns or throws.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        promise = _Promise()
        executor = _AsyncExecutor(gen, promise)
        executor.start()
        return promise.get_future()

    return wrapper


def await(future, timeout=None):
    """
    Should be used inside functions decorated with @async in yield expressions:
    @async
    def asyncFunction():
        yield await(self.otherAsyncFunction(), timeout=10)
    Timeout can be specified to limit time to execute invoked async function. TimoutError will be
    raised if invoked function cannot complete in time.
    Note, that timeout does not terminate other function execution. It may still complete, but the
    result will not be delivered to the caller.
    """
    if timeout is not None:
        future.set_timeout(timeout)
    return future


def await_callback(func, timeout=None):
    """
    Similar to await, but can be used on functions that require callback parameter:
        result = yield await_callback(self.otherAsyncFunction, timeout=10)(param1, param2)
    It wraps function passed as a parameter and returns new function which does not require callback
    parameter and returns Future object. Parameters passed to callback will be returned from yield
    expression.
    """

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
    """Similar to await, but for waiting functions returning twisted Deferred object.
    Deferred is used in BigWorld's two way calls.
    For example:
        try:
            type, value = yield await_deferred(remoteFind(key))
        except MyException, e:
            # this code is invoked in case errback is called on deferred
            ...
    """
    promise = _Promise()

    def callback(value):
        promise.set_value(value)

    def errback(failure):
        try:
            failure.raiseException()
            assert False
        except:
            promise.set_exception(*sys.exc_info())

    d.addCallback(callback)
    d.addErrback(errback)
    return promise.get_future()


def resignTickIfRequired(timeout=0.1):
    """Used inside @async functions together with yield to postpone execution to next tick
    if it is required. Usage example:
        yield resignTickIfRequired()
    
    Note: In case of using the function inside entity function you should check entity destruction.
    """
    if BigWorld.isNextTickPending():
        return delay(timeout)
    else:
        promise = _Promise()
        promise.set_value(None)
        return promise.get_future()
        return


def delay(timeout):
    """
    Note: In case of using the function inside entity function you should check entity destruction.
    Allows to postpone execution on the specified time.
    """
    promise = _Promise()

    def onTimer(timerID, userArg):
        promise.set_value(None)
        return

    BigWorld.addTimer(onTimer, timeout)
    return promise.get_future()


class TimeoutError(Exception):
    pass


class BrokenPromiseError(Exception):
    pass


class _Future(object):
    """
    Similar to BigWorld's internal PyFuture, but can be created in python code,
    supports timeout and cancellation.
    """

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
        """
        Invoked by Promise when result for this Future is retrieved. Result object should have get
        method to fetch actual value or raise exception.
        """
        if self.__expired:
            try:
                result.get()
            except:
                LOG_CURRENT_EXCEPTION()

            return
        else:
            self.__cancel_timeout()
            assert not self.__result_set
            self.__result_set = True
            if self.__callback is not None:
                callback = self.__callback
                self.__callback = None
                callback(result)
            else:
                self.__result = result
            return

    def then(self, callback):
        """
        Sets callback that will be invoked, when the result is ready.
        """
        assert not self.__callback_set
        self.__callback_set = True
        if self.__result_set:
            result = self.__result
            self.__result = None
            callback(result)
        else:
            self.__callback = callback
        return

    def cancel(self):
        """
        Requests cancellation. Calling this function does not guarantee that execution
        will be actually cancelled. It can still complete execution, for example,
        in cases, when cancelling is not possible.
        When cancelling generator based @async functions, generator should properly handle
        GeneratorExit exceptions (they should not be caught).
        """
        if self.__result_set:
            return
        self.__promise.cancel()

    def _confirm_cancel(self):
        self.__result_set = True
        self.__callback = None
        self.__cancel_timeout()
        return

    def set_timeout(self, timeout):
        assert self.__timerID is None
        assert timeout >= 0
        self.__timerID = BigWorld.addTimer(self.__expire, timeout)
        return

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
    """
    Similar to BigWorld's internal PyPromise, but can be created in python code.
    """

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
        """
        Indicates that Promise has successfully completed with the specified value.
        """
        assert not self.__value_set
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
        """
        Indicates that Promise has failed with the specified exception.
        """
        assert not self.__value_set
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
        """
        Sets function that can cancel this promise, when requested by consumer.
        func has a single parameter - promise which is being cancelled.
        By default, cancelling does nothing.
        """
        if not self.__value_set:
            self.__cancel = func
            if self.__cancelled:
                self.cancel()

    def cancel(self):
        """
        Attempts to cancel Promise. Cancel handler should be set via set_cancel_handler, otherwise
        this call will not have effect. See also Future.cancel.
        """
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
        """
        Returns Future object that can be used to retrieve result of the Promise.
        """
        assert not self.__future_set
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
    """
    Executes generator code by resuming when necessary.
    Special care should be taken here to avoid cyclic references or holding references unnecessarily.
    """

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
            self.__promise.set_cancel_handler(future.cancel)
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
    """
    Provides scope for async primitives, such as semaphore.
    If scope is destroyed or it's no longer referenced by any object, it will invalidate
    all primitives, and fail all wait operations on them.
    """

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
    """
    Base class for different async primitives, such as event, semaphore, etc.
    """

    def __init__(self, scope=None):
        if scope:
            scope.registerObject(self)

    def _register_cancel(self, promise):
        """
        Registers cancellation routine in specified promise.
        When promise is cancelled, _cancel will be invoked with the promise as argument.
        """
        cancel = type(self)._cancel
        self_ref = weakref.ref(self)
        promise_ref = weakref.ref(promise)
        promise.set_cancel_handler(lambda : cancel(self_ref(), promise_ref()))

    def _cancel(self, promise):
        """
        Override in subclasses to perform cancellation for the specified promise.
        _register_cancel must be called for promise to have _cancel called.
        """
        pass


class AsyncEvent(AsyncObject):
    """
    Event can be in two states: set and cleared. When event is set, then all wait requests are
    satisfied, otherwise requests are enqueued and wait for setting an event.
    Unlike in synchronous version of event, wait does not block. It always returns Future object,
    and caller should rely on callback to ensure that event is set.
    """

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
    """
    Semaphore provides tow operations:
        release - increases internal counter.
        acquire - decreases internal counter.
    Internal counter cannot become below zero, so if acquire operation is requested when counter
    is zero, it should wait for release operation performed somewhere else.
    Unlike in synchronous version of semaphore, acquire does not block. It always returns Future object,
    and caller should rely on callback to ensure that semaphore is in signaled state.
    """

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
    """
    Provides enqueue and dequeue operations. If queue is empty, then dequeue operation may need
    to wait. In addition to enqueue operation, throw operation is supported. When result of throw
    operation is dequeued, Future returned by dequeue will throw an exception.
    Unlike in synchronous version of queue, dequeue does not block. It always returns Future object,
    and caller should rely on callback to wait for an enqueue operation.
    """

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
