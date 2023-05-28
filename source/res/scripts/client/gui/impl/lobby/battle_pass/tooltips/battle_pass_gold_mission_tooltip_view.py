# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_gold_mission_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_gold_mission_tooltip_view_model import BattlePassGoldMissionTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache

class BattlePassGoldMissionTooltipView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, token):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassGoldMissionTooltipView())
        settings.model = BattlePassGoldMissionTooltipViewModel()
        super(BattlePassGoldMissionTooltipView, self).__init__(settings)
        self.__token = token

    @property
    def viewModel(self):
        return super(BattlePassGoldMissionTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        goldAmount = first(first(self.__eventsCache.getAllQuests(lambda q: q.getData().get('requiredToken') == self.__token).values()).getBonuses(Currency.GOLD)).getValue()
        _, days = first((tokenData for token, tokenData in self.__eventsCache.questsProgress.getTokensData().iteritems() if token == self.__token))
        with self.viewModel.transaction() as tx:
            tx.setCount(goldAmount)
            tx.setDays(days)
