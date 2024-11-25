# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/tooltips/advent_calendar_all_rewards_tooltip.py
from advent_calendar.gui.feature.constants import PROGRESSION_REWARD_TYPE_TO_ICON
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.all_rewards_tooltip_view_model import AllRewardsTooltipViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.bonus_item_view_model import BonusItemViewModel
from advent_calendar.gui.impl.lobby.feature.bonus_grouper import QuestRewardsGroups
from advent_calendar.skeletons import IAdventCalendarController
from frameworks.wulf import ViewSettings, ViewFlags
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
_QUEST_REWARDS_GROUPS_ORDER = ((QuestRewardsGroups.PROGRESSION_REWARDS, ('tankwoman', 'lootBox')),
 (QuestRewardsGroups.CUSTOMIZATIONS, ('style', 'projectionDecal', 'crewSkin1')),
 (QuestRewardsGroups.BOOSTERS, ('booster_credits', 'booster_xp', 'booster_free_xp_and_crew_xp')),
 (QuestRewardsGroups.CREW_BONUSES_OR_X5, ('universal_brochure', 'recertificationForm', 'bonus_battle_task')),
 (QuestRewardsGroups.EXPERIMENTAL_EQUIPMENT_AND_COMPONENTS, ('expequipments_gift', 'equipCoin')),
 (QuestRewardsGroups.CURRENCIES_AND_PREMIUM, ('gold', 'credits', 'premium_plus_universal')))

def _rewardsGroupsSortOrder(bonusGroup):
    for idx, (group, bonuses) in enumerate(_QUEST_REWARDS_GROUPS_ORDER):
        if bonusGroup[0] == group:
            bonusGroup[1].sort(key=lambda b: bonuses.index(b) if b in bonuses else len(bonuses))
            return idx

    return len(_QUEST_REWARDS_GROUPS_ORDER)


class AdventCalendarAllRewardsTooltip(ViewImpl):
    __adventCalendarController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, *args):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarAllRewardsTooltip(), flags=ViewFlags.VIEW, model=AllRewardsTooltipViewModel(), args=args)
        super(AdventCalendarAllRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        rewardGroups = self.__adventCalendarController.getAdventCalendarGroupedQuestsRewards()
        if not rewardGroups:
            return
        formattedGroups = self.__processRewardGroups(rewardGroups)
        with self.viewModel.transaction() as tx:
            rewards = tx.getRewards()
            rewards.clear()
            for group, bonuses in sorted(formattedGroups.items(), key=_rewardsGroupsSortOrder):
                bonusItemModel = BonusItemViewModel()
                bonusItemModel.setType(group.value)
                valueModel = bonusItemModel.getValue()
                valueModel.clear()
                fillStringsArray(bonuses, valueModel)
                rewards.addViewModel(bonusItemModel)

            rewards.invalidate()
        super(AdventCalendarAllRewardsTooltip, self)._onLoading()

    @staticmethod
    def __processRewardGroups(rewardGroups):
        result = {}
        for group, bonuses in rewardGroups.items():
            if group == QuestRewardsGroups.PROGRESSION_REWARDS:
                rewards = [ PROGRESSION_REWARD_TYPE_TO_ICON[bonus] for bonus in bonuses if bonus in PROGRESSION_REWARD_TYPE_TO_ICON ]
            else:
                rewards = list(bonuses)
            if rewards:
                result[group] = rewards

        return result
