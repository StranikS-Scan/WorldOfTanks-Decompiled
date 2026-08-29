# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/synchronous_event.py
from __future__ import absolute_import
from wg_async import wg_async, forwardAsFuture, wg_await
from debug_utils import LOG_CURRENT_EXCEPTION
from Event import Event

class SynchronousEvent(Event):
    __slots__ = ()

    @wg_async
    def __call__(self, *args, **kwargs):
        for delegate in self[:]:
            try:
                yield wg_await(forwardAsFuture(delegate(*args, **kwargs)))
            except:
                LOG_CURRENT_EXCEPTION()
