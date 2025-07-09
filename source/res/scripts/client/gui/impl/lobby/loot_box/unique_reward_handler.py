# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/unique_reward_handler.py
import typing
from typing import Dict, Optional, Type
from gui.impl.gen import R
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import processVehicles, getOpenedLootBoxFromRewards, isGuaranteedReward
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVideoRewardView, LootboxVideoRewardWindow
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from constants import LOOTBOX_MTL_CATEGORY
from gui.impl.lobby.loot_box.sound_control import VideoRewardsSoundControl
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
REWARDS_DATA_CATEGORY = 'MTLRewardsData'

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueRewardsData(resultData, itemsCache=None):
    rewardsData = {REWARDS_DATA_CATEGORY: []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is not None and openedLootbox.getCategory() in [LOOTBOX_MTL_CATEGORY]:
            isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
            processVehicles(rewardsData, rewards.get('vehicles', []), isGuaranteed, openedLootbox, rewardsCategory=REWARDS_DATA_CATEGORY)

    return rewardsData


class MTLVideoReward(LootboxVideoRewardView):
    __slots__ = ('_vehicles', '__dataIter')

    def __init__(self, layoutID, rewards):
        self.__dataIter = (vD for vD in rewards[REWARDS_DATA_CATEGORY])
        vehicle, videoRes, isGuaranteed, lootbox = next(self.__dataIter)
        super(MTLVideoReward, self).__init__(layoutID, vehicle, videoRes, rewards, isGuaranteed, VideoRewardsSoundControl(), lootbox=lootbox)

    def _onClose(self):
        try:
            self._vehicles, self._videoRes, self._isGuaranteedReward = next(self.__dataIter)
            self._soundControl.stop()
            self._update()
        except StopIteration:
            super(MTLVideoReward, self)._onClose()


class MTLUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData):
        rewardsData = getUniqueRewardsData(resultData)
        return cls(rewardsData) if rewardsData[REWARDS_DATA_CATEGORY] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = MTLVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return MTLVideoReward
