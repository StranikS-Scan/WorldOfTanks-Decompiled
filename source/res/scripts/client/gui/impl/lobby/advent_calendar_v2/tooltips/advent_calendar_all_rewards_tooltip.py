# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/tooltips/advent_calendar_all_rewards_tooltip.py
from frameworks.wulf import ViewSettings, ViewFlags
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.advent_all_rewards_tooltip_view_model import AdventAllRewardsTooltipViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.bonus_item_view_model import BonusItemViewModel
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_bonus_groupper import QuestRewardsGroups
from gui.shared.advent_calendar_v2_consts import PROGRESSION_REWARD_TYPE_TO_ICON
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IAdventCalendarV2Controller
_QUEST_REWARDS_GROUPS_ORDER = ((QuestRewardsGroups.PROGRESSION_REWARDS, ('nyCoin', 'tankwoman', 'lootBox')),
 (QuestRewardsGroups.CUSTOMIZATIONS, ('style', 'projectionDecal', 'crewSkin1')),
 (QuestRewardsGroups.BOOSTERS, ('booster_credits', 'booster_xp', 'booster_free_xp_and_crew_xp')),
 (QuestRewardsGroups.CREW_BONUSES_OR_X5, ('brochure_random', 'recertificationForm', 'bonus_battle_task')),
 (QuestRewardsGroups.EXPERIMENTAL_EQUIPMENT_AND_COMPONENTS, ('expequipments_gift', 'equipCoin')),
 (QuestRewardsGroups.CURRENCIES_AND_PREMIUM, ('gold', 'credits', 'premium_plus_universal')))

def _rewardsGroupsSortOrder(bonusGroup):
    for idx, (group, bonuses) in enumerate(_QUEST_REWARDS_GROUPS_ORDER):
        if bonusGroup[0] == group:
            bonusGroup[1].sort(key=lambda b: bonuses.index(b) if b in bonuses else len(bonuses))
            return idx

    return len(_QUEST_REWARDS_GROUPS_ORDER)


class AdventCalendarAllRewardsTooltip(ViewImpl):
    __adventCalendarV2Controller = dependency.descriptor(IAdventCalendarV2Controller)

    def __init__(self, *args):
        settings = ViewSettings(R.views.lobby.advent_calendar.tooltips.AdventCalendarAllRewardsTooltip())
        settings.flags = ViewFlags.VIEW
        settings.model = AdventAllRewardsTooltipViewModel()
        settings.args = args
        super(AdventCalendarAllRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        rewardGroups = self.__adventCalendarV2Controller.getAdventCalendarGroupedQuestsRewards()
        if rewardGroups:
            self.__processRewardGroups(rewardGroups)
            with self.viewModel.transaction() as tx:
                rewards = tx.getRewards()
                rewards.clear()
                for group, bonuses in sorted(rewardGroups.items(), key=_rewardsGroupsSortOrder):
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
        for group, bonuses in rewardGroups.items():
            if group == QuestRewardsGroups.PROGRESSION_REWARDS:
                rewardGroups[group] = [ PROGRESSION_REWARD_TYPE_TO_ICON[bonus] for bonus in bonuses ]
            rewardGroups[group] = list(bonuses)
