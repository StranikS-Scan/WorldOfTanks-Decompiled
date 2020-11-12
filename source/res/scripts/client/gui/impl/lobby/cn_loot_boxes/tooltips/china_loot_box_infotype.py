# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/tooltips/china_loot_box_infotype.py
from frameworks.wulf import ViewSettings
from gui.cn_loot_boxes.cn_loot_box_bonuses_packers import getCNLBInfoTypeBonusPacker
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.tooltips.china_loot_box_infotype_model import ChinaLootBoxInfotypeModel
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.tooltips.infotype_slot_model import InfotypeSlotModel, RewardType
from gui.impl.pub import ViewImpl
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.gui.game_control import ICNLootBoxesController
_VEHICLES_BONUS_NAME = 'vehicles'
_SLOTS_ORDER = range(0, 4)
_REWARDS_WHICH_NEED_MERGE = (BlueprintsBonusSubtypes.NATION_FRAGMENT, CREW_BOOK_RARITY.CREW_COMMON)

class LootBoxSlot(object):
    __slots__ = ('__probability', '__bonuses', '__rewardsType')

    def __init__(self, probability, bonuses):
        self.__probability = round(probability * 100, 2)
        self.__bonuses = bonuses
        self.__detectRewardsType(bonuses)

    def getProbability(self):
        return self.__probability

    def getRewards(self):
        return self.__bonuses.copy()

    def getRewardsType(self):
        return self.__rewardsType

    def getViewModel(self):
        slotModel = InfotypeSlotModel()
        slotModel.setProbability(self.__probability)
        slotModel.setRewardType(self.__rewardsType.value)
        rewardsModelArray = slotModel.getRewards()
        for bonus in self.__packBonuses():
            rewardsModelArray.addViewModel(bonus)

        rewardsModelArray.invalidate()
        return slotModel

    def __detectRewardsType(self, bonuses):
        if any((bonus.getName() == _VEHICLES_BONUS_NAME for bonus in bonuses)):
            self.__rewardsType = RewardType.VEHICLE
        else:
            self.__rewardsType = RewardType.DEFAULT

    def __packBonuses(self):
        packer = getCNLBInfoTypeBonusPacker()
        bonusList = []
        mergeRewards = {}
        for bonus in self.__bonuses:
            if bonus.isShowInGUI():
                if self.__rewardsType == RewardType.VEHICLE and bonus.getName() == _VEHICLES_BONUS_NAME or self.__rewardsType == RewardType.DEFAULT:
                    packedBonuses = packer.pack(bonus)
                    for packedBonus in packedBonuses:
                        if packedBonus.getName() in _REWARDS_WHICH_NEED_MERGE:
                            if packedBonus.getName() in mergeRewards:
                                count = mergeRewards[packedBonus.getName()].getCount()
                                mergeRewards[packedBonus.getName()].setCount(max(count, packedBonus.getCount()))
                            else:
                                mergeRewards[packedBonus.getName()] = packedBonus
                        bonusList.append(packedBonus)

        for mergeReward in mergeRewards.itervalues():
            bonusList.append(mergeReward)

        return bonusList


class ChinaLootBoxTooltip(ViewImpl):
    __slots__ = ('__boxType',)
    __cnLootBoxesCtrl = dependency.descriptor(ICNLootBoxesController)

    def __init__(self, boxType):
        settings = ViewSettings(R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxInfoType())
        settings.model = ChinaLootBoxInfotypeModel()
        self.__boxType = boxType
        super(ChinaLootBoxTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChinaLootBoxTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxTooltip, self)._onLoading(*args, **kwargs)
        boxesInfo = self.__cnLootBoxesCtrl.getBoxesInfo().get(self.__boxType, {})
        slots = boxesInfo.get('slots', {})
        with self.viewModel.transaction() as model:
            model.setBoxType(self.__boxType)
            slotsModel = model.getSlots()
            for slotName in _SLOTS_ORDER:
                slot = slots.get(slotName, {})
                lbSlot = LootBoxSlot(probability=slot.get('probability', 0), bonuses=slot.get('bonuses', []))
                slotsModel.addViewModel(lbSlot.getViewModel())

            slotsModel.invalidate()
