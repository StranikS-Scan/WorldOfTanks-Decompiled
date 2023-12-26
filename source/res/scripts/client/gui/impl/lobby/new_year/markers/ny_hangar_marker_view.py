# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_hangar_marker_view.py
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import WindowLayer, WindowStatus, ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.impl.lobby.new_year.main_view import MainView
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.pub import ViewImpl
from gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_constants import NYObjects
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from skeletons.new_year import INewYearController
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES

class NyHangarMarkerView(ViewImpl):
    __slots__ = ()
    __guiLoader = dependency.descriptor(IGuiLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _nyController = dependency.descriptor(INewYearController)
    __LAYERS_WITHOUT_MARKERS = {WindowLayer.FULLSCREEN_WINDOW, WindowLayer.OVERLAY, WindowLayer.TOP_SUB_VIEW}
    __ALIASES_WITHOUT_MARKERS = {PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
     PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
     PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY,
     PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION}
    __NY_VIEWS_WITHOUT_MARKERS = {NYObjects.MARKETPLACE}
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def __init__(self, settings):
        settings.flags = ViewFlags.VIEW
        super(NyHangarMarkerView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(NyHangarMarkerView, self)._onLoading(*args, **kwargs)
        self._updateMarkerVisibility()
        self.__guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self._nyController.onStateChanged += self._updateMarkerVisibility
        NewYearNavigation.onObjectStateChanged += self._updateMarkerVisibility

    def _finalize(self):
        super(NyHangarMarkerView, self)._finalize()
        self.__guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self._nyController.onStateChanged -= self._updateMarkerVisibility
        NewYearNavigation.onObjectStateChanged -= self._updateMarkerVisibility

    def _setMarkerVisible(self, value):
        pass

    def _canShowMarkers(self):
        if not self._nyController.isEnabled():
            return False
        windowsManager = self.__guiLoader.windowsManager
        blockedByWindow = len(windowsManager.findWindows(lambda w: w.layer in self.__LAYERS_WITHOUT_MARKERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)) > 0
        blockedByAlias = len(windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES and isinstance(w, SFWindow) and w.loadParams.viewKey.alias in self.__ALIASES_WITHOUT_MARKERS)) > 0
        blockedByNyView = NewYearNavigation.getCurrentObject() in self.__NY_VIEWS_WITHOUT_MARKERS
        mainViewExists = len(windowsManager.findWindows(lambda w: w.windowStatus in self.__ACTIVE_WINDOW_STATUSES and isinstance(w.content, MainView))) > 0
        tutorialState = self._settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE)
        isVisibleForTutorial = tutorialState and tutorialState != TutorialStates.INTRO or not mainViewExists
        return not blockedByWindow and not blockedByAlias and not blockedByNyView and isVisibleForTutorial

    def _updateMarkerVisibility(self, *args, **kwargs):
        self._setMarkerVisible(self._canShowMarkers())

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            self._updateMarkerVisibility()

    def __onSettingsChanged(self, diff):
        if NewYearStorageKeys.TUTORIAL_STATE in diff:
            self._updateMarkerVisibility()
