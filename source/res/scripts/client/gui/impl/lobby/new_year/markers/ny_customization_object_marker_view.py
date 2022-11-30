# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_customization_object_marker_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_customization_object_marker_model import NyCustomizationObjectMarkerModel, MarkerType
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView
from gui.impl.new_year.navigation import NewYearNavigation
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from helpers import dependency
from items.components.ny_constants import ObjectsWithMarkers
from new_year.ny_constants import UPGRADABLE_OBJECTS, GLADE_OBJECTS, SyncDataKeys, AdditionalCameraObject
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import INewYearController, IFriendServiceController

class NyCustomizationObjectMarkerView(NyHangarMarkerView):
    __slots__ = ()
    _nyController = dependency.descriptor(INewYearController)
    _friendService = dependency.descriptor(IFriendServiceController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _OBJECT_TYPE = None

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyCustomizationObjectMarker())
        settings.model = NyCustomizationObjectMarkerModel()
        settings.flags = ViewFlags.MARKER
        settings.args = args
        settings.kwargs = kwargs
        super(NyCustomizationObjectMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(NyCustomizationObjectMarkerView, self)._getEvents()
        return events + ((self._settingsCore.onSettingsChanged, self._onSettingsChanged),
         (self._nyController.onDataUpdated, self._onDataUpdated),
         (self._friendService.onFriendHangarEnter, self._updateMarker),
         (self._friendService.onFriendHangarExit, self._updateMarker),
         (NewYearNavigation.onObjectStateChanged, self._onObjectUpdate))

    def _onLoading(self, *args, **kwargs):
        super(NyCustomizationObjectMarkerView, self)._onLoading(*args, **kwargs)
        self._updateMarker()
        self.viewModel.setTutorialState(self._settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE, TutorialStates.INTRO))

    def _onObjectUpdate(self):
        self.viewModel.setIsAbleForUpgrade(NewYearNavigation.getCurrentObject() in GLADE_OBJECTS)
        if self.viewModel.getTutorialState() > TutorialStates.WIDGET:
            return
        isUnderSpece = NewYearNavigation.getCurrentObject() == AdditionalCameraObject.UNDER_SPACE
        self.viewModel.setIsCameraOnUnderSpace(isUnderSpece)

    def __ableForUpgrade(self):
        self.viewModel.setIsAbleForUpgrade(True)

    def _onDataUpdated(self, keys, _):
        checkKeys = {SyncDataKeys.OBJECTS_LEVELS}
        if set(keys) & checkKeys and not self._friendService.friendHangarSpaId:
            self._updateMarker()

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            model.setIsVisible(isVisible)
        if isVisible:
            self._updateMarker()

    def _updateMarker(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setObjectType(self._OBJECT_TYPE)
            if self._OBJECT_TYPE in UPGRADABLE_OBJECTS:
                currentLevel = self._nyController.customizationObjects.getLevel(self._OBJECT_TYPE)
                model.setCurrentLevel(currentLevel)
                model.setIsUpgradable(True)
            model.setMarkerType(MarkerType.DEFAULT if self._friendService.friendHangarSpaId is None else MarkerType.FRIEND)
        return

    def _onSettingsChanged(self, diff):
        if NewYearStorageKeys.TUTORIAL_STATE in diff:
            self.viewModel.setTutorialState(diff[NewYearStorageKeys.TUTORIAL_STATE])


class NyFirMarkerView(NyCustomizationObjectMarkerView):
    _OBJECT_TYPE = ObjectsWithMarkers.FIR


class NyFairMarkerView(NyCustomizationObjectMarkerView):
    _OBJECT_TYPE = ObjectsWithMarkers.FAIR


class NyInstallationMarkerView(NyCustomizationObjectMarkerView):
    _OBJECT_TYPE = ObjectsWithMarkers.INSTALLATION


class NyHeadquartersMarkerView(NyCustomizationObjectMarkerView):
    _OBJECT_TYPE = ObjectsWithMarkers.HEADQUARTERS
