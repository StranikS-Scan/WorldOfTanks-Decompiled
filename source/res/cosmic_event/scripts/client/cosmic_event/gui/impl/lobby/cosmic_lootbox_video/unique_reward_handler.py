# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/cosmic_lootbox_video/unique_reward_handler.py
import typing
from typing import Dict, Optional, Type
from gui.impl.gen import R
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import getOpenedLootBoxFromRewards, isGuaranteedReward, processVehicles
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVideoRewardView, LootboxVideoRewardWindow
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.video.video_view import VideoViewWindow
from cosmic_constants import COSMIC_LOOTBOX_CATEGORY
from cosmic_event.gui.sound_control.sound_control import VideoRewardsSoundControl
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
REWARDS_DATA_CATEGORY = 'CosmicRewardsData'

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueCosmicRewardsData(resultData, itemsCache=None):
    rewardsData = {REWARDS_DATA_CATEGORY: []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is not None and openedLootbox.getCategory().startswith(COSMIC_LOOTBOX_CATEGORY):
            isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
            processVehicles(rewardsData, rewards.get('vehicles', []), isGuaranteed, openedLootbox, rewardsCategory=REWARDS_DATA_CATEGORY)

    return rewardsData


class CosmicVideoReward(LootboxVideoRewardView):
    __slots__ = ('__vehicles', '__dataIter')

    def __init__(self, layoutID, rewards):
        self.__dataIter = (vD for vD in rewards[REWARDS_DATA_CATEGORY])
        bonus, videoRes, isGuaranteed, lootbox = next(self.__dataIter)
        super(CosmicVideoReward, self).__init__(layoutID, bonus, videoRes, rewards, isGuaranteed, VideoRewardsSoundControl(), lootbox=lootbox)

    def _onClose(self):
        try:
            self._bonus, self._videoRes, self._isGuaranteedReward, self._lootbox = next(self.__dataIter)
            self._soundControl.stop()
            self._update()
        except StopIteration:
            super(CosmicVideoReward, self)._onClose()


class CosmicUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData):
        rewardsData = getUniqueCosmicRewardsData(resultData)
        return cls(rewardsData) if rewardsData[REWARDS_DATA_CATEGORY] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = CosmicVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return CosmicVideoReward
