# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/base_queue_view.py
import BigWorld
from PlayerEvents import g_playerEvents
from helpers import dependency
from gui.impl.pub import ViewImpl
from story_mode.skeletons.story_mode_controller import IStoryModeController

class BaseWaitQueueView(ViewImpl):
    __slots__ = ('_timerCallback',)
    storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, *args, **kwargs):
        super(BaseWaitQueueView, self).__init__(*args, **kwargs)
        self._timerCallback = None
        return

    def startWaitQueue(self):
        if self._timerCallback is None:
            self._timerCallback = BigWorld.callback(self.storyModeCtrl.settings.waitTimeQueue, self._onWaitQueueTimeout)
        return

    def _onLoading(self, *args, **kwargs):
        super(BaseWaitQueueView, self)._onLoading(*args, **kwargs)
        g_playerEvents.onArenaCreated += self._onArenaCreated

    def _finalize(self):
        self._stopTimer()
        g_playerEvents.onArenaCreated -= self._onArenaCreated
        super(BaseWaitQueueView, self)._finalize()

    def _onArenaCreated(self):
        self._stopTimer()

    def _stopTimer(self):
        if self._timerCallback is not None:
            BigWorld.cancelCallback(self._timerCallback)
            self._timerCallback = None
        return

    def _onWaitQueueTimeout(self):
        self._timerCallback = None
        return
