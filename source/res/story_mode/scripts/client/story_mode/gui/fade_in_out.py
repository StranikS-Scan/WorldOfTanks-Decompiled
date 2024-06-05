# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/fade_in_out.py
import logging
import time
from functools import wraps
from BWUtil import AsyncReturn
import BattleReplay
import BigWorld
import adisp
from frameworks.wulf import WindowLayer
from gui.shared import g_eventBus
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from helpers import dependency
from story_mode.gui.shared.event import StoryModeViewReadyEvent
from story_mode.skeletons.story_mode_fading_controller import IStoryModeFadingController
from wg_async import wg_await, wg_async, BrokenPromiseError, await_callback, forwardAsFuture, AsyncEvent
_logger = logging.getLogger(__name__)
WAIT_FOR_EVENT_TIMEOUT = 10.0

class _AsyncEventWithTimout(AsyncEvent):

    def __init__(self, warning, state=False, scope=None):
        super(_AsyncEventWithTimout, self).__init__(state, scope)
        self._warning = warning
        self._expireTime = None
        self._updateTimeoutID = None
        return

    def wait(self):
        if not self.is_set():
            self._updateTimeoutID = BigWorld.callback(0, self.update)
            self._expireTime = time.time() + WAIT_FOR_EVENT_TIMEOUT
        return super(_AsyncEventWithTimout, self).wait()

    def set(self):
        if self._updateTimeoutID is not None:
            BigWorld.cancelCallback(self._updateTimeoutID)
            self._updateTimeoutID = None
        super(_AsyncEventWithTimout, self).set()
        return

    def update(self):
        if self._expireTime > time.time():
            self._updateTimeoutID = BigWorld.callback(0, self.update)
        else:
            _logger.warning(self._warning)
            self.set()


class UseStoryModeFading(object):
    __slots__ = ('_hide', '_show', '_layer', '_waitForLayoutReady', '_currentFunctions', '_callback')
    _fadeManager = dependency.descriptor(IStoryModeFadingController)

    def __init__(self, show=True, hide=True, layer=WindowLayer.OVERLAY, waitForLayoutReady=None, callback=None):
        super(UseStoryModeFading, self).__init__()
        self._hide = hide
        self._show = show
        self._layer = layer
        self._waitForLayoutReady = waitForLayoutReady
        self._currentFunctions = set()
        self._callback = callback

    def __call__(self, func):

        @wraps(func)
        @wg_async
        def wrapper(*args, **kwargs):
            if func in self._currentFunctions:
                return
            else:
                self._currentFunctions.add(func)
                try:
                    asyncEvent = _AsyncEventWithTimout('Got time-out during the fade-in/fade-out animation.')

                    def viewReadyHandler(event):
                        if event.viewID == self._waitForLayoutReady:
                            asyncEvent.set()

                    if self._waitForLayoutReady is None:
                        asyncEvent.set()
                    else:
                        g_eventBus.addListener(StoryModeViewReadyEvent.VIEW_READY, viewReadyHandler)
                    if not BattleReplay.isPlaying() and self._show:
                        yield wg_await(self._fadeManager.show(self._layer))
                    if adisp.isAsync(func):
                        yield await_callback(func)(*args, **kwargs)
                    else:
                        yield wg_await(forwardAsFuture(func(*args, **kwargs)))
                    yield wg_await(asyncEvent.wait())
                    g_eventBus.removeListener(StoryModeViewReadyEvent.VIEW_READY, viewReadyHandler)
                    if not BattleReplay.isPlaying() and self._hide:
                        yield wg_await(self._fadeManager.hide(self._layer))
                except BrokenPromiseError:
                    _logger.debug('%s got BrokenPromiseError during the fade-in/fade-out animation.', func)

                self._currentFunctions.remove(func)
                if self._callback is not None:
                    self._callback()
                return

        return wrapper


class UseHeaderNavigationImpossible(object):

    def __call__(self, func):

        @wraps(func)
        @wg_async
        def wrapper(*args, **kwargs):

            @wg_async
            def confirmation():
                raise AsyncReturn(False)

            confirmationHelper = CloseConfirmatorsHelper()
            confirmationHelper.start(confirmation)
            yield wg_await(forwardAsFuture(func(*args, **kwargs)))
            confirmationHelper.stop()

        return wrapper
