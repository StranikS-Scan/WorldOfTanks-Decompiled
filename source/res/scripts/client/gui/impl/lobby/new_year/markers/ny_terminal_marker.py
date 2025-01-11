# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_terminal_marker.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_terminal_marker_model import NyTerminalMarkerModel
from helpers import dependency
from new_year.ny_constants import MAX_TOKENS_DISPLAYED
from skeletons.new_year import INewYearController, IFriendServiceController
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView

class NyTerminalMarker(NyHangarMarkerView):
    _nyController = dependency.descriptor(INewYearController)
    _friendService = dependency.descriptor(IFriendServiceController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyTerminalMarker())
        settings.model = NyTerminalMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyTerminalMarker, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyTerminalMarker, self)._onLoading(*args, **kwargs)
        self.__onDataUpdated()

    def _getEvents(self):
        events = super(NyTerminalMarker, self)._getEvents()
        return events + ((self._nyController.currencies.onNyCoinsUpdate, self.__onDataUpdated), (self._friendService.onFriendHangarEnter, self._updateMarkerVisibility), (self._friendService.onFriendHangarExit, self._updateMarkerVisibility))

    def _canShowMarkers(self):
        isFriendHangar = self._friendService.isInFriendHangar
        return not isFriendHangar and super(NyTerminalMarker, self)._canShowMarkers()

    def __onDataUpdated(self):
        self._updateMarkerVisibility()

    def _updateMarkerVisibility(self, *args, **kwargs):
        count = self._nyController.currencies.getCoinsCount()
        with self.viewModel.transaction() as model:
            model.setIsVisible(count > 0 and self._canShowMarkers())
            model.setCount(MAX_TOKENS_DISPLAYED if count > MAX_TOKENS_DISPLAYED else count)
