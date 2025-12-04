# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/gui_lootbox_integration/unique_reward_handler.py
import typing
from collections import namedtuple
from gui.impl.gen import R
from new_year.gui.impl.lobby.loot_box.ny_loot_box_helper import getOpenedLootBoxFromRewards
from new_year.gui.impl.new_year.sounds import NY_REWARD_VIDEO_SOUND_SPACE, VideoRewardsSoundControl
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxIDFromToken
from gui.server_events.bonuses import VehiclesBonus, tokensFactory, CustomizationsBonus
from gui.shared.gui_items.Vehicle import getNationLessName
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVideoRewardView, LootboxVideoRewardWindow
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from helpers import dependency
from new_year.ny_constants import NewYearCategories, NewYearLootBoxes
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
REWARDS_DATA_CATEGORY = 'NyRewardsData'
_REWARDS_VIDEO_ORDER = ('vehicles', 'lootBoxToken', 'customizations')

def getVideoResForVehicle(vehicle):
    return getNationLessName(vehicle.name).replace('-', '_')


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVideoResForLootbox(lootboxToken, itemsCache=None):
    lootBoxID = getLootBoxIDFromToken(lootboxToken)
    lootBox = itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
    return lootBox.getType()


def getVideoResForCustomization(custBonus):
    return 'customizations_{}'.format(first(custBonus.getWrappedBonus(), {}).get('id', 0))


def getVideoExists(videoRes, lbType):
    resId = R.videos.lootbox_reward_video.dyn(lbType).dyn(videoRes)
    return resId.exists()


def isGuaranteedReward(limitName, usedLimits):
    return usedLimits is not None and limitName in usedLimits


_VideoRewardData = namedtuple('_VideoRewardData', ('bonus', 'video', 'isGuaranteed', 'openedLootbox'))

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processVehicles(rewardsData, vehiclesList, isGuaranteed, openedLootbox, itemsCache=None):
    for vehiclesDict in vehiclesList:
        for venIntCD, vehicleData in vehiclesDict.iteritems():
            vehicleBonus = VehiclesBonus('vehicles', {venIntCD: vehicleData})
            if {'rentCompensation', 'customCompensation'}.isdisjoint(vehicleData):
                vehicle = itemsCache.items.getItemByCD(venIntCD)
                video = getVideoResForVehicle(vehicle)
                if getVideoExists(video, openedLootbox.getType()):
                    rewardsData[REWARDS_DATA_CATEGORY].append(_VideoRewardData(vehicleBonus, video, isGuaranteed, openedLootbox))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processTokens(rewardsData, tokens, isGuaranteed, openedLootbox, itemsCache=None):
    for tokenID, tokenData in tokens.iteritems():
        if tokenData.get('count', 0) <= 0:
            continue
        if tokenID.startswith('lootBox'):
            tokenBonus = first(tokensFactory('tokens', {tokenID: tokenData}))
            video = getVideoResForLootbox(tokenID, itemsCache=itemsCache)
            if getVideoExists(video, openedLootbox.getType()):
                rewardsData[REWARDS_DATA_CATEGORY].append(_VideoRewardData(tokenBonus, video, isGuaranteed, openedLootbox))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processCustomization(rewardsData, customizationsList, isGuaranteed, openedLootbox, itemsCache=None):
    for custItem in customizationsList:
        custBonus = CustomizationsBonus('customizations', [custItem])
        video = getVideoResForCustomization(custBonus)
        if getVideoExists(video, openedLootbox.getType()):
            rewardsData[REWARDS_DATA_CATEGORY].append(_VideoRewardData(custBonus, video, isGuaranteed, openedLootbox))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueNYRewardsData(resultData, nyLootboxCategories, itemsCache=None):
    rewardsData = {REWARDS_DATA_CATEGORY: []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is None or openedLootbox.getCategory() not in nyLootboxCategories:
            continue
        isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
        processVehicles(rewardsData, rewards.get('vehicles', []), isGuaranteed, openedLootbox)
        processTokens(rewardsData, rewards.get('tokens', {}), isGuaranteed, openedLootbox)
        processCustomization(rewardsData, rewards.get('customizations', []), isGuaranteed, openedLootbox)

    return rewardsData


def _videoRewardsSortOrder(rewards):
    rewardName = rewards.bonus.getName()
    return _REWARDS_VIDEO_ORDER.index(rewardName) if rewardName in _REWARDS_VIDEO_ORDER else len(_REWARDS_VIDEO_ORDER)


class NewYearVideoReward(LootboxVideoRewardView):
    _COMMON_SOUND_SPACE = NY_REWARD_VIDEO_SOUND_SPACE
    __slots__ = ('__dataIter',)

    def __init__(self, layoutID, rewards):
        self.__dataIter = (vD for vD in rewards[REWARDS_DATA_CATEGORY])
        self.__removeDuplicateVideoLootboxes()
        bonus, videoRes, isGuaranteed, lootbox = next(self.__dataIter)
        super(NewYearVideoReward, self).__init__(layoutID, bonus, videoRes, rewards, isGuaranteed, VideoRewardsSoundControl(videoRes), lootbox=lootbox)

    def __removeDuplicateVideoLootboxes(self):
        isLootboxVideoAdded = False
        videoDatas = []
        for videoData in self.__dataIter:
            if videoData.video != NewYearLootBoxes.NY_CUR_YEAR_TANKS:
                videoDatas.append(videoData)
            if videoData.video == NewYearLootBoxes.NY_CUR_YEAR_TANKS and not isLootboxVideoAdded:
                isLootboxVideoAdded = True
                videoDatas.append(videoData)

        if len(videoDatas) > 1:
            self.__sortRewards(videoDatas, _videoRewardsSortOrder)
        self.__dataIter = (vD for vD in videoDatas)

    def __sortRewards(self, videoDatas, sortMethod):
        videoDatas.sort(key=sortMethod)

    def _getVideoConfigKey(self):
        return self._lootbox.getType()

    def _onClose(self):
        try:
            self._bonus, self._videoRes, self._isGuaranteedReward, self._lootbox = next(self.__dataIter)
            self._soundControl.stop()
            self._soundControl.setBonusName(self._videoRes)
            self._update()
        except StopIteration:
            super(NewYearVideoReward, self)._onClose()


class NewYearUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData):
        rewardsData = getUniqueNYRewardsData(resultData, NewYearCategories.ALL())
        return cls(rewardsData) if rewardsData[REWARDS_DATA_CATEGORY] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = NewYearVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return NewYearVideoReward
