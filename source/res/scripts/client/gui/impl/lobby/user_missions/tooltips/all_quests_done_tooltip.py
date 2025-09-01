# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/all_quests_done_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.tooltips.all_quests_done_tooltip_model import AllQuestsDoneTooltipModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_helpers import EventInfoModel

class AllQuestsDoneTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.all_quests_done_tooltip())
        settings.model = AllQuestsDoneTooltipModel()
        super(AllQuestsDoneTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AllQuestsDoneTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self._fillViewModel()
        super(AllQuestsDoneTooltip, self)._onLoading()

    def _fillViewModel(self):
        dailyResetTimeDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        with self.viewModel.transaction() as vm:
            vm.setCountdown(dailyResetTimeDelta)
