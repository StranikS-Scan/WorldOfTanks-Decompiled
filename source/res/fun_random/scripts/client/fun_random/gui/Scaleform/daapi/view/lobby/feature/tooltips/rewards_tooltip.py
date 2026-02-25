# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/feature/tooltips/rewards_tooltip.py
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from gui.shared.tooltips.quests import AdditionalAwardTooltipData
from fun_random.gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import FunCurtailingAwardsComposer, getFunAwardsPacker
from gui.server_events.bonuses import mergeBonuses
_MAX_BONUS_COUNT = 8
_ALL_BONUSES_ORDER = ('lootBoxToken', 'crystal', 'premium_plus', 'freeXP', 'battlePassPoints', 'credits', 'items')

class FunRandomRewardsTooltip(AdditionalAwardTooltipData, FunProgressionWatcher):

    @hasActiveProgression(defReturn=[])
    def _packBlocks(self, *args, **kwargs):
        formatter = FunCurtailingAwardsComposer(_MAX_BONUS_COUNT, getFunAwardsPacker())
        bonuses = self.getActiveProgression().getAllBonuses()
        bonuses.sort(key=self._keySortOrder)
        formattedBonuses = formatter.getShortBonusesData(mergeBonuses(bonuses))
        return super(FunRandomRewardsTooltip, self)._packBlocks(*formattedBonuses)

    @classmethod
    def _keySortOrder(cls, bonus):
        return _ALL_BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _ALL_BONUSES_ORDER else len(_ALL_BONUSES_ORDER)
