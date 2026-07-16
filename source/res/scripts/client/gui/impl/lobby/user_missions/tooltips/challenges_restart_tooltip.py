# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/challenges_restart_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.tooltips.challenges_restart_tooltip_model import ChallengesRestartTooltipModel
from gui.impl.pub import ViewImpl
from shared_utils import first

class ChallengesRestartTooltip(ViewImpl):

    def __init__(self, challenge):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.challenges_restart_tooltip())
        settings.model = ChallengesRestartTooltipModel()
        super(ChallengesRestartTooltip, self).__init__(settings)
        self.__challenge = challenge

    @property
    def viewModel(self):
        return super(ChallengesRestartTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChallengesRestartTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel as model:
            model.setFreeRestarts(self.__challenge.freeRestartsPerCompletion)
            model.setUsedFreeRestarts(self.__challenge.usedFreeRestarts)
            currency, cost = first(self.__challenge.restartPrice.items())
            model.setCurrency(currency)
            model.setRestartCost(cost)
