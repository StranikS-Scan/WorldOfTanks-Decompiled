# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/markers/base_marker_view.py
from frameworks.wulf import WindowLayer, WindowStatus, ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntity
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class BaseHangarMarkerView(ViewImpl):
    __slots__ = ()
    __guiLoader = dependency.descriptor(IGuiLoader)
    __LAYERS_WITHOUT_MARKERS = {WindowLayer.FULLSCREEN_WINDOW, WindowLayer.OVERLAY, WindowLayer.TOP_SUB_VIEW}
    __ALIASES_WITHOUT_MARKERS = {PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
     PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
     PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY,
     PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION,
     VIEW_ALIAS.STYLE_PREVIEW,
     VIEW_ALIAS.VEHICLE_PREVIEW,
     VIEW_ALIAS.HERO_VEHICLE_PREVIEW}
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def __init__(self, settings):
        settings.flags = ViewFlags.VIEW
        super(BaseHangarMarkerView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(BaseHangarMarkerView, self)._onLoading(*args, **kwargs)
        self._updateMarkerVisibility()
        self.__guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def _finalize(self):
        super(BaseHangarMarkerView, self)._finalize()
        self.__guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def _setMarkerVisible(self, value):
        pass

    def _canShowMarkers(self):
        windowsManager = self.__guiLoader.windowsManager
        dispatcher = g_prbLoader.getDispatcher()
        blockedByGameMode = issubclass(type(dispatcher.getEntity()), (MapsTrainingEntity,))
        blockedByWindow = len(windowsManager.findWindows(lambda w: w.layer in self.__LAYERS_WITHOUT_MARKERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)) > 0
        blockedByAlias = len(windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES and isinstance(w, SFWindow) and w.loadParams.viewKey.alias in self.__ALIASES_WITHOUT_MARKERS)) > 0
        return not blockedByWindow and not blockedByAlias and not blockedByGameMode

    def _updateMarkerVisibility(self, *args, **kwargs):
        self._setMarkerVisible(self._canShowMarkers())

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            self._updateMarkerVisibility()
