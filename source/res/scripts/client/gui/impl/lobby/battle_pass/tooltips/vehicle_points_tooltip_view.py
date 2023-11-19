# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/vehicle_points_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.vehicle_points_tooltip_view_model import VehiclePointsTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.formatters.invites import getPreQueueName
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache

class VehiclePointsTooltipView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.VehiclePointsTooltipView())
        settings.model = VehiclePointsTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(VehiclePointsTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehiclePointsTooltipView, self).getViewModel()

    def _onLoading(self, intCD, *args, **kwargs):
        with self.viewModel.transaction() as model:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            isSpecial = self.__battlePassController.isSpecialVehicle(intCD)
            currentPoints, limitPoints = self.__battlePassController.getVehicleProgression(intCD)
            pointsReward = self.__battlePassController.getVehicleCapBonus(intCD)
            gameMode = getSupportedCurrentArenaBonusType()
            commonPerBattlePoints = {points.label:(points.winPoint, points.losePoint) for points in self.__battlePassController.getPerBattlePoints(gameMode=gameMode)}
            items = model.rewardPoints.getItems()
            for points in self.__battlePassController.getPerBattlePoints(vehCompDesc=intCD, gameMode=gameMode):
                isHighlighted = True
                if points.label in commonPerBattlePoints:
                    commonWinPoint, commonLosePoint = commonPerBattlePoints[points.label]
                    isHighlighted = commonWinPoint < points.winPoint or commonLosePoint < points.losePoint
                item = RewardPointsModel()
                item.setTopCount(points.label)
                item.setPointsWin(points.winPoint)
                item.setPointsLose(points.losePoint)
                item.setIsSpecial(isHighlighted)
                items.addViewModel(item)

            model.setVehicleName(vehicle.shortUserName)
            model.setVehicleLevel(vehicle.level)
            model.setVehicleType(vehicle.type)
            model.setIsSpecialVehicle(isSpecial)
            model.setPointsCurrent(currentPoints)
            model.setPointsTotal(limitPoints)
            model.setPointsReward(pointsReward)
            model.setIsElite(vehicle.isFullyElite)
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher:
                queueType = dispatcher.getEntity().getQueueType()
                if queueType:
                    model.setBattleType(getPreQueueName(queueType, True))
