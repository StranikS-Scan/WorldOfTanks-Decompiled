# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_popover_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.game_control.wt_lootboxes_controller import convertToBonuses
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.infotype_slot_model import InfotypeSlotModel, RewardType
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_popover_tooltip_view_model import WtEventPopoverTooltipViewModel, BoxType
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from gui.shared.gui_items.loot_box import WTLootBoxes
from gui.wt_event.wt_event_helpers import WT_RENTAL_TOKEN
from gui.wt_event.wt_event_simple_bonus_packers import getEventLootBoxesInfoTypeBonusPacker
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.gui.game_control import IWTLootBoxesController
_VEHICLES_BONUS_NAME = 'vehicles'
_REWARDS_WHICH_NEED_MERGE = (BlueprintsBonusSubtypes.NATION_FRAGMENT,
 CREW_BOOK_RARITY.CREW_COMMON,
 CREW_BOOK_RARITY.CREW_EPIC,
 CREW_BOOK_RARITY.CREW_RARE)
_REWARDS_WITHOUT_DUPLICATES = {'customizations'}

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
        slotModel.setRewardType(RewardType(self.__rewardsType))
        rewardsModelArray = slotModel.getRewards()
        for bonus in self.__packBonuses():
            rewardsModelArray.addViewModel(bonus)

        rewardsModelArray.invalidate()
        return slotModel

    def __detectRewardsType(self, bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'gold':
                self.__rewardsType = RewardType.GOLD
                return
            if bonus.getName() == 'vehicles':
                self.__rewardsType = RewardType.VEHICLE
                return
            if bonus.getName() == 'battleToken' and bonus.getValue().keys() and WT_RENTAL_TOKEN in bonus.getValue().keys()[0]:
                self.__rewardsType = RewardType.RENTALTANK
                return

        self.__rewardsType = RewardType.DEFAULT

    def __packBonuses(self):
        packer = getEventLootBoxesInfoTypeBonusPacker()
        bonusList = []
        mergeRewards = {}
        rawBonusList = []
        for bonus in self.__bonuses:
            if not self.__isValidBonus(bonus):
                continue
            if self.__isAlreadyIncluded(bonus, rawBonusList):
                continue
            rawBonusList.append(bonus)
            packedBonuses = packer.pack(bonus)
            for packedBonus in packedBonuses:
                if packedBonus.getName() in _REWARDS_WHICH_NEED_MERGE:
                    if packedBonus.getName() in mergeRewards:
                        count = mergeRewards[packedBonus.getName()].getCount()
                        mergeRewards[packedBonus.getName()].setCount(max(count, packedBonus.getCount()))
                        packedBonus.unbind()
                    else:
                        mergeRewards[packedBonus.getName()] = packedBonus
                if not self.__isExistingVehicle(packedBonus, bonusList):
                    bonusList.append(packedBonus)

        for mergeReward in mergeRewards.itervalues():
            bonusList.append(mergeReward)

        return bonusList

    def __isValidBonus(self, bonus):
        isVehicleReward = self.__rewardsType == RewardType.VEHICLE and bonus.getName() == _VEHICLES_BONUS_NAME
        isValidReward = self.__rewardsType in (RewardType.DEFAULT, RewardType.GOLD)
        return bonus.isShowInGUI() and (isVehicleReward or isValidReward)

    def __isAlreadyIncluded(self, bonus, bonusList):
        if bonus.getName() not in _REWARDS_WITHOUT_DUPLICATES:
            return False
        return any([ x for x in bonusList if bonus.isEqual(x) ])

    def __isExistingVehicle(self, packedBonus, bonusList):
        return self.__rewardsType == RewardType.VEHICLE and packedBonus.getName() in (b.getName() for b in bonusList)


class WtEventPopoverTooltipView(ViewImpl):
    __slots__ = ('__boxType',)
    __eventLootBoxes = dependency.descriptor(IWTLootBoxesController)

    def __init__(self, boxType):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventPopoverTooltipView())
        settings.model = WtEventPopoverTooltipViewModel()
        self.__boxType = boxType
        super(WtEventPopoverTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventPopoverTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventPopoverTooltipView, self)._onLoading(*args, **kwargs)
        boxesInfo = self.__eventLootBoxes.getBoxesInfo().get(self.__boxType, {})
        slots = boxesInfo.get('slots', {})
        with self.viewModel.transaction() as model:
            model.setGuaranteedLimit(self.__eventLootBoxes.getGuaranteedBonusLimit(self.__boxType))
            model.setBoxType(BoxType(self.__boxType))
            self.__updateSlots(slots=slots, model=model)

    def _getEvents(self):
        return ((self.__eventLootBoxes.onBoxInfoUpdated, self.__onBoxInfoUpdated),)

    def __onBoxInfoUpdated(self):
        boxesInfo = self.__eventLootBoxes.getBoxesInfo().get(self.__boxType, {})
        slots = boxesInfo.get('slots', {})
        self.__updateSlots(slots=slots)

    @replaceNoneKwargsModel
    def __updateSlots(self, slots, model=None):
        slotsModel = model.getSlots()
        slotsModel.clear()
        slots = self.__reorderSlots(slots, self.__boxType)
        for slotName in range(0, len(slots)):
            slot = slots.get(slotName, {})
            lbSlot = LootBoxSlot(slot.get('probability', [[0]])[0], slot.get('bonuses', []))
            slotsModel.addViewModel(lbSlot.getViewModel())

        slotsModel.invalidate()

    def __reorderSlots(self, slots, boxType):
        if boxType == WTLootBoxes.WT_BOSS:
            newSlots = dict()
            extra = self.__eventLootBoxes.getExtraRewards(boxType, count=0)
            extraRewardBonus = {'probability': [1],
             'bonuses': convertToBonuses(extra)[0].bonuses}
            newSlots[0] = extraRewardBonus
            for i in range(0, len(slots)):
                newSlots[i + 1] = slots[i]

            return newSlots
        return slots if boxType == WTLootBoxes.WT_HUNTER else None
