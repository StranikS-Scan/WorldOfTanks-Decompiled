# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_hangar_marker_view.py
from frameworks.wulf import WindowLayer, WindowStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.impl.lobby.new_year.main_view import MainView
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class NyHangarMarkerView(ViewImpl):
    __slots__ = ()
    __guiLoader = dependency.descriptor(IGuiLoader)
    __LAYERS_WITHOUT_MARKERS = {WindowLayer.FULLSCREEN_WINDOW,
     WindowLayer.OVERLAY,
     WindowLayer.SUB_VIEW,
     WindowLayer.TOP_SUB_VIEW}
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def _onLoading(self, *args, **kwargs):
        super(NyHangarMarkerView, self)._onLoading(*args, **kwargs)
        self.__guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def _finalize(self):
        super(NyHangarMarkerView, self)._finalize()
        self.__guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def _setMarkerVisible(self, value):
        pass

    def __canShowMarkers(self):
        windowsManager = self.__guiLoader.windowsManager
        windows = windowsManager.findWindows(lambda w: w.layer in self.__LAYERS_WITHOUT_MARKERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)
        hangarExists = len(windowsManager.findWindows(lambda w: isinstance(w, SFWindow) and w.loadParams.viewKey.alias == VIEW_ALIAS.LOBBY_HANGAR)) > 0
        mainViewExists = next((w for w in windows if isinstance(w.content, MainView)), None) is not None
        return len(windows) == 1 and hangarExists or mainViewExists

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            self._setMarkerVisible(self.__canShowMarkers())
