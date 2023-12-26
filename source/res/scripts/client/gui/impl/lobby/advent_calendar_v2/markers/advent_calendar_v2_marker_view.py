# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/markers/advent_calendar_v2_marker_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.markers.advent_calendar_marker_view_model import AdventCalendarMarkerViewModel
from helpers import dependency
from skeletons.gui.game_control import IAdventCalendarV2Controller
from skeletons.new_year import INewYearController, IFriendServiceController
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView

class AdventCalendarMarkerView(NyHangarMarkerView):
    _nyController = dependency.descriptor(INewYearController)
    _friendService = dependency.descriptor(IFriendServiceController)
    _adventCalendarV2Controller = dependency.descriptor(IAdventCalendarV2Controller)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.advent_calendar.markers.AdventCalendarMarker())
        settings.model = AdventCalendarMarkerViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdventCalendarMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(AdventCalendarMarkerView, self)._getEvents()
        return events + ((self._nyController.sacksHelper.onUpdated, self._updateMarkerVisibility),
         (self._friendService.onFriendHangarEnter, self._updateMarkerVisibility),
         (self._friendService.onFriendHangarExit, self._updateMarkerVisibility),
         (self._adventCalendarV2Controller.onDoorOpened, self._updateMarkerVisibility),
         (self._adventCalendarV2Controller.onConfigChanged, self._updateMarkerVisibility))

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            model.setIsVisible(isVisible)
            if isVisible:
                self.__updateMarker()

    def _canShowMarkers(self):
        doorsToOpenAmount = self._adventCalendarV2Controller.getAvailableDoorsToOpenAmount()
        isSelfHangar = not self._friendService.isInFriendHangar
        return isSelfHangar and doorsToOpenAmount and self._adventCalendarV2Controller.isAvailable() and super(AdventCalendarMarkerView, self)._canShowMarkers()

    def __updateMarker(self):
        doorsToOpenAmount = self._adventCalendarV2Controller.getAvailableDoorsToOpenAmount()
        with self.viewModel.transaction() as model:
            model.setAvailableDoorsAmount(doorsToOpenAmount)
            model.setDogSacksAvailable(self._nyController.sacksHelper.getSacksCount() > 0)
            model.setIsPostEvent(self._adventCalendarV2Controller.isInPostActivePhase())
