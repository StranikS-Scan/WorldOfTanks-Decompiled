# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/additional_rewards_view.py
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.server_events.bonuses import SimpleBonus, VehiclesBonus
from helpers import dependency
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_reward_view_model import RewardType
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
from one_time_gift.gui.impl.lobby.awards.base_reward_view import BaseRewardView
from one_time_gift.gui.impl.lobby.awards.packers import composeBonuses, getOTGMixedRewardsBonusPacker, OneTimeGiftItemBonusUIPacker
from one_time_gift.gui.impl.lobby.tooltips.otg_equipment_set_tooltip_view import OTGEquipmentSetTooltipView
from one_time_gift.gui.impl.lobby.tooltips.otg_quest_tooltip_view import OTGQuestTooltipView
DEFAULT_FIRST_ROW_COUNT = 4
DEFAULT_SECOND_ROW_COUNT = 10

def _getShownRewardsCount(rewardsCount, layoutTotalCount):
    return rewardsCount if rewardsCount <= layoutTotalCount else layoutTotalCount - 1


class AdditionalRewardsView(BaseRewardView):
    _oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)
    _REWARD_TYPE = RewardType.ADDITIONAL_REWARD

    def __init__(self, viewModel, parentView):
        super(AdditionalRewardsView, self).__init__(viewModel, parentView)
        self.__rewards = None
        return

    @property
    def viewId(self):
        return MainViews.ADDITIONAL_REWARD

    def finalize(self):
        self.__rewards = None
        super(AdditionalRewardsView, self).finalize()
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            return self.__createBoxRewardsTooltip()
        if contentID == R.aliases.one_time_gift.default.EquipmentSetTooltip():
            return self.__createOTGEquipmentSetTooltip(event)
        return self.__createOTGQuestTooltip(event) if contentID == R.views.one_time_gift.mono.lobby.one_time_gift_quest_tooltip() else super(AdditionalRewardsView, self).createTooltipContent(event, contentID)

    def _composeRewards(self, bonuses):
        return composeBonuses(bonuses)

    def _setResources(self, vm):
        locales = R.strings.one_time_gift.awards.additionalRewardFull
        vm.setTitle(locales.title())
        vm.setDefaultButtonTitle(locales.button.submit())

    def _setRewards(self, vm, rewards):
        self.__rewards = rewards
        self.__packBonusModelAndTooltipData(vm, rewards)

    def __createBoxRewardsTooltip(self):
        if not self.__rewards:
            return
        packer = getOTGMixedRewardsBonusPacker()
        packed = []
        for bonus in self.__rewards:
            packed.extend(packer.pack(bonus))

        order, firstRowCount, secondRowCount = self.__getRowsLayout()
        shownCount = _getShownRewardsCount(len(packed), firstRowCount + secondRowCount)
        packed.sort(key=lambda item: order.index(item.getName()) if item.getName() in order else len(order))
        boxRewards = [ bonus for bonus in packed[shownCount:] ]
        return AdditionalRewardsTooltip(boxRewards)

    def __createOTGEquipmentSetTooltip(self, event):
        tooltipId = event.getArgument('tooltipId')
        data = self._tooltipItems.get(tooltipId)
        if data is None:
            return
        else:
            itemsForTooltip = data.specialArgs.get('itemsForTooltip')
            if not itemsForTooltip:
                return
            bonus = data.specialArgs.get('bonus')
            itemsForTooltip.sort(key=lambda i: i[0].name)
            packedBonuses = []
            for item, count in itemsForTooltip:
                packedBonuses.append(OneTimeGiftItemBonusUIPacker.packSingleBonus(bonus, item, count))

            return OTGEquipmentSetTooltipView(packedBonuses)

    def __createOTGQuestTooltip(self, event):
        tooltipData = self.getTooltipData(event)
        return None if tooltipData is None else OTGQuestTooltipView(*tooltipData.specialArgs)

    def __getRowsLayout(self):
        config = self._oneTimeGiftController.getConfig().additionalRewards
        mainRewardConfig = config['newbie' if self._oneTimeGiftController.isPlayerNewbie() else 'veteran']['mainReward']
        layout = mainRewardConfig.get('layout') or {}
        order = layout.get('order') or tuple()
        firstRowCount = layout.get('firstRowCount', DEFAULT_FIRST_ROW_COUNT)
        secondRowCount = layout.get('secondRowCount', DEFAULT_SECOND_ROW_COUNT)
        return (order, firstRowCount, secondRowCount)

    def __packBonusModelAndTooltipData(self, vm, rewards):
        itemsForModel = []
        packer = getOTGMixedRewardsBonusPacker()
        for bonus in rewards:
            if bonus.isShowInGUI():
                bonusList = packer.pack(bonus)
                if not bonusList:
                    continue
                bonusTooltipList = packer.getToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
                for bonusIndex, item in enumerate(bonusList):
                    bonusTooltipData, bonusContentIdData = (None, None)
                    if bonusTooltipList:
                        bonusTooltipData = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        bonusContentIdData = str(bonusContentIdList[bonusIndex])
                    if bonus.getName() == VehiclesBonus.VEHICLES_BONUS and item.getName() == 'vehicles':
                        continue
                    itemsForModel.append((item, bonusTooltipData, bonusContentIdData))

        order, firstRowCount, secondRowCount = self.__getRowsLayout()
        itemsForModel.sort(key=lambda item: order.index(item[0].getName()) if item[0].getName() in order else len(order))
        shownCount = _getShownRewardsCount(len(itemsForModel), firstRowCount + secondRowCount)
        boxedCount = len(itemsForModel) - shownCount
        if boxedCount > 0:
            vm.setBoxRewardsCount(boxedCount)
        for idx, data in enumerate(itemsForModel[:shownCount]):
            item, bonusTooltipData, bonusContentIdData = data
            if idx < firstRowCount:
                item.setIndex(idx)
                vm.mainRewards.addViewModel(item)
            else:
                item.setIndex(idx - firstRowCount)
                vm.additionalRewards.addViewModel(item)
            tooltipIdx = str(idx)
            item.setTooltipId(tooltipIdx)
            if bonusTooltipList:
                self._tooltipItems[tooltipIdx] = bonusTooltipData
            if bonusContentIdList:
                item.setTooltipContentId(bonusContentIdData)

        return None
