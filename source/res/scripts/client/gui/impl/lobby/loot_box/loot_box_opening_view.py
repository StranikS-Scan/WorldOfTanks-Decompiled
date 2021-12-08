# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_opening_view.py
import logging
import Windowing
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_opening_model import LootBoxOpeningModel
from gui.impl.lobby.loot_box.loot_box_helper import LootBoxHideableView
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideosSpecialRewardType
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideos, playSound, LootBoxViewEvents
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)
_VIDEO_BUFFER_TIME = 1

class LootBoxOpeningView(LootBoxHideableView):
    settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('__boxItem', '__specialRewardType', '__videoStartStopHandler')

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.loot_box.views.loot_box_opening_view.LootBoxOpeningView(), flags=ViewFlags.NON_REARRANGE_VIEW, model=LootBoxOpeningModel())
        super(LootBoxOpeningView, self).__init__(settings)
        self.__boxItem = None
        self.__specialRewardType = None
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler()
        return

    @property
    def viewModel(self):
        return super(LootBoxOpeningView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxOpeningView, self)._initialize()
        self.viewModel.onOpeningStart += self.__onOpeningStart
        self.viewModel.onOpeningEnd += self.__onOpeningEnd
        self.viewModel.onReloadEnd += self.__onReloadEnd
        self.viewModel.onNeedShowRewards += self.__onNeedShowRewards
        self.viewModel.onVideoOffViewReady += self.__onVideoOffViewReady
        self.viewModel.onLoadError += self.__onLoadError
        self.settingsCore.onSettingsChanged += self.__updateVideoOff
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        g_eventBus.addListener(events.LootboxesEvent.ON_OPEN_LOOTBOX, self.__onOpenNextBox, scope=EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self, *args, **kwargs):
        super(LootBoxOpeningView, self)._onLoading()
        isVideoOff = self.settingsCore.getSetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF)
        self.viewModel.setIsVideoOff(isVideoOff)

    def _finalize(self):
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.viewModel.onLoadError -= self.__onLoadError
        self.viewModel.onOpeningStart -= self.__onOpeningStart
        self.viewModel.onOpeningEnd -= self.__onOpeningEnd
        self.viewModel.onReloadEnd -= self.__onReloadEnd
        self.viewModel.onNeedShowRewards -= self.__onNeedShowRewards
        self.viewModel.onVideoOffViewReady -= self.__onVideoOffViewReady
        self.settingsCore.onSettingsChanged -= self.__updateVideoOff
        self.__videoStartStopHandler.onVideoDone()
        self.__videoStartStopHandler = None
        g_eventBus.removeListener(events.LootboxesEvent.ON_OPEN_LOOTBOX, self.__onOpenNextBox, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxOpeningView, self)._finalize()
        return

    def __onOpeningStart(self):
        if self.__boxItem is None:
            _logger.error('Failed to handle lootbox opening video start. Missing lootbox item.')
            return
        else:
            self.__playOpeningSound()
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_OPENING_START), EVENT_BUS_SCOPE.LOBBY)
            return

    def __onLoadError(self):
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_VIDEO_LOAD_ERROR), EVENT_BUS_SCOPE.LOBBY)

    def __playOpeningSound(self):
        if self.__boxItem.isFree():
            sourceID = self.__boxItem.getType()
        else:
            rewardType = self.__specialRewardType
            rewardType = LootBoxVideosSpecialRewardType.GIFT if rewardType else LootBoxVideosSpecialRewardType.COMMON
            sourceID = '{boxType}_{rewardType}_{boxCategory}'.format(boxType=self.__boxItem.getType(), rewardType=rewardType, boxCategory=self.__boxItem.getCategory())
        self.__videoStartStopHandler.onVideoStart(LootBoxVideos.OPEN_BOX, sourceID)

    def __onOpeningEnd(self):
        self.viewModel.setIsOpening(False)
        self.__videoStartStopHandler.onVideoDone()
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_OPENING_END), EVENT_BUS_SCOPE.LOBBY)

    def __onNeedShowRewards(self):
        self.__videoStartStopHandler.onVideoDone()
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.NEED_SHOW_REWARDS), EVENT_BUS_SCOPE.LOBBY)

    def __onVideoOffViewReady(self):
        if not self._isMemoryRiskySystem:
            return
        self.viewModel.onVideoOffViewReady -= self.__onVideoOffViewReady
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_VIDEO_OFF_MOVIE_LOADED), EVENT_BUS_SCOPE.LOBBY)

    def __onReloadEnd(self):
        self.viewModel.setIsReloading(False)
        self.viewModel.setIsOpening(True)

    def __onOpenNextBox(self, event):
        ctx = event.ctx
        self.__boxItem = ctx['boxItem']
        self.__specialRewardType = ctx['specialRewardType']
        withReload = ctx['withReload']
        isForcedToEnd = ctx['isForcedToEnd']
        with self.viewModel.transaction() as tx:
            tx.setIsForcedToEnd(isForcedToEnd)
            tx.setBoxCategory(self.__boxItem.getCategory())
            tx.setIsFreeBox(self.__boxItem.isFree())
            tx.setSpecialRewardType(self.__specialRewardType)
            tx.setIsVideoOff(self.settingsCore.getSetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF))
            tx.setStreamBufferLength(_VIDEO_BUFFER_TIME)
        isVideoOff = self.viewModel.getIsVideoOff()
        self.viewModel.setIsOpening(not withReload and not isVideoOff and not isForcedToEnd)
        self.viewModel.setIsReloading(withReload and not isVideoOff and not isForcedToEnd)
        if withReload:
            playSound(LootBoxViewEvents.LOGISTIC_CENTER_NEXT)

    def __updateVideoOff(self, diff):
        if NewYearStorageKeys.LOOT_BOX_VIDEO_OFF in diff:
            isVideoOff = diff[NewYearStorageKeys.LOOT_BOX_VIDEO_OFF]
            self.viewModel.setIsVideoOff(isVideoOff)

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        self.__videoStartStopHandler.setIsNeedPause(not isWindowAccessible)
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def canBeClosed(self):
        return False


class LootBoxOpeningWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(LootBoxOpeningWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxOpeningView(), parent=parent, layer=WindowLayer.TOP_WINDOW)
