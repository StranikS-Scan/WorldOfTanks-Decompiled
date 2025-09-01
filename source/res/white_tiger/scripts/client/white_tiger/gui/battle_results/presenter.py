# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/presenter.py
import typing
import BigWorld
from gui import SystemMessages
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.presenters.packers.tooltips.efficiency_tooltips import EfficiencyTooltipsPacker
from gui.battle_results.presenters.packers.user_info import PersonalInfo
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty
from gui.shared.notifications import NotificationPriorityLevel
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from white_tiger.gui.shared.tooltips import TooltipType
from white_tiger.gui.battle_results.packers.white_tiger_packers import WhiteTigerPersonalEfficiency, WhiteTigerTeamStats, WhiteTigerBattleInfo, WhiteTigerPersonalRewards, WhiteTigerPremiumPlus, WTSimpleQuestUIDataPacker
from white_tiger.gui.battle_results.tooltips.earned_currency_tooltips import WTEarnedCurrencyTooltips
from white_tiger.gui.battle_results.base_presenter import BaseStatsPresenter
from white_tiger.gui.battle_results.base_constants import PresenterUpdateTypes
from white_tiger.gui.shared.event_dispatcher import showWhiteTigerBattleResultView
if typing.TYPE_CHECKING:
    from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.white_tiger_results_view_model import WhiteTigerResultsViewModel

def showErrorMessage():
    SystemMessages.pushI18nMessage(backport.text(R.strings.white_tiger_lobby.notifications.battleResults.disableInQueue()), type=SystemMessages.SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)


class WhiteTigerBattleResultsPresenter(BaseStatsPresenter):
    __slots__ = ('_tooltipData',)
    _TOOLTIPS_PACKERS = {TooltipType.WHITE_TIGER_EFFICIENCY_PARAMETER: EfficiencyTooltipsPacker,
     TooltipType.WHITE_TIGER_EARNED_CURRENCY: WTEarnedCurrencyTooltips}
    _CONTEXT_MENU_TYPE = CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER

    def __init__(self, args):
        super(WhiteTigerBattleResultsPresenter, self).__init__(args)
        self._updateCommandsMap = {PresenterUpdateTypes.XP_BONUS: self._updatePremiumBlock}
        self._tooltipData = {}

    def packModel(self, model, tooltipData=None):
        self._tooltipData = {} if tooltipData is None else tooltipData
        battleResults = self._battleResults
        PersonalInfo.packModel(model, battleResults)
        WhiteTigerPersonalEfficiency.packModel(model.getEfficiency(), battleResults)
        WhiteTigerTeamStats.packModel(model.teamStats, battleResults)
        WhiteTigerBattleInfo.packModel(model.battleInfo, battleResults)
        WhiteTigerPersonalRewards.packModel(model.getRewards(), battleResults, tooltipData)
        WhiteTigerPremiumPlus.packModel(model.premiumPlus, battleResults)
        WTSimpleQuestUIDataPacker().fillQuests(model, battleResults.results[_RECORD.PERSONAL]['avatar']['team'])
        return

    def _updatePremiumBlock(self, model, ctx, isFullUpdate):
        battleResults = self._battleResults
        WhiteTigerPersonalRewards.packModel(model.getRewards(), battleResults, self._tooltipData)
        WhiteTigerPremiumPlus.updateModel(model.premiumPlus, battleResults, ctx, isFullUpdate)

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onResultsPosted(self, arenaUniqueID):
        if WhiteTigerBattleResultsPresenter.prbEntity.isInQueue():
            BigWorld.callback(0, showErrorMessage)
            return
        if self._battleResults:
            showWhiteTigerBattleResultView(arenaUniqueID)
            return
        pushNoBattleResultsDataMessage()
