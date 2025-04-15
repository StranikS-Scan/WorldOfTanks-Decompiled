# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/fall_tanks_presenter.py
import typing
from fun_random.gui.battle_results.packers.fun_packers import FunRandomPersonalRewards, FunRandomPremiumPlus, FunRandomProgress
from fun_random.gui.battle_results.presenter import FunRandomBattleResultsPresenter
from fun_random.gui.battle_results.tooltips.earned_currency_tooltips import FunEarnedCurrencyTooltipsPacker
from fun_random.gui.shared.tooltips import TooltipType
from fall_tanks.gui.battle_results.fall_tanks_packers import FallTanksBattleInfo, FallTanksTeamStats, FallTanksPersonalEfficiency
from fall_tanks.gui.battle_results.tooltips.fall_tanks_total_efficiency_tooltips import FallTanksEfficiencyTooltipsPacker
from fall_tanks.gui.shared.event_dispatcher import showFallTanksBattleResults
if typing.TYPE_CHECKING:
    from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel

class FallTanksBattleResultsPresenter(FunRandomBattleResultsPresenter):
    __slots__ = ()
    _TOOLTIPS_PACKERS = {TooltipType.FUN_EFFICIENCY_PARAMETER: FallTanksEfficiencyTooltipsPacker,
     TooltipType.FUN_EARNED_CURRENCY: FunEarnedCurrencyTooltipsPacker}

    def saveStatsSorting(self, columnType, sortDirection):
        pass

    def packModel(self, model, *args, **kwargs):
        battleResults = self._battleResults
        FallTanksPersonalEfficiency.packModel(model.getEfficiency(), battleResults)
        FallTanksTeamStats.packModel(model.teamStats, battleResults)
        FallTanksBattleInfo.packModel(model.battleInfo, battleResults)
        FunRandomPersonalRewards.packModel(model.getRewards(), battleResults)
        FunRandomPremiumPlus.packModel(model.premiumPlus, battleResults)
        FunRandomProgress.packModel(model.progress, battleResults, *args, **kwargs)

    def _showBattleResults(self, arenaUniqueID):
        showFallTanksBattleResults(arenaUniqueID)
