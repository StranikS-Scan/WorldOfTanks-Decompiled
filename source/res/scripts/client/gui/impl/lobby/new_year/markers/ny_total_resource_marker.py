# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_total_resource_marker.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_total_resource_marker_model import NyTotalResourceMarkerModel, MarkerType
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView
from gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_resource_collecting_helper import getAvgResourcesByCollecting, isCollectingAvailable, getCollectingCooldownTime
from new_year.ny_helper import getNYGeneralConfig
from helpers import dependency, time_utils
from new_year.ny_constants import NYObjects, RESOURCES_ORDER
from skeletons.new_year import IFriendServiceController, INewYearController

class NyTotalResourceMarkerView(NyHangarMarkerView):
    __slots__ = ()
    __friendService = dependency.descriptor(IFriendServiceController)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyTotalResourceMarker())
        settings.model = NyTotalResourceMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyTotalResourceMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyTotalResourceMarkerView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyTotalResourceMarkerView, self)._onLoading(*args, **kwargs)
        self.__updateMarker()

    def _getEvents(self):
        events = super(NyTotalResourceMarkerView, self)._getEvents()
        return events + ((NewYearNavigation.onObjectStateChanged, self.__updateMarker),
         (self.__nyController.resourceCollecting.onSwitchCollectingState, self.__onSwitchCollectingState),
         (self.__friendService.onSwitchFriendCollectingState, self.__onSwitchCollectingState),
         (self.__friendService.onFriendHangarEnter, self.__onFriendHangar),
         (self.__friendService.onFriendHangarExit, self.__onFriendHangar),
         (self.__friendService.onBestFriendsUpdated, self.__onFriendHangar))

    def __updateMarker(self):
        with self.viewModel.transaction() as model:
            model.setAmount(getAvgResourcesByCollecting() * len(RESOURCES_ORDER))
            model.setMarkerType(MarkerType.FRIEND if self.__friendService.isInFriendHangar else MarkerType.DEFAULT)
            model.setIsDisabled(not isCollectingAvailable())

    def _canShowMarkers(self):
        cooldownTime = getCollectingCooldownTime()
        eventEndTimeTill = getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime()
        isInFriendHangar = self.__friendService.isInFriendHangar
        isBestFriend = self.__friendService.friendHangarSpaId in self.__friendService.bestFriendList
        friendCooldown = self.__friendService.getFriendCollectingCooldownTime()
        return super(NyTotalResourceMarkerView, self)._canShowMarkers() and (isBestFriend and friendCooldown < eventEndTimeTill if isInFriendHangar else cooldownTime < eventEndTimeTill)

    def _setMarkerVisible(self, value):
        with self.viewModel.transaction() as model:
            model.setIsVisible(value and NewYearNavigation.getCurrentObject() != NYObjects.RESOURCES)

    def __onSwitchCollectingState(self, _):
        self.__updateMarker()

    def __onFriendHangar(self, *_):
        self.__updateMarker()
