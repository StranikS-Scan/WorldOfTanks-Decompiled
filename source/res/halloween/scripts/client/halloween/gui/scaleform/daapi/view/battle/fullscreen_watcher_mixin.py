# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/fullscreen_watcher_mixin.py
from __future__ import absolute_import
from frameworks.wulf import WindowStatus, WindowLayer
from halloween.gui.impl.battle.help_view import HelpWindow
from halloween.gui.scaleform.daapi.view.battle.anomalies_watcher_mixin import AnomaliesWatcherMixin
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class FullscreenWatcherMixin(AnomaliesWatcherMixin):
    guiLoader = dependency.descriptor(IGuiLoader)
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)
    __RESTRICTED_LAYERS = (WindowLayer.FULLSCREEN_WINDOW,
     WindowLayer.OVERLAY,
     WindowLayer.TOP_WINDOW,
     WindowLayer.WINDOW,
     WindowLayer.TOP_SUB_VIEW)

    def __init__(self, *args, **kwargs):
        super(FullscreenWatcherMixin, self).__init__(*args, **kwargs)
        self.__isWindowOverlapped = False

    def updateVisibility(self):
        self.as_setVisibleS(self.isDisplayAllowed and self.needToShow and not self.__isWindowOverlapped)

    def _populate(self):
        super(FullscreenWatcherMixin, self)._populate()
        self.guiLoader.windowsManager.onViewStatusChanged += self._onViewStatusChanged

    def _dispose(self):
        self.guiLoader.windowsManager.onViewStatusChanged -= self._onViewStatusChanged
        super(FullscreenWatcherMixin, self)._dispose()

    def _onViewStatusChanged(self, _, newStatus):
        if newStatus not in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            return
        windows = self.guiLoader.windowsManager.findWindows(lambda w: w.layer in self.__RESTRICTED_LAYERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)
        self.__isWindowOverlapped = bool(windows) and not (len(windows) == 1 and isinstance(windows[0], HelpWindow))
        self.updateVisibility()
