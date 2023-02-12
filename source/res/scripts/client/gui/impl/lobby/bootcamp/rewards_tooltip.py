# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/rewards_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.bootcamp.bootcamp_rewards_tooltip_model import BootcampRewardsTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class RewardsTooltip(ViewImpl):
    __slots__ = ()
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, isNeedAwarding):
        settings = ViewSettings(R.views.lobby.bootcamp.RewardsTooltip(), model=BootcampRewardsTooltipModel())
        super(RewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RewardsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RewardsTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsNeedAwarding(self.__bootcampController.needAwarding())
