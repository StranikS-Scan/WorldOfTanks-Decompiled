# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_resource_marker_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_resource_marker_model import NyResourceMarkerModel, AnimationState, MarkerType
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NyResourcesEvent
from helpers import dependency, time_utils
from new_year.ny_constants import SyncDataKeys
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_resource_collecting_helper import getAvgResourcesByCollecting, isCollectingAvailable, getCollectingCooldownTime
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, IFriendServiceController
from wg_async import wg_await, delay, wg_async

class NyResourceMarkerView(NyHangarMarkerView):
    __slots__ = ('__lockForCustomAnimation',)
    RESOURCE_NAME = ''
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __friendService = dependency.descriptor(IFriendServiceController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyResourceMarker())
        settings.model = NyResourceMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__lockForCustomAnimation = False
        super(NyResourceMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyResourceMarkerView, self)._onLoading(*args, **kwargs)
        self.viewModel.setResourceType(self.RESOURCE_NAME.value)
        self.__initAnimState()
        self.__updateData()

    def _setMarkerVisible(self, value):
        with self.viewModel.transaction() as model:
            model.setIsVisible(value)

    def _canShowMarkers(self):
        cooldownTime = getCollectingCooldownTime()
        eventEndTimeTill = getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime()
        isInFriendHangar = self.__friendService.isInFriendHangar
        isBestFriend = self.__friendService.friendHangarSpaId in self.__friendService.bestFriendList
        friendCooldown = self.__friendService.getFriendCollectingCooldownTime()
        return super(NyResourceMarkerView, self)._canShowMarkers() and (isBestFriend and friendCooldown < eventEndTimeTill if isInFriendHangar else cooldownTime < eventEndTimeTill)

    def _getEvents(self):
        resHelper = self.__nyController.resourceCollecting
        return super(NyResourceMarkerView, self)._getEvents() + ((self.viewModel.onAnimationEnd, self.__onCollectingAnimationEnd),
         (self.__nyController.onDataUpdated, self.__onDataUpdated),
         (self.__friendService.onFriendHangarEnter, self.__onFriendHangarEnter),
         (self.__friendService.onFriendHangarExit, self.__onFriendHangarExit),
         (self.__friendService.onBestFriendsUpdated, self.__onBestFriendsUpdated),
         (resHelper.onStartCollectingAnim, self.__onCollectingAnimStart),
         (resHelper.onStartCollectingAvailableAnim, self.__onStartCollectingAvailableAnim),
         (resHelper.onCancelCollectingAnim, self.__onCancelCollectingAnim),
         (resHelper.onCollectingUpdateLock, self.__onCollectingUpdateLock))

    def __initAnimState(self):
        self.viewModel.setAnimationState(AnimationState.AVAILABLE if isCollectingAvailable() else AnimationState.DISABLED)

    @wg_async
    def __onCollectingAnimStart(self, resourceName, waitAnim):
        if resourceName != self.RESOURCE_NAME:
            return
        self.viewModel.setAnimationState(AnimationState.COLLECTING)
        if not waitAnim:
            yield wg_await(delay(0.1))
            self.__initAnimState()

    def __onStartCollectingAvailableAnim(self):
        self.viewModel.setAnimationState(AnimationState.AVAILABLE)

    def __onCancelCollectingAnim(self):
        if self.viewModel.getAnimationState() == AnimationState.COLLECTING:
            self.__initAnimState()

    def __onCollectingAnimationEnd(self):
        self.viewModel.setAnimationState(AnimationState.DISABLED)
        self.__updateVisibility()
        g_eventBus.handleEvent(NyResourcesEvent(eventType=NyResourcesEvent.RESOURCE_COLLECTED, ctx={'resource': self.RESOURCE_NAME}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onFriendHangarEnter(self, *_):
        self.__lockForCustomAnimation = False
        self.__updateData()
        self.__initAnimState()

    def __onFriendHangarExit(self, *_):
        self.__lockForCustomAnimation = False
        self.__updateData()
        self.__initAnimState()

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.RESOURCE_COLLECTING in keys and self.__lockForCustomAnimation is False:
            self.__updateData()

    def __onBestFriendsUpdated(self):
        if not self.__lockForCustomAnimation:
            self.__updateVisibility()

    def __onCollectingUpdateLock(self, enable):
        self.__lockForCustomAnimation = enable
        if enable is False:
            self.__updateData()

    def __updateData(self):
        self.__updateVisibility()
        with self.viewModel.transaction() as model:
            if not self.__friendService.isInFriendHangar:
                self.viewModel.setMarkerType(MarkerType.DEFAULT)
            else:
                self.viewModel.setMarkerType(MarkerType.FRIEND)
            model.setCollectAmount(getAvgResourcesByCollecting())

    def __updateVisibility(self):
        self._setMarkerVisible(self._canShowMarkers())


class NyCrystalMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.CRYSTAL


class NyEmeraldMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.EMERALD


class NyAmberMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.AMBER


class NyIronMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.IRON
