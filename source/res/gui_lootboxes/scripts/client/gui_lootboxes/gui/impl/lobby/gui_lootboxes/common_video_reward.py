# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/common_video_reward.py
import typing
from gui.impl.gen import R
from gui.impl.lobby.loot_box.sound_control import VideoRewardsSoundControl
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import processVehicles
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVideoRewardView
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import UniqueLootBoxesRewardsWindow
REWARDS_DATA_CATEGORY = 'CommonRewardsData'

class FakeGUILootbox(object):
    __slots__ = ('__category',)

    def __init__(self, category):
        self.__category = category

    def getCategory(self):
        return self.__category

    def getID(self):
        pass

    def getType(self):
        pass


def getUniqueCommonRewardsData(rewards, lootbox):
    rewardsData = {REWARDS_DATA_CATEGORY: []}
    if not lootbox:
        return rewardsData
    processVehicles(rewardsData, rewards.get('vehicles', []), False, lootbox, rewardsCategory=REWARDS_DATA_CATEGORY)
    return rewardsData


class CommonVideoReward(LootboxVideoRewardView):
    __slots__ = ('__dataIter', '__closeCallback')

    def __init__(self, layoutID, rewards, soundControl, closeCallback):
        self.__dataIter = (vD for vD in rewards[REWARDS_DATA_CATEGORY])
        self.__closeCallback = closeCallback
        bonus, videoRes, isGuaranteed, lootbox = next(self.__dataIter)
        super(CommonVideoReward, self).__init__(layoutID, bonus, videoRes, rewards, isGuaranteed, soundControl, lootbox=lootbox)

    def _onClose(self):
        try:
            self._bonus, self._videoRes, self._isGuaranteedReward, self._lootbox = next(self.__dataIter)
            self._soundControl.stop()
            self._update()
        except StopIteration:
            self.__closeCallback()
            super(CommonVideoReward, self)._onClose()


class CommonUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData, lootbox=None):
        rewardsData = getUniqueCommonRewardsData(resultData, lootbox)
        return cls(rewardsData) if rewardsData[REWARDS_DATA_CATEGORY] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent, closeCallback=lambda : None):
        viewClass = self._getRewardsViewClass()
        layoutID = self.getRewardsViewID()
        soundControl = self.getVideoRewarsdSoundControl()
        rewardData = self.getRewardsData()
        content = viewClass(layoutID, rewardData, soundControl(), closeCallback)
        self._window = UniqueLootBoxesRewardsWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return CommonVideoReward

    def getVideoRewarsdSoundControl(self):
        return VideoRewardsSoundControl
