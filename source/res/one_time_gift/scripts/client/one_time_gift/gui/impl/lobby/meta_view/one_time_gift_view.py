# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/meta_view/one_time_gift_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from skeletons.gui.app_loader import IAppLoader
from one_time_gift.gui.gui_constants import OTG_LOCK_SOURCE_NAME
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews, OneTimeGiftViewModel
from one_time_gift.gui.impl.lobby.awards.additional_rewards_view import AdditionalRewardsView
from one_time_gift.gui.impl.lobby.awards.bonus_vehicles_reward import BonusVehiclesRewardView
from one_time_gift.gui.impl.lobby.awards.branch_reward_view import BranchRewardView
from one_time_gift.gui.impl.lobby.awards.collectors_compensation_view import CollectorsCompensationView
from one_time_gift.gui.impl.lobby.branch_selection_view import BranchSelectionView
from one_time_gift.gui.impl.lobby.intro_view import IntroView
from one_time_gift.gui.one_time_gift_sounds import ONE_TIME_GIFT_OVERLAY_SOUND_SPACE
from one_time_gift.gui.shared.lock_overlays import lockAchievementsEarning, lockEliteWindows, lockSteamShade
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
if typing.TYPE_CHECKING:
    from typing import Optional

class OneTimeGiftView(ViewImpl):
    _COMMON_SOUND_SPACE = ONE_TIME_GIFT_OVERLAY_SOUND_SPACE
    __oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, viewId, *args, **kwargs):
        settings = ViewSettings(R.views.one_time_gift.mono.lobby.one_time_gift_view())
        settings.flags = ViewFlags.VIEW
        settings.model = OneTimeGiftViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__subViews = None
        self.__currentSubView = None
        self.__viewId = viewId
        super(OneTimeGiftView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(OneTimeGiftView, self).getViewModel()

    def switchContent(self, viewType, *args, **kwargs):
        if self.__currentSubView is not None and self.__currentSubView.isLoaded:
            if self.__viewId != viewType:
                self.__currentSubView.finalize()
                self.__currentSubView = self.__subViews[MainViews(viewType)]
                self.__viewId = viewType
        self.__updateSubView(*args, **kwargs)
        return

    def createToolTip(self, event):
        tooltip = None
        if self.__currentSubView and self.__currentSubView.isLoaded:
            tooltip = self.__currentSubView.createToolTip(event)
        return tooltip or super(OneTimeGiftView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        content = None
        if self.__currentSubView.isLoaded:
            content = self.__currentSubView.createToolTipContent(event, contentID)
        return content or super(OneTimeGiftView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(OneTimeGiftView, self)._onLoading(*args, **kwargs)
        lockNotificationManager(True, OTG_LOCK_SOURCE_NAME)
        lockAchievementsEarning(True)
        lockEliteWindows(True)
        g_messengerEvents.onLockPopUpMessages(OTG_LOCK_SOURCE_NAME, lockHigh=True, useQueue=False)
        self.__createSubViews()
        self.__currentSubView = self.__subViews[self.__viewId]
        self.__updateSubView(*args, **kwargs)

    def _finalize(self):
        self.__closeNotificationCenter()
        self.__currentSubView = None
        self.__clearSubViews()
        lockEliteWindows(False)
        lockAchievementsEarning(False)
        lockSteamShade(False)
        lockNotificationManager(False, OTG_LOCK_SOURCE_NAME, releasePostponed=True, fireReleased=False)
        g_messengerEvents.onUnlockPopUpMessages(OTG_LOCK_SOURCE_NAME)
        self.__oneTimeGiftController.onEntryPointUpdated()
        super(OneTimeGiftView, self)._finalize()
        return

    def __createSubViews(self):
        subViews = (IntroView(self.viewModel.introModel, self),
         BranchSelectionView(self.viewModel.branchSelectionModel, self),
         BranchRewardView(self.viewModel.rewardModel, self),
         CollectorsCompensationView(self.viewModel.rewardModel, self),
         BonusVehiclesRewardView(self.viewModel.rewardModel, self),
         AdditionalRewardsView(self.viewModel.rewardModel, self))
        self.__subViews = {sv.viewId:sv for sv in subViews}

    def __clearSubViews(self):
        if self.__subViews is None:
            return
        else:
            for subView in self.__subViews.values():
                if subView is not None and subView.isLoaded:
                    subView.finalize()

            self.__subViews.clear()
            return

    def __closeNotificationCenter(self):
        app = self.__appLoader.getApp()
        if app is None:
            return
        else:
            notificationsView = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.NOTIFICATIONS_LIST))
            if notificationsView is not None:
                window = notificationsView.getParentWindow()
                if window is not None:
                    window.destroy()
            return

    def __updateSubView(self, *args, **kwargs):
        try:
            with self.viewModel.transaction() as vm:
                vm.setViewType(self.__currentSubView.viewId)
            self.__currentSubView.initialize(*args, **kwargs)
        except Exception:
            self.__oneTimeGiftController.onViewError()
            raise


class OneTimeGiftViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, viewId=MainViews.INTRO, *args, **kwargs):
        super(OneTimeGiftViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.WINDOW, content=OneTimeGiftView(viewId, *args, **kwargs))
