# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/markers/grinch_progression_marker.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from grinch_progression.gui.impl.gen.view_models.views.lobby.markers.grinch_progression_marker_model import GrinchProgressionMarkerModel, MarkerState
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from grinch.skeletons.battle_controller import IGrinchController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView
from grinch_progression_common.grinch_progression_constants import ProgressionStates
from skeletons.new_year import IFriendServiceController
from gui.impl.new_year.navigation import NewYearNavigation
MAX_SYNC_INITIATOR = 1000

class GrinchProgressionMarker(NyHangarMarkerView):
    __slots__ = ('__syncInitiator',)
    __gpController = dependency.descriptor(IGrinchProgressionController)
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __friendService = dependency.descriptor(IFriendServiceController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.grinch_progression.lobby.markers.GrinchProgressionMarker())
        settings.model = GrinchProgressionMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__syncInitiator = 0
        super(GrinchProgressionMarker, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isLobbyMode(self):
        return NewYearNavigation.getCurrentObject() is None

    def _onLoading(self, *args, **kwargs):
        super(GrinchProgressionMarker, self)._onLoading(*args, **kwargs)
        if self.__hangarSpace.spaceInited:
            self.__updateMarker()

    def _getEvents(self):
        return ((self.__gpController.onDataUpdated, self.__updateMarker),
         (self.__hangarSpace.onSpaceCreate, self._updateMarkerVisibility),
         (self.__friendService.onFriendHangarEnter, self._updateMarkerVisibility),
         (self.__friendService.onFriendHangarExit, self._updateMarkerVisibility),
         (NewYearNavigation.onObjectStateChanged, self.__onObjectStateChanged),
         (self.__eventsCache.onSyncCompleted, self.__updateMarker),
         (self.__grinchCtrl.onConfigChanged, self.__updateVisibility))

    def _finalize(self):
        self.__syncInitiator = None
        super(GrinchProgressionMarker, self)._finalize()
        return

    def __updateVisibility(self, diff):
        with self.viewModel.transaction() as model:
            model.setIsVisible(self.__grinchCtrl.isEnabled())

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            newValue = isVisible and self.__hangarSpace.spaceInited and not self.__friendService.isInFriendHangar
            if model.getIsVisible() != newValue:
                model.setIsVisible(newValue)
                if newValue:
                    self.__updateMarker()

    def __updateMarker(self, *args, **kwargs):
        points = self.__gpController.getPoints()
        previousPoints = self.__gpController.getPreviousPointsCount()
        progressionState = self.__gpController.getProgressionState()
        with self.viewModel.transaction() as model:
            model.setPoints(points)
            model.setPrevPoints(previousPoints)
            model.setCountdown(self.__getTimeTill(progressionState))
            model.setEnoughForClaimReward(self.__gpController.enoughForClaimReward)
            model.setMarkerState(self.__getMarkerState(progressionState))
            model.setIsVisible(self.__hangarSpace.spaceInited and not self.__friendService.isInFriendHangar and self.__grinchCtrl.isEnabled())
        if previousPoints != points:
            self.__gpController.setPreviousPointsCount(points)

    def __getTimeTill(self, progressionState):
        return self.__gpController.getTimeTillNextBattlesStart()

    def __getMarkerState(self, progressionState):
        if progressionState == ProgressionStates.IN_PROGRESS:
            return MarkerState.ACTIVE
        if progressionState == ProgressionStates.OFF_CHAPTER:
            return MarkerState.PAUSED
        return MarkerState.DONE if progressionState == ProgressionStates.FINISHED else MarkerState.LOCK

    def __onObjectStateChanged(self):
        with self.viewModel.transaction() as model:
            if self.isLobbyMode:
                if self.__syncInitiator >= MAX_SYNC_INITIATOR:
                    self.__syncInitiator = 0
                else:
                    self.__syncInitiator += 1
                model.setSyncInitiator(self.__syncInitiator)
