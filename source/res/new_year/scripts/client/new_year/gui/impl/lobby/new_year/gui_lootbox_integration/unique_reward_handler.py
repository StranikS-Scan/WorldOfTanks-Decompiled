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
from new_year.ny_constants import NewYearCategories, NewYearLootBoxRewards
from new_year.ny_constants import NewYearLootBoxes
from shared_utils import first
from skeletons.gui.shared import IItemsCache
_REWARDS_VIDEO_ORDER = ('vehicles', 'lootBoxToken', 'customizations')
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window

def getVideoResForVehicle(vehicle):
    return getNationLessName(vehicle.name).replace('-', '_')


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVideoResForLootbox(lootboxToken, itemsCache=None):
    lootBoxID = getLootBoxIDFromToken(lootboxToken)
    lootBox = itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
    return lootBox.getType()


def getVideoResForCustomization(custBonus):
    return 'customizations_{}'.format(first(custBonus.getWrappedBonus(), {}).get('id', 0))


def getVideoExists(videoRes):
    resId = R.videos.VehicleLootBoxCongrats.dyn(videoRes)
    return resId.exists()


def isGuaranteedReward(limitName, usedLimits):
    return usedLimits is not None and limitName in usedLimits


_VideoRewardData = namedtuple('_VideoRewardData', ('bonus', 'video', 'isGuaranteed'))

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processVehicles(rewardsData, vehiclesList, isGuaranteed, itemsCache=None):
    for vehiclesDict in vehiclesList:
        for venIntCD, vehicleData in vehiclesDict.iteritems():
            vehicleBonus = VehiclesBonus('vehicles', {venIntCD: vehicleData})
            if {'rentCompensation', 'customCompensation'}.isdisjoint(vehicleData):
                vehicle = itemsCache.items.getItemByCD(venIntCD)
                video = getVideoResForVehicle(vehicle)
                if getVideoExists(video):
                    rewardsData['nyRewardsData'].append(_VideoRewardData(vehicleBonus, video, isGuaranteed))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processTokens(rewardsData, tokens, isGuaranteed, itemsCache=None):
    for tokenID, tokenData in tokens.iteritems():
        if tokenData.get('count', 0) <= 0:
            continue
        if tokenID.startswith('lootBox'):
            tokenBonus = first(tokensFactory('tokens', {tokenID: tokenData}))
            video = getVideoResForLootbox(tokenID)
            if getVideoExists(video) and tokenBonus:
                rewardsData['nyRewardsData'].append(_VideoRewardData(tokenBonus, video, isGuaranteed))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processCustomization(rewardsData, customizationsList, isGuaranteed, itemsCache=None):
    for custItem in customizationsList:
        custBonus = CustomizationsBonus('customizations', [custItem])
        video = getVideoResForCustomization(custBonus)
        if getVideoExists(video):
            rewardsData['nyRewardsData'].append(_VideoRewardData(custBonus, video, isGuaranteed))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueNYRewardsData(resultData, nyLootboxCategories, itemsCache=None):
    rewardsData = {'nyRewardsData': []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is not None and openedLootbox.getCategory() in nyLootboxCategories:
            isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
            processVehicles(rewardsData, rewards.get('vehicles', []), isGuaranteed)
            processTokens(rewardsData, rewards.get('tokens', {}), isGuaranteed)
            processCustomization(rewardsData, rewards.get('customizations', []), isGuaranteed)

    return rewardsData


def _videoRewardsSortOrder(rewards):
    rewardName = rewards.bonus.getName()
    return _REWARDS_VIDEO_ORDER.index(rewardName) if rewardName in _REWARDS_VIDEO_ORDER else len(_REWARDS_VIDEO_ORDER)


class NewYearVideoReward(LootboxVideoRewardView):
    _COMMON_SOUND_SPACE = NY_REWARD_VIDEO_SOUND_SPACE
    __slots__ = ('__dataIter',)

    def __init__(self, layoutID, rewards):
        self.__dataIter = [ vD for vD in rewards['nyRewardsData'] ]
        self.__removeDuplicateVideoLootboxes()
        bonus, videoRes, isGuaranteed = next(self.__dataIter)
        super(NewYearVideoReward, self).__init__(layoutID, bonus, videoRes, rewards, isGuaranteed, VideoRewardsSoundControl(NewYearLootBoxRewards.ALL.get(videoRes, 'tank_default')))

    def __removeDuplicateVideoLootboxes(self):
        isLootboxVideoAdded = False
        videoDatas = []
        for videoData in self.__dataIter:
            if videoData.video != NewYearLootBoxes.NY_25_TANKS:
                videoDatas.append(videoData)
            if videoData.video == NewYearLootBoxes.NY_25_TANKS and not isLootboxVideoAdded:
                isLootboxVideoAdded = True
                videoDatas.append(videoData)

        if len(videoDatas) > 1:
            self.__sortRewards(videoDatas, _videoRewardsSortOrder)
        self.__dataIter = (vD for vD in videoDatas)

    def __sortRewards(self, videoDatas, sortMethod):
        videoDatas.sort(key=sortMethod)

    def _onClose(self):
        try:
            self._bonus, self._videoRes, self._isGuaranteedReward = next(self.__dataIter)
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
        return cls(rewardsData) if rewardsData['nyRewardsData'] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = NewYearVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return NewYearVideoReward
