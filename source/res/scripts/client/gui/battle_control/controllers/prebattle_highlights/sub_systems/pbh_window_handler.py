# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/sub_systems/pbh_window_handler.py
from __future__ import absolute_import
import logging
import typing
import Windowing
from frameworks.wulf import WindowLayer
from gui.battle_control.controllers.prebattle_highlights.sub_systems.base_sub_system import BasePbhSubSystem
from gui.impl.battle.prebattle_highlights.utils import getPrebattleHighlightsWindow
from gui.impl.common.fade_manager import FadeManager, FadingCoverWindow, DefaultFadingCover
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from uilogging.prebattle_highlights.loggers import PrebattleHighlightsEventLogger
from wg_async import await_callback, wg_async
if typing.TYPE_CHECKING:
    from typing import Optional, Callable
    from gui.impl.common.fade_manager import ICover
_logger = logging.getLogger(__name__)

class _PreloadedFadeManager(FadeManager):

    def __init__(self, layer, coverFactory=None):
        super(_PreloadedFadeManager, self).__init__(layer, coverFactory)
        self._preloaded = False

    def preload(self):
        if self._currentWindow:
            self.hideImmediately()
        self._preloaded = True

    def hideImmediately(self):
        super(_PreloadedFadeManager, self).hideImmediately()
        self._preloaded = False

    @wg_async
    def _doShow(self):
        if self._isDestroyed:
            return
        else:
            container = self._appLoader.getApp().containerManager.getContainer(self._layer)
            if container is None:
                return
            if self._currentWindow is None:
                cover = self._coverFactory() if self._coverFactory else DefaultFadingCover(fadeInDuration=0.5, fadeOutDuration=0.5)
                self._currentWindow = FadingCoverWindow(content=cover, layer=self._layer)
            self._gui.windowsManager.onWindowStatusChanged += self._windowStatusChanged
            yield await_callback(self._currentWindow.fadeOut)()
            return


class PbhWindowHandler(BasePbhSubSystem):

    def __init__(self, readyCallback):
        self.__window = None
        self.__windowReady = False
        self.__fadeManager = _PreloadedFadeManager(WindowLayer.OVERLAY)
        self.__uiLogger = PrebattleHighlightsEventLogger()
        super(PbhWindowHandler, self).__init__(readyCallback)
        return

    def subscribe(self):
        g_eventBus.addListener(GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def unsubscribe(self):
        g_eventBus.removeListener(GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def isReady(self):
        return self.__window is not None and self.__windowReady

    def startFlow(self):
        if not self.isReady():
            return
        self.__window.show()
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        if not Windowing.isWindowAccessible():
            self.__uiLogger.logUnfocusClientEvent()

    def stopFlow(self):
        if self.__window is not None:
            self.__window.destroy()
            self.__window = None
            self.__windowReady = False
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.__uiLogger.reset()
        return

    def clear(self):
        if self.__window is not None:
            self.__window = None
            self.__windowReady = False
        self.__fadeManager = None
        super(PbhWindowHandler, self).clear()
        return

    def preload(self):
        self.__preload()

    def forceStopFlow(self):
        if self.__window is not None:
            self.__window.destroy()
            self.__window = None
            self.__windowReady = False
        if self.__fadeManager is not None:
            self.__fadeManager.hideImmediately()
        return

    @wg_async
    def toggleFadeManager(self, value):
        if value:
            yield self.__fadeManager.show()
        else:
            yield self.__fadeManager.hide()

    def __handleBattleLoading(self, event):
        if event.ctx.get('isShown', False):
            self.__preload()

    def __preload(self):
        if self.__window is None:
            windowClass = getPrebattleHighlightsWindow()
            if windowClass is not None:
                self.__window = windowClass()
                self.__window.onReady += self.__onPBHWindowReady
                self.__window.load()
        self.__fadeManager.preload()
        return

    def __onPBHWindowReady(self):
        _logger.debug('[PBH] onPBHWindowReady')
        self.__window.onReady -= self.__onPBHWindowReady
        self.__windowReady = True
        self._readyCallback()

    def __onWindowAccessibilityChanged(self, isAccessible):
        if not isAccessible:
            self.__uiLogger.logUnfocusClientEvent()
