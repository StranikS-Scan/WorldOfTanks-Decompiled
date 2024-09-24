# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/presenter.py
import typing
from fun_random.gui.battle_results.pbs_helpers import getEventID
from fun_random.gui.battle_results.packers.fun_packers import FunRandomPersonalEfficiency, FunRandomTeamStats, FunRandomBattleInfo, FunRandomPersonalRewards, FunRandomPremiumPlus, FunRandomProgress
from fun_random.gui.battle_results.tooltips.earned_currency_tooltips import FunEarnedCurrencyTooltipsPacker
from fun_random.gui.battle_results.tooltips.total_efficiency_tooltips import FunEfficiencyTooltipsPacker
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.shared.event_dispatcher import showFunRandomBattleResultsWindow
from fun_random.gui.shared.tooltips import TooltipType
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.presenters.base_presenter import BaseStatsPresenter
from gui.battle_results.presenters.base_constants import PresenterUpdateTypes
from gui.battle_results.presenters.packers.user_info import PersonalInfo
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
if typing.TYPE_CHECKING:
    from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel

class FunRandomBattleResultsPresenter(BaseStatsPresenter, FunSubModesWatcher):
    __slots__ = ()
    _TOOLTIPS_PACKERS = {TooltipType.FUN_EFFICIENCY_PARAMETER: FunEfficiencyTooltipsPacker,
     TooltipType.FUN_EARNED_CURRENCY: FunEarnedCurrencyTooltipsPacker}
    _CONTEXT_MENU_TYPE = CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER

    def __init__(self, args):
        super(FunRandomBattleResultsPresenter, self).__init__(args)
        self._updateCommandsMap = {PresenterUpdateTypes.XP_BONUS: self._updatePremiumBlock}

    def packModel(self, model, *args, **kwargs):
        battleResults = self._battleResults
        PersonalInfo.packModel(model, battleResults)
        FunRandomPersonalEfficiency.packModel(model.getEfficiency(), battleResults)
        FunRandomTeamStats.packModel(model.teamStats, battleResults)
        FunRandomBattleInfo.packModel(model.battleInfo, battleResults)
        FunRandomPersonalRewards.packModel(model.getRewards(), battleResults)
        FunRandomPremiumPlus.packModel(model.premiumPlus, battleResults)
        FunRandomProgress.packModel(model.progress, battleResults, *args, **kwargs)

    def _updatePremiumBlock(self, model, ctx, isFullUpdate):
        battleResults = self._battleResults
        FunRandomPersonalRewards.packModel(model.getRewards(), battleResults)
        FunRandomPremiumPlus.updateModel(model.premiumPlus, battleResults, ctx, isFullUpdate)

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults and self._funRandomCtrl.isEnabled():
            subMode = self.getSubMode(getEventID(self._battleResults.reusable))
            if subMode is not None and subMode.isAvailable():
                showFunRandomBattleResultsWindow(arenaUniqueID)
                return
        pushNoBattleResultsDataMessage()
        return
