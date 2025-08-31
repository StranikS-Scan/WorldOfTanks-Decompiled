# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/synchronous_event.py
from th_async import th_async, forwardAsFuture, th_await
from debug_utils import LOG_CURRENT_EXCEPTION
from Event import Event

class SynchronousEvent(Event):
    __slots__ = ()

    def __init__(self, manager=None):
        super(SynchronousEvent, self).__init__(manager)

    @th_async
    def __call__(self, *args, **kwargs):
        for delegate in self[:]:
            try:
                yield th_await(forwardAsFuture(delegate(*args, **kwargs)))
            except:
                LOG_CURRENT_EXCEPTION()
