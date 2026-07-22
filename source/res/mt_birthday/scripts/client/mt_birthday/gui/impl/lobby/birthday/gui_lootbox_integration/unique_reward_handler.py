# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/gui_lootbox_integration/unique_reward_handler.py
import typing
from skeletons.gui.shared import IItemsCache
from gui.impl.gen import R
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import isGuaranteedReward, getOpenedLootBoxFromRewards, processVehicles
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVideoRewardView, LootboxVideoRewardWindow
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from helpers import dependency
from mt_birthday.gui.impl.sounds import BIRTHDAY_REWARD_VIDEO_SOUND_SPACE, VideoRewardsSoundControl
REWARDS_DATA_CATEGORY = 'eventRewardsData'
EVENT_CATEGORY = 'tanks_birthday_2026'
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueRewardsData(resultData, itemsCache=None):
    rewardsData = {REWARDS_DATA_CATEGORY: []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is not None and openedLootbox.getCategory() in EVENT_CATEGORY:
            isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
            processVehicles(rewardsData, rewards.get('vehicles', []), isGuaranteed, openedLootbox, rewardsCategory=REWARDS_DATA_CATEGORY)

    return rewardsData


class BirthdayVideoReward(LootboxVideoRewardView):
    _COMMON_SOUND_SPACE = BIRTHDAY_REWARD_VIDEO_SOUND_SPACE
    __slots__ = ('__vehicles', '__dataIter')

    def __init__(self, layoutID, rewards):
        self.__dataIter = (vD for vD in rewards[REWARDS_DATA_CATEGORY])
        bonus, videoRes, isGuaranteed, _lootbox = next(self.__dataIter)
        super(BirthdayVideoReward, self).__init__(layoutID, bonus, videoRes, rewards, isGuaranteed, VideoRewardsSoundControl(videoRes), lootbox=_lootbox)

    def _onClose(self):
        try:
            self._bonus, self._videoRes, self._isGuaranteedReward, self._lootbox = next(self.__dataIter)
            self._soundControl.stop()
            self._update()
        except StopIteration:
            super(BirthdayVideoReward, self)._onClose()


class BirthdayUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData):
        rewardsData = getUniqueRewardsData(resultData)
        return cls(rewardsData) if rewardsData[REWARDS_DATA_CATEGORY] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = BirthdayVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return BirthdayVideoReward
