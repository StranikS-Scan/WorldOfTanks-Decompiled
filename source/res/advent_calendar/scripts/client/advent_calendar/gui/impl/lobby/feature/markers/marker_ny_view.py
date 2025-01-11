# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/markers/marker_ny_view.py
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorState
from advent_calendar.gui.impl.gen.view_models.views.lobby.marker_ny_view_model import MarkerNyViewModel
from advent_calendar.gui.impl.lobby.feature.advent_helper import getDoorState
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView
from helpers import dependency
from new_year.celebrity.celebrity_quests_helpers import getTotalDogSacksCount
from skeletons.new_year import INewYearController, IFriendServiceController

class MarkerNyView(NyHangarMarkerView):
    __nyController = dependency.descriptor(INewYearController)
    __friendService = dependency.descriptor(IFriendServiceController)
    __adventController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.MarkerNyView(), model=MarkerNyViewModel(), args=args, kwargs=kwargs)
        super(MarkerNyView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MarkerNyView, self)._onLoading(*args, **kwargs)
        self.__updateMarker()

    def _getEvents(self):
        events = super(MarkerNyView, self)._getEvents()
        return events + ((self.__nyController.sacksHelper.onUpdated, self.__updateMarker),
         (self.__friendService.onFriendHangarEnter, self.__updateMarker),
         (self.__friendService.onFriendHangarExit, self.__updateMarker),
         (self.__adventController.onDoorOpened, self.__updateMarker),
         (self.__adventController.onConfigChanged, self.__updateMarker))

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            if model.getIsVisible() != isVisible:
                model.setIsVisible(isVisible)
                if isVisible:
                    self.__updateMarker()

    def __updateMarker(self, *args, **kwargs):
        doorsToOpenAmount = self.__getAvailableDoorsToOpenAmount()
        with self.viewModel.transaction() as model:
            model.setIsVisible(self.__isSelfHangar and doorsToOpenAmount and self.__adventController.isAvailable() and self._canShowMarkers())
            model.setAvailableDoorsAmount(doorsToOpenAmount)
            model.setDogSacksAvailable(getTotalDogSacksCount() > 0)
            model.setIsPostEvent(self.__adventController.isInPostActivePhase())

    def __getAvailableDoorsToOpenAmount(self):
        return len([ doorId for doorId in range(0, self.__adventController.config.doorsCount + 1) if getDoorState(doorId + 1) == DoorState.READY_TO_OPEN ])

    @property
    def __isSelfHangar(self):
        return not self.__friendService.isInFriendHangar
