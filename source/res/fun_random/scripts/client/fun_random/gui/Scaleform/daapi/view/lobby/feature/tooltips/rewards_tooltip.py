# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/feature/tooltips/rewards_tooltip.py
from fun_random.gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import FunCurtailingAwardsComposer, getFunAwardsPacker
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.lobby.common.fun_view_helpers import sortFunProgressionBonuses
from gui.server_events.bonuses import mergeBonuses
from gui.shared.tooltips.quests import AdditionalAwardTooltipData
_MAX_BONUS_COUNT = 8

class FunRandomRewardsTooltip(AdditionalAwardTooltipData, FunProgressionWatcher):

    @hasActiveProgression(defReturn=[])
    def _packBlocks(self, *args, **kwargs):
        formatter = FunCurtailingAwardsComposer(_MAX_BONUS_COUNT, getFunAwardsPacker(isSpecial=True))
        progression = self.getActiveProgression()
        if progression.isInUnlimitedProgression:
            bonuses = progression.unlimitedProgression.bonuses
        else:
            bonuses = progression.getAllBonuses()
        displayBonuses = [ b for b in mergeBonuses(bonuses) if b.isShowInGUI() ]
        formattedBonuses = formatter.getShortBonusesData(sortFunProgressionBonuses(displayBonuses))
        return super(FunRandomRewardsTooltip, self)._packBlocks(*formattedBonuses)
