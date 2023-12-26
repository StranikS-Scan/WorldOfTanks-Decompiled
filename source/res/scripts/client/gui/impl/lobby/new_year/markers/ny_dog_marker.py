# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_dog_marker.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_dog_marker_model import NyDogMarkerModel
from helpers import dependency
from skeletons.new_year import INewYearController, IFriendServiceController
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView

class NyDogMarker(NyHangarMarkerView):
    _nyController = dependency.descriptor(INewYearController)
    _friendService = dependency.descriptor(IFriendServiceController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyDogMarker())
        settings.model = NyDogMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyDogMarker, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyDogMarker, self)._onLoading(*args, **kwargs)
        self.__updateMarker()

    def _getEvents(self):
        events = super(NyDogMarker, self)._getEvents()
        return events + ((self._nyController.sacksHelper.onUpdated, self.__onDataUpdated), (self._friendService.onFriendHangarEnter, self.__updateMarker), (self._friendService.onFriendHangarExit, self.__updateMarker))

    def __onDataUpdated(self):
        if self.__isSelfHangar:
            self.__updateMarker()

    def __updateMarker(self, *args, **kwargs):
        sacksCount = self._nyController.sacksHelper.getSacksCount()
        with self.viewModel.transaction() as model:
            model.setIsVisible(self.__isSelfHangar and sacksCount > 0)
            model.setSacksCount(sacksCount)

    @property
    def __isSelfHangar(self):
        return self._friendService.friendHangarSpaId is None
