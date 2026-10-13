# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/tooltips/session_progress_rewards_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.tooltips.session_progress_rewards_tooltip_model import SessionProgressRewardsTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ISessionProgressRewardsController

class SessionProgressRewardsTooltip(ViewImpl):
    __slots__ = ()
    __sessionProgressRewardsController = dependency.descriptor(ISessionProgressRewardsController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.daily.tooltips.SessionProgressRewardsTooltip())
        settings.flags = ViewFlags.VIEW
        settings.model = SessionProgressRewardsTooltipModel()
        super(SessionProgressRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SessionProgressRewardsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SessionProgressRewardsTooltip, self)._onLoading(*args, **kwargs)
        controller = self.__sessionProgressRewardsController
        isRewardReceivedToday = controller.isRewardWasReceivedToday
        isProgressionCompleted = controller.currentStep > controller.finalStep
        self.viewModel.setIsCompleted(isRewardReceivedToday)
        self.viewModel.setIsProgressionCompleted(isProgressionCompleted)
