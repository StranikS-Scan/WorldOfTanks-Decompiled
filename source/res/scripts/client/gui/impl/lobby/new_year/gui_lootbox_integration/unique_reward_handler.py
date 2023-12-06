# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gui_lootbox_integration/unique_reward_handler.py
import typing
from collections import namedtuple
from gui.impl.gen import R
from gui.impl.lobby.loot_box.ny_loot_box_helper import getOpenedLootBoxFromRewards
from gui.impl.new_year.sounds import NY_REWARD_VIDEO_SOUND_SPACE, VideoRewardsSoundControl
from gui.shared.gui_items.Vehicle import getNationLessName
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootbox_video_reward_view import LootboxVehicleVideoRewardView, LootboxVideoRewardWindow
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardHandler
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items.loot_box import NewYearCategories
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window

def getRewardVideo(vehicle):
    return R.videos.VehicleLootBoxCongrats.dyn(getNationLessName(vehicle.name).replace('-', '_'), R.invalid)()


def isGuaranteedReward(limitName, usedLimits):
    return usedLimits is not None and limitName in usedLimits


_VideoRewardData = namedtuple('_VideoRewardData', ('vehicle', 'video', 'isGuaranteed'))

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUniqueVehicleRewardsData(resultData, nyLootboxCategories, itemsCache=None):
    rewardsData = {'vehiclesData': []}
    usedLimits = resultData.get('extData', {}).get('usedLimits', None)
    for idx, rewards in enumerate(resultData.get('bonus', [])):
        vehiclesList = rewards.get('vehicles', [])
        openedLootbox = getOpenedLootBoxFromRewards(rewards, itemsCache=itemsCache)
        if openedLootbox is not None and openedLootbox.getCategory() in nyLootboxCategories:
            for vehiclesDict in vehiclesList:
                for venIntCD, vehicleData in vehiclesDict.iteritems():
                    if {'rentCompensation', 'customCompensation'}.isdisjoint(vehicleData):
                        vehicle = itemsCache.items.getItemByCD(venIntCD)
                        video = getRewardVideo(vehicle)
                        if video:
                            isGuaranteed = isGuaranteedReward(openedLootbox.getGuaranteedFrequencyName(), None if usedLimits is None else usedLimits[idx])
                            rewardsData['vehiclesData'].append(_VideoRewardData(vehicle, video, isGuaranteed))

    rewardsData['vehiclesData'].sort(key=lambda d: d[0])
    return rewardsData


class NewYearVideoReward(LootboxVehicleVideoRewardView):
    _COMMON_SOUND_SPACE = NY_REWARD_VIDEO_SOUND_SPACE
    __slots__ = ('__vehicles', '__dataIter')

    def __init__(self, layoutID, rewards):
        self.__dataIter = (vD for vD in rewards['vehiclesData'])
        vehicle, videoRes, isGuaranteed = next(self.__dataIter)
        super(NewYearVideoReward, self).__init__(layoutID, vehicle, videoRes, rewards, isGuaranteed, VideoRewardsSoundControl(getNationLessName(vehicle.name)))

    def _onClose(self):
        try:
            self._vehicle, self._videoRes, self._isGuaranteedReward = next(self.__dataIter)
            self._soundControl.stop()
            self._soundControl.setVehicleName(getNationLessName(self._vehicle.name))
            self._update()
        except StopIteration:
            super(NewYearVideoReward, self)._onClose()


class NewYearVehicleUniqueRewardHandler(BaseUniqueRewardHandler):
    __slots__ = ('_vehicles',)

    @classmethod
    def createHandler(cls, resultData):
        rewardsData = getUniqueVehicleRewardsData(resultData, NewYearCategories.ALL())
        return cls(rewardsData) if rewardsData['vehiclesData'] else None

    def getRewardsViewID(self):
        return R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxVideoRewardView()

    def showRewardsWindow(self, parent):
        content = NewYearVideoReward(self.getRewardsViewID(), rewards=self.getRewardsData())
        self._window = LootboxVideoRewardWindow(content, parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return NewYearVideoReward
