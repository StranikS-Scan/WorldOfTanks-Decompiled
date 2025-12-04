# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/lootbox_video_reward_view.py
import Windowing
import logging
from gui.impl.lobby.video.video_sound_manager import DummySoundManager
from gui.impl.gen import R
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.reward_video_model import RewardVideoModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_config import REWARD_VIDEO_CONFIG
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_REWARD_VIDEO_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardsView
from helpers import dependency
from frameworks.wulf import WindowFlags, WindowLayer
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_video_reward_view_model import LootboxVideoRewardViewModel
from gui.impl.pub.lobby_window import LobbyWindow
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
_logger = logging.getLogger(__name__)

def isValidVideoConfig(videoConfig):
    if not videoConfig.keys():
        _logger.error('Empty video config')
        return False
    for category in videoConfig:
        if not videoConfig[category].keys():
            _logger.error('Empty video config for category: %s', category)
            return False
        for rewardType in videoConfig[category]:
            if not videoConfig[category][rewardType].keys():
                _logger.error('Empty video config for reward type: %s, category: %s', rewardType, category)
                return False
            if not videoConfig[category][rewardType]['videos']:
                _logger.error('Empty video list for reward type: %s, category: %s', rewardType, category)
                return False
            for video in videoConfig[category][rewardType]['videos']:
                if not video.keys():
                    _logger.error('Wrong video settings for reward type: %s, category: %s', rewardType, category)
                    return False
                if 'duration' not in video:
                    _logger.error('No field [duration] for reward type: %s, category: %s', rewardType, category)
                    return False
                if 'videoResName' not in video:
                    _logger.error('No field [videoResName] for reward type: %s, category: %s', rewardType, category)
                    return False

    return True


def packVideoRewardConfig(lootboxCategory, videoRes, videoRewardConfig):
    videos = []
    for videoConfig in videoRewardConfig:
        video = {}
        if videoConfig['videoResName'] is not None:
            video['videoResName'] = R.videos.lootbox_reward_video.dyn(lootboxCategory).dyn(videoConfig['videoResName'])()
        else:
            video['videoResName'] = R.videos.lootbox_reward_video.dyn(lootboxCategory).dyn(videoRes)()
        if 'showFooterTiming' in videoConfig:
            video['showFooterTiming'] = videoConfig['showFooterTiming']
        else:
            video['showFooterTiming'] = 0
        video['duration'] = videoConfig['duration']
        videos.append(video)

    return videos


class LootboxVideoRewardView(BaseUniqueRewardsView):
    __slots__ = ('_bonus', '_soundControl', '__isWindowAccessibleHandlerInit', '_videoRes', '_isGuaranteedReward', '_videoConfig', '_lootbox', '__soundStarted')
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = LOOT_BOXES_REWARD_VIDEO_SOUND_SPACE

    def __init__(self, layoutID, bonus, videoRes, rewards, isGuaranteedReward=False, soundControl=DummySoundManager(), videoConfig=None, lootbox=None):
        super(LootboxVideoRewardView, self).__init__(layoutID, rewards, LootboxVideoRewardViewModel())
        self._bonus = bonus
        self._soundControl = soundControl
        self._videoRes = videoRes
        self._isGuaranteedReward = isGuaranteedReward
        self.__isWindowAccessibleHandlerInit = False
        self._videoConfig = None
        self._lootbox = lootbox
        self.__soundStarted = False
        if isValidVideoConfig(REWARD_VIDEO_CONFIG):
            self._videoConfig = REWARD_VIDEO_CONFIG
        else:
            _logger.error('Invalid REWARD_VIDEO_CONFIG')
        if videoConfig is not None and isValidVideoConfig(videoConfig):
            self._updateVideoConfig(videoConfig)
        return

    def _finalize(self):
        if self.__isWindowAccessibleHandlerInit:
            Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
            self.__isWindowAccessibleHandlerInit = False
        self.__soundStarted = False
        self._soundControl.stop()
        super(LootboxVideoRewardView, self)._finalize()

    def _updateVideoConfig(self, videoConfig):
        self._videoConfig.update(videoConfig)

    @property
    def viewModel(self):
        return super(LootboxVideoRewardView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LootboxVideoRewardView, self)._onLoading(*args, **kwargs)
        self._update()
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
        self.__isWindowAccessibleHandlerInit = True

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onVideoStarted, self._onVideoStarted))

    def _update(self):
        with self.viewModel.transaction() as vm:
            vm.setIsWindowAccessible(Windowing.isWindowAccessible())
            if self._bonus.getName() == 'vehicles':
                vehicle = self._bonus.getVehicles()[0][0]
                vm.setIsElite(vehicle.isElite)
                vm.setVehicleType(vehicle.type)
                vm.setVehicleLvl(vehicle.level)
            vm.setVideoRes(self._videoRes)
            vm.setIsGuaranteedReward(self._isGuaranteedReward)
            vm.reward.clearItems()
            packBonusModelAndTooltipData([self._bonus], vm.reward)
            vm.reward.invalidate()
            vm.setLootboxType(self._lootbox.getType())
            vm.setLootboxID(self._lootbox.getID())
            if self._videoConfig is not None:
                videoHasFooter = self._videoConfig[self._getVideoConfigKey()][self._bonus.getName()]['hasFooter']
                vm.setHasVideoFooter(videoHasFooter)
                rewardVideos = vm.getRewardVideos()
                rewardVideos.clear()
                for videoConfig in packVideoRewardConfig(self._getVideoConfigKey(), self._videoRes, self._videoConfig[self._getVideoConfigKey()][self._bonus.getName()]['videos']):
                    rewardVideoConfig = RewardVideoModel()
                    rewardVideoConfig.setVideoResName(videoConfig['videoResName'])
                    rewardVideoConfig.setDuration(videoConfig['duration'])
                    rewardVideoConfig.setShowFooterTiming(videoConfig['showFooterTiming'])
                    rewardVideos.addViewModel(rewardVideoConfig)

                rewardVideos.invalidate()
            else:
                vm.setHasVideoFooter(False)
                rewardVideos = vm.getRewardVideos()
                rewardVideos.clear()
                rewardVideos.invalidate()
                _logger.error('Invalid video config')
        return

    def _getVideoConfigKey(self):
        return self._lootbox.getCategory()

    def _onClose(self):
        self.destroyWindow()

    def _onVideoStarted(self):
        self._startVideoSound()
        if not Windowing.isWindowAccessible():
            self._soundControl.pause()

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            if self.__soundStarted:
                self._soundControl.unpause()
            else:
                self._startVideoSound()
        else:
            self._soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def _startVideoSound(self):
        self.__soundStarted = True
        self._soundControl.start()


class LootboxVideoRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, contentView, parent=None):
        super(LootboxVideoRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=contentView, parent=parent, layer=WindowLayer.OVERLAY)
