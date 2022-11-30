# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/markers/ny_resource_marker_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.markers.ny_resource_marker_model import NyResourceMarkerModel, AnimationState, MarkerType
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.lobby.new_year.markers.ny_hangar_marker_view import NyHangarMarkerView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NyResourcesEvent
from gui.impl.new_year.navigation import NewYearNavigation
from helpers import dependency
from new_year.ny_constants import SyncDataKeys, AdditionalCameraObject
from new_year.ny_resource_collecting_helper import getAvgResourcesByCollecting, isManualCollectingAvailable
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, IFriendServiceController
from wg_async import wg_await, delay, wg_async

class NyResourceMarkerView(NyHangarMarkerView):
    __slots__ = ('__lockForCustomAnimation', '__isAbleToChangeAnimationState')
    RESOURCE_NAME = ''
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __friendService = dependency.descriptor(IFriendServiceController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.markers.NyResourceMarker())
        settings.model = NyResourceMarkerModel()
        settings.flags = ViewFlags.MARKER
        settings.args = args
        settings.kwargs = kwargs
        self.__lockForCustomAnimation = False
        self.__isAbleToChangeAnimationState = True
        super(NyResourceMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NyResourceMarkerView, self)._onLoading(*args, **kwargs)
        self.viewModel.setResourceType(self.RESOURCE_NAME.value)
        self.__initAnimState()
        self.__updateData()

    def _setMarkerVisible(self, value):
        with self.viewModel.transaction() as model:
            model.setIsVisible(value)

    def _getEvents(self):
        resHelper = self.__nyController.resourceCollecting
        return super(NyResourceMarkerView, self)._getEvents() + ((self.viewModel.onAnimationEnd, self.__onCollectingAnimationEnd),
         (self.__nyController.onDataUpdated, self.__onDataUpdated),
         (self.__friendService.onFriendHangarEnter, self.__onFriendHangarEnter),
         (self.__friendService.onFriendHangarExit, self.__onFriendHangarExit),
         (resHelper.onStartCollectingAnim, self.__onCollectingAnimStart),
         (resHelper.onStartCollectingAvailableAnim, self.__onStartCollectingAvailableAnim),
         (resHelper.onCancelCollectingAnim, self.__onCancelCollectingAnim),
         (resHelper.onCollectingUpdateLock, self.__onCollectingUpdateLock),
         (NewYearNavigation.onObjectStateChanged, self._onObjectUpdate))

    def _onObjectUpdate(self):
        self.viewModel.setIsCameraOnResources(AdditionalCameraObject.RESOURCES == NewYearNavigation.getCurrentObject())

    def __initAnimState(self):
        self.viewModel.setAnimationState(AnimationState.AVAILABLE if isManualCollectingAvailable() else AnimationState.DISABLED)

    @wg_async
    def __onCollectingAnimStart(self, resourceName, waitAnim):
        if resourceName != self.RESOURCE_NAME:
            return
        self.__isAbleToChangeAnimationState = True
        self.viewModel.setAnimationState(AnimationState.COLLECTING)
        if not waitAnim:
            yield wg_await(delay(0.1))
            if self.__isAbleToChangeAnimationState:
                self.viewModel.setAnimationState(AnimationState.DISABLED)

    def __onStartCollectingAvailableAnim(self):
        self.viewModel.setAnimationState(AnimationState.AVAILABLE)

    def __onCancelCollectingAnim(self):
        if self.viewModel.getAnimationState() == AnimationState.COLLECTING and self.__isAbleToChangeAnimationState:
            self.viewModel.setAnimationState(AnimationState.DISABLED)

    def __onCollectingAnimationEnd(self):
        self.viewModel.setAnimationState(AnimationState.DISABLED)
        g_eventBus.handleEvent(NyResourcesEvent(eventType=NyResourcesEvent.RESOURCE_COLLECTED, ctx={'resource': self.RESOURCE_NAME}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onFriendHangarEnter(self, *_):
        self.__lockForCustomAnimation = False
        self.__isAbleToChangeAnimationState = False
        self.__updateData()
        self.__initAnimState()

    def __onFriendHangarExit(self, *_):
        self.__lockForCustomAnimation = False
        self.__isAbleToChangeAnimationState = False
        self.__updateData()
        self.__initAnimState()

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.RESOURCE_COLLECTING in keys and self.__lockForCustomAnimation is False:
            self.__updateData()

    def __onCollectingUpdateLock(self, enable):
        self.__lockForCustomAnimation = enable
        if enable is False:
            self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as model:
            if self.__friendService.friendHangarSpaId is None:
                self.viewModel.setMarkerType(MarkerType.DEFAULT)
                isAutoCollectingActivated, _, _ = self.__itemsCache.items.festivity.getResourceCollecting()
                model.setIsAutoCollectActive(isAutoCollectingActivated)
            else:
                self.viewModel.setMarkerType(MarkerType.FRIEND)
                model.setIsAutoCollectActive(False)
            model.setCollectAmount(getAvgResourcesByCollecting())
        return


class NyCrystalMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.CRYSTAL


class NyEmeraldMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.EMERALD


class NyAmberMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.AMBER


class NyIronMarkerView(NyResourceMarkerView):
    RESOURCE_NAME = Resource.IRON
