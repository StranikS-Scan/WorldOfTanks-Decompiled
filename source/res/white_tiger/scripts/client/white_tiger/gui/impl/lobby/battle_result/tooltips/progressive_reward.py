# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/battle_result/tooltips/progressive_reward.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.progressive_reward_model import ProgressiveRewardModel
from gui.impl.pub import ViewImpl

class WtRewardsTooltip(ViewImpl):
    __slots__ = ('__sourceDataModel',)

    def __init__(self, sourceDataModel):
        contentResID = R.views.white_tiger.lobby.postbattle.tooltips.ProgressiveReward()
        settings = ViewSettings(contentResID)
        settings.model = ProgressiveRewardModel()
        super(WtRewardsTooltip, self).__init__(settings)
        self.__sourceDataModel = sourceDataModel

    def _finalize(self):
        super(WtRewardsTooltip, self)._finalize()
        self.__sourceDataModel = None
        return

    def _onLoading(self, *args, **kwargs):
        super(WtRewardsTooltip, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setCurrentStep(self.__sourceDataModel.getCurrentStep())
            model.setCurrentStepState(self.__sourceDataModel.getCurrentStepState())
            model.setMaxSteps(self.__sourceDataModel.getMaxSteps())
            model.setIsEnabled(self.__sourceDataModel.getIsEnabled())
