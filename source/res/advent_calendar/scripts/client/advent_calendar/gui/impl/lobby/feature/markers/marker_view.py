# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/markers/marker_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from advent_calendar.gui.impl.gen.view_models.views.lobby.marker_view_model import MarkerViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorState
from advent_calendar.gui.impl.lobby.feature.markers.base_marker_view import BaseHangarMarkerView
from advent_calendar.gui.impl.lobby.feature.advent_helper import getDoorState
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from CurrentVehicle import g_currentPreviewVehicle

class AdventCalendarMarkerView(BaseHangarMarkerView):
    __adventController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.MarkerView())
        settings.model = MarkerViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdventCalendarMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarMarkerView, self)._onLoading(*args, **kwargs)
        self.__updateMarker()

    def _getEvents(self):
        events = super(AdventCalendarMarkerView, self)._getEvents()
        return events + ((self.__adventController.onDoorOpened, self.__updateMarker), (self.__adventController.onConfigChanged, self.__updateMarker), (g_currentPreviewVehicle.onSelected, self.__onPreviewVehicleSelected))

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            if model.getIsVisible() != isVisible:
                model.setIsVisible(isVisible)
                if isVisible:
                    self.__updateMarker()

    def __updateMarker(self, *args, **kwargs):
        doorsToOpenAmount = self.__getAvailableDoorsToOpenAmount()
        with self.viewModel.transaction() as model:
            model.setIsVisible(doorsToOpenAmount and self.__adventController.isAvailable())
            model.setAvailableDoorsAmount(doorsToOpenAmount)
            model.setIsFirstDay(self.__adventController.getCurrentDayNumber() == 1)

    def __getAvailableDoorsToOpenAmount(self):
        return len([ doorId for doorId in range(0, self.__adventController.config.doorsCount + 1) if getDoorState(doorId + 1) == DoorState.READY_TO_OPEN ])

    def __onPreviewVehicleSelected(self):
        self._setMarkerVisible(g_currentPreviewVehicle.item is None)
        return
