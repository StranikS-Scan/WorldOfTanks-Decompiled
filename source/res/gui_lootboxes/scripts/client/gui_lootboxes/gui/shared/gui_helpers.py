# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/shared/gui_helpers.py
from frameworks.wulf.view.array import fillStringsArray, fillIntsArray
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from gui.server_events.bonuses import mergeBonuses, splitBonuses
from gui.shared.gui_items.loot_box import LootBox, GROUP_PRIORITIES
from gui_lootboxes.gui.bonuses.bonuses_helpers import calculateCountBonusItems
from gui_lootboxes.gui.bonuses.bonuses_packers import getStatisticsBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses, getStatisticSortKeyFunc
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_key_view_model import LootboxKeyViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_view_model import LootboxViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.statistic_reward_model import StatisticRewardModel
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import IGuiLootBoxesController

def getLootBoxViewModel(lootBox, attemptsAfterGuaranteedReward):
    lbModel = LootboxViewModel()
    lbModel.setTier(lootBox.getTier())
    lbModel.setBoxID(lootBox.getID())
    lbModel.setBoxType(lootBox.getType())
    lbModel.setCount(lootBox.getInventoryCount())
    lbModel.setIsOpenEnabled(lootBox.isEnabled())
    lbModel.setAutoOpenTime(lootBox.getAutoOpenTime())
    lbModel.setUserName(lootBox.getUserNameKey())
    lbModel.setIconName(lootBox.getIconName())
    lbModel.setDescriptionKey(lootBox.getDesrciption())
    lbModel.setVideoRes(lootBox.getVideoRes())
    lbModel.setCategory(lootBox.getCategory())
    lbModel.setIsInfinite(lootBox.isHiddenCount())
    lbModel.setHasUniqueBack(lootBox.hasUniqueBack())
    lbModel.setManualMaxOpenCount(lootBox.getManualMaxOpenCount())
    fillIntsArray(lootBox.getUnlockKeyIDs(), lbModel.getUnlockKeyIDs())
    rotationStage = lootBox.getCurrentRotationStage()
    guaranteedFrequency = lootBox.getGuaranteedFrequency()
    if guaranteedFrequency > 0:
        fillIntsArray(lootBox.getGuaranteedVehicleLevelsRange(), lbModel.guaranteedReward.getLevelsRange())
        lbModel.guaranteedReward.setBoxesUntilGuaranteedReward(guaranteedFrequency - attemptsAfterGuaranteedReward)
        lbModel.guaranteedReward.setVehiclesOnly(lootBox.isVehicleGuaranteedOnly())
    lbModel.setProgressionStage(rotationStage)
    fillStringsArray(lootBox.getBonusGroups(), lbModel.getBonusGroups())
    return lbModel


def getLootBoxKeyViewModel(lootBoxKey):
    lbKeyModel = LootboxKeyViewModel()
    lbKeyModel.setKeyID(lootBoxKey.keyID)
    lbKeyModel.setCount(lootBoxKey.count)
    lbKeyModel.keyType.setValue(lootBoxKey.keyType)
    lbKeyModel.setIconName(lootBoxKey.iconName)
    lbKeyModel.setUserName(lootBoxKey.userName)
    lbKeyModel.setOpenProbability(lootBoxKey.openProbability)
    return lbKeyModel


def fillLootBoxGuaranteedFrequencies(lootBox, vm):
    guaranteedFrequencies = lootBox.getGuaranteedFrequency(multiple=True)
    fillIntsArray(guaranteedFrequencies, vm.getGuaranteedFrequencies())


@replace_none_kwargs(guiLootBoxes=IGuiLootBoxesController)
def fillStatisticModel(rewards, rewardsList, lootbox, tooltipData, guiLootBoxes=None):
    rewards = splitBonuses(rewards)
    rewardsMapping = LootBox.getBonusGroupsWithBonuses(rewards)
    for bonusGroup in GROUP_PRIORITIES:
        bonuses = rewardsMapping.get(bonusGroup)
        if bonuses:
            statisticModel = StatisticRewardModel()
            statisticRewards = statisticModel.getRewards()
            statisticRewards.clear()
            lootboxCategory = lootbox.getCategory() if lootbox else None
            bonuses = sortBonuses(mergeBonuses(bonuses), guiLootBoxes.getBonusesOrder(lootboxCategory), sortFunc=getStatisticSortKeyFunc)
            bonuses = aggregateSimilarBonuses(bonuses)
            packBonusModelAndTooltipData(bonuses, statisticRewards, tooltipData, getStatisticsBonusPacker(), len(rewardsList))
            statisticModel.setRewardCount(calculateCountBonusItems(bonuses))
            statisticModel.setBonusGroup(bonusGroup)
            statisticRewards.invalidate()
            rewardsList.addViewModel(statisticModel)

    rewardsList.invalidate()
    return
