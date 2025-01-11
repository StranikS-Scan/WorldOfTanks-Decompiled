# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_headquarters_marker_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_headquarters_marker_model import NyHeadquartersMarkerModel
from skeletons.gui.shared.utils import IHangarSpace
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import LevelState
from helpers import dependency
from new_year.celebrity.celebrity_quests_helpers import getTotalDogSacksCount
from new_year.ny_constants import GuestsQuestsTokens
from gui.impl.new_year.navigation import NewYearNavigation
from skeletons.new_year import INewYearController, IFriendServiceController, ICelebrityController, ICelebritySceneController
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView

class NyHeadquartersMarkerView(NyHangarMarkerView):
    __slots__ = ('__isAnimationEnd', '__wasHiddenOnLobby', '__needResetAnimation')
    _nyController = dependency.descriptor(INewYearController)
    _friendService = dependency.descriptor(IFriendServiceController)
    __celebrityController = dependency.descriptor(ICelebrityController)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyHeadquartersMarker())
        settings.model = NyHeadquartersMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__isAnimationEnd = False
        self.__wasHiddenOnLobby = False
        self.__needResetAnimation = False
        super(NyHeadquartersMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyHeadquartersMarkerView, self)._onLoading(*args, **kwargs)
        self.__updateMarker()

    def _getEvents(self):
        events = super(NyHeadquartersMarkerView, self)._getEvents()
        return events + ((self._nyController.sacksHelper.onUpdated, self.__onDataUpdated),
         (self._nyController.onStateChanged, self.__onDataUpdated),
         (self._friendService.onFriendHangarEnter, self.__updateMarker),
         (self._friendService.onFriendHangarExit, self.__updateMarker),
         (NewYearNavigation.onObjectStateChanged, self.__onObjectStateChanged),
         (self.__hangarSpace.onSpaceCreate, self.__onHangarSpaceCreated),
         (self.viewModel.onAnimationEnd, self.__onAnimationEnd))

    def __onHangarSpaceCreated(self):
        self.viewModel.setIsHangarReady(True)

    def _onShown(self):
        if self.isLobbyMode:
            self.__wasHiddenOnLobby = False

    def _onHidden(self):
        if self.isLobbyMode:
            self.__wasHiddenOnLobby = True

    def __onAnimationEnd(self):
        self.__isAnimationEnd = True
        if self.__needResetAnimation:
            self.__needResetAnimation = False
            self.viewModel.setSyncInitiator(self.viewModel.getSyncInitiator() + 1)

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            if model.getIsVisible() != isVisible:
                model.setIsVisible(isVisible)
                if isVisible:
                    self.__updateMarker()

    def __onDataUpdated(self):
        if not self._friendService.friendHangarSpaId:
            self.__updateMarker()

    def __updateMarker(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setSacksCount(getTotalDogSacksCount())
            model.setIsLobby(self.isLobbyMode)
            model.setLevelState(self.__getLevelState())
            model.setIsFriendHangar(self._friendService.friendHangarSpaId is not None)
        return

    def __onObjectStateChanged(self):
        with self.viewModel.transaction() as model:
            if self.isLobbyMode:
                self.__isAnimationEnd = False
                model.setSyncInitiator(self.viewModel.getSyncInitiator() + 1)
            elif self.__wasHiddenOnLobby and not self.__isAnimationEnd:
                self.__needResetAnimation = True
            model.setIsLobby(self.isLobbyMode)

    @property
    def isLobbyMode(self):
        return NewYearNavigation.getCurrentObject() is None

    def __getLevelState(self):
        isChallengeCompleted = self.__celebritySceneController.isChallengeCompleted
        if isChallengeCompleted:
            guests = (GuestsQuestsTokens.GUEST_A,)
            if self._nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_CAT):
                guests += (GuestsQuestsTokens.GUEST_C,)
            if self.__celebrityController.isGuestQuestsCompletedFully(guests):
                return LevelState.ZERO.value
        return LevelState.DEFAULT.value
