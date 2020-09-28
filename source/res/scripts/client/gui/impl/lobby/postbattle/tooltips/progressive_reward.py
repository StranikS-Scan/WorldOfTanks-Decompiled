# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/tooltips/progressive_reward.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.progressive_reward_model import ProgressiveRewardModel
from gui.impl.pub import ViewImpl

class RewardsTooltip(ViewImpl):
    __slots__ = ('__sourceDataModel',)

    def __init__(self, sourceDataModel):
        contentResID = R.views.lobby.postbattle.tooltips.ProgressiveReward()
        settings = ViewSettings(contentResID)
        settings.model = ProgressiveRewardModel()
        super(RewardsTooltip, self).__init__(settings)
        self.__sourceDataModel = sourceDataModel

    def _finalize(self):
        super(RewardsTooltip, self)._finalize()
        self.__sourceDataModel = None
        return

    def _onLoading(self, *args, **kwargs):
        super(RewardsTooltip, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setCurrentStep(self.__sourceDataModel.getCurrentStep())
            model.setCurrentStepState(self.__sourceDataModel.getCurrentStepState())
            model.setMaxSteps(self.__sourceDataModel.getMaxSteps())
            model.setIsEnabled(self.__sourceDataModel.getIsEnabled())
