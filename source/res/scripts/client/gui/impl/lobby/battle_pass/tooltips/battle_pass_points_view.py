# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_points_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_points_view_model import BattlePassPointsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.vehicle_item_model import VehicleItemModel
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
        perBattlePoints = self.__battlePassController.getPerBattlePoints()
        specialVehicles = self.__battlePassController.getSpecialVehicles()
        rewardPoints = model.rewardPoints.getItems()
        for _, (label, winPoint, losePoint) in enumerate(perBattlePoints):
            item = RewardPointsModel()
            item.setTopCount(label)
            item.setPointsWin(winPoint)
            item.setPointsLose(losePoint)
            rewardPoints.addViewModel(item)

        vehiclesList = model.vehiclesList.getItems()
        for intCD in specialVehicles:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            pointsDiff = self.__battlePassController.getPointsDiffForVehicle(intCD)
            if vehicle is None or pointsDiff.textID == 0:
                _logger.warning('No vehicle or points data found for CD: %s', str(intCD))
                continue
            item = VehicleItemModel()
            item.setVehicleType(vehicle.type)
            item.setVehicleLevel(vehicle.level)
            item.setVehicleName(vehicle.userName)
            item.setVehicleBonus(pointsDiff.bonus)
            item.setVehicleTop(pointsDiff.top)
            item.setTextResource(backport.text(pointsDiff.textID))
            vehiclesList.addViewModel(item)

        rewardPoints.invalidate()
        vehiclesList.invalidate()
        return
