# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/daily_reroll_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.tooltips.daily_reroll_tooltip_model import DailyRerollTooltipModel
from gui.impl.pub import ViewImpl

class DailyRerollTooltip(ViewImpl):
    __slots__ = ('_timeLeft', '_rerollInterval')

    def __init__(self, timeLeft, rerollInterval):
        self._timeLeft = timeLeft
        self._rerollInterval = rerollInterval
        settings = ViewSettings(R.views.mono.user_missions.tooltips.daily_reroll_tooltip(), model=DailyRerollTooltipModel())
        super(DailyRerollTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyRerollTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.viewModel.setTimeLeft(self._timeLeft)
        self.viewModel.setRerollInterval(self._rerollInterval)
