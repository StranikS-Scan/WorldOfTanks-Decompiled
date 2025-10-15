# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/tooltips/battle_matters_token_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.tooltips.battle_matters_token_tooltip_view_model import BattleMattersTokenTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.shared import IItemsCache

class BattleMattersTokenTooltipView(ViewImpl):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_matters.tooltips.BattleMattersTokenTooltipView())
        settings.model = BattleMattersTokenTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattleMattersTokenTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersTokenTooltipView, self).getViewModel()

    def _onLoading(self, rewardToken):
        super(BattleMattersTokenTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            level = self.__battleMattersController.getDelayedRewardVehiclesLevel(rewardToken)
            model.setVehiclesLevel(level)
            if self.__battleMattersController.isFinished():
                model.setEndDate(self.__battleMattersController.getDelayedRewardExpirationTime())
