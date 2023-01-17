# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_points_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_points_view_model import BattlePassPointsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BattlePassPointsTooltip(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassPointsView())
        settings.model = BattlePassPointsViewModel()
        super(BattlePassPointsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassPointsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassPointsTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__setPointsInfo(model)

    def __setPointsInfo(self, model):
        model.rewardPoints.clearItems()
        model.vehiclesList.clearItems()
        rewardPoints = model.rewardPoints.getItems()
        for points in self.__battlePassController.getPerBattlePoints():
            item = RewardPointsModel()
            item.setTopCount(points.label)
            item.setPointsWin(points.winPoint)
            item.setPointsLose(points.losePoint)
            rewardPoints.addViewModel(item)

        vehiclesList = model.vehiclesList.getItems()
        rewardPoints.invalidate()
        vehiclesList.invalidate()
