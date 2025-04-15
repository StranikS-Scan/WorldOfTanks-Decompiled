# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/cosmic_lootbox_video/unique_reward_handler.py
import typing
from typing import Dict, Iterable, Optional, Type
from collections import namedtuple
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getNationLessName
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVehicleVideoRewardView, LootboxVideoRewardWindow
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from constants import LOOTBOX_TOKEN_PREFIX
from gui.impl.lobby.video.video_view import VideoViewWindow
from cosmic_constants import COSMIC_LOOTBOX_CATEGORY_25
from cosmic_event.gui.sound_control.sound_control import VideoRewardsSoundControl
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window

def getVideoResForVehicle(vehicle):
    return getNationLessName(vehicle.name).replace('-', '_')


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getOpenedLootBoxFromRewards(rewards, itemsCache=None):
    return first((itemsCache.items.tokens.getLootBoxByTokenID(tID) for tID, tData in rewards.get('tokens', {}).iteritems() if tID.startswith(LOOTBOX_TOKEN_PREFIX) and tData.get('count', 0) < 0))


def getVideoExists(videoRes):
    resId = R.videos.cosmic.reward_vehicle.dyn(videoRes)
    return resId.exists()


def isGuaranteedReward(limitName, usedLimits):
    return usedLimits is not None and limitName in usedLimits


VideoRewardData = namedtuple('_VideoRewardData', ('vehicle', 'video', 'isGuaranteed'))

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processVehicles(rewardsData, vehiclesList, isGuaranteed, itemsCache=None):
    for vehiclesDict in vehiclesList:
        for venIntCD, vehicleData in vehiclesDict.iteritems():
            if {'rentCompensation', 'customCompensation'}.isdisjoint(vehicleData):
                vehicle = itemsCache.items.getItemByCD(venIntCD)
                video = getVideoResForVehicle(vehicle)
                if getVideoExists(video):
                    rewardsData['CosmicRewardsData'].append(VideoRewardData(vehicle, video, isGuaranteed))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueCosmicRewardsData(resultData, itemsCache=None):
    rewardsData = {'CosmicRewardsData': []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is not None and openedLootbox.getCategory() in COSMIC_LOOTBOX_CATEGORY_25:
            isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
            processVehicles(rewardsData, rewards.get('vehicles', []), isGuaranteed)

    return rewardsData


class CosmicVideoReward(LootboxVehicleVideoRewardView):
    __slots__ = ('__vehicles', '__dataIter')

    def __init__(self, layoutID, rewards):
        self.__dataIter = (vD for vD in rewards['CosmicRewardsData'])
        vehicle, videoRes, isGuaranteed = next(self.__dataIter)
        videoDyn = R.videos.cosmic.reward_vehicle.dyn(videoRes)
        super(CosmicVideoReward, self).__init__(layoutID, vehicle, videoDyn(), rewards, isGuaranteed, VideoRewardsSoundControl())

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onIntroVideoStarted, self._onIntroVideoStarted))

    def _onIntroVideoStarted(self):
        super(CosmicVideoReward, self)._onVideoStarted()

    def _onClose(self):
        try:
            self._vehicle, videoRes, self._isGuaranteedReward = next(self.__dataIter)
            self._videoRes = R.videos.cosmic.reward_vehicle.dyn(videoRes)()
            self._soundControl.stop()
            self._update()
        except StopIteration:
            super(CosmicVideoReward, self)._onClose()


class CosmicUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData):
        rewardsData = getUniqueCosmicRewardsData(resultData)
        return cls(rewardsData) if rewardsData['CosmicRewardsData'] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = CosmicVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return CosmicVideoReward
