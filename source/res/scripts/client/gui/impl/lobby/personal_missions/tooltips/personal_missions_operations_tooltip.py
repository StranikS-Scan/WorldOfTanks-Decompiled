# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/personal_missions_operations_tooltip.py
from typing import Dict
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.personal_missions_operations_tooltip_model import PersonalMissionsOperationsTooltipModel, MissionStatus
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_operations_tooltip_branches_model import Pm3OperationsTooltipBranchesModel
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_operations_tooltip_rewards_model import Pm3OperationsTooltipRewardsModel
from gui.server_events.event_items import PMOperation
from gui.shared.gui_items import Vehicle
from helpers import dependency
from skeletons.gui.game_control import IPersonalMissionsController
from skeletons.gui.shared import IItemsCache
from helpers import int2roman
from frameworks.wulf import Array

class PersonalMissionsOperationsTooltip(ViewImpl):
    __slots__ = ('__operationId',)
    __personalMissionsCtrl = dependency.descriptor(IPersonalMissionsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, operationId):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsOperationsTooltipModel()
        self.__operationId = operationId
        super(PersonalMissionsOperationsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsOperationsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsOperationsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    @staticmethod
    def __getMissionStatus(operation):
        if not (operation.isDisabled() or operation.isUnlocked()):
            return MissionStatus.DISABLED
        if not operation.hasRequiredVehicles():
            return MissionStatus.DISABLEDLEVEL
        if operation.isInProgress():
            return MissionStatus.ACTIVE
        if operation.isFullCompleted():
            return MissionStatus.COMPLETEDPERFECTLY
        return MissionStatus.COMPLETED if operation.isCompleted() else MissionStatus.AVAILABLE

    def __updateModel(self, model):
        ctrl = self.__personalMissionsCtrl
        operation = ctrl.getOperationById(self.__operationId)
        model.setOperationID(self.__operationId)
        model.setMissionStatus(self.__getMissionStatus(operation))
        model.setName(operation.getShortUserName())
        minVehLevel, maxVehLevel = ctrl.getMinMaxVehicleLevelForOperation(operation)
        model.setFrom(int2roman(minVehLevel))
        model.setTo(int2roman(maxVehLevel))
        branchesModel = model.getBranches()
        model.setPrevOperationName(ctrl.getPreviousOperationName(self.__operationId))
        chainsData = ctrl.getOperationChainsData(operation)
        for _, data in chainsData.iteritems():
            self.__addPm3OperationsTooltipBranchesModel(branchesModel, data)

        branchesModel.invalidate()
        rewardsModel = model.getRewards()
        if not operation.isCompleted():
            self.__addVehicleRewards(rewardsModel, operation.getVehicleBonus())
        self.__addBadgesRewards(rewardsModel, operation)
        rewardsModel.invalidate()

    @staticmethod
    def __addPm3OperationsTooltipBranchesModel(branchesModel, data):
        nextModel = Pm3OperationsTooltipBranchesModel()
        nextModel.setName(data['name'])
        nextModel.setCompleted(data['completed'])
        nextModel.setAll(data['size'])
        branchesModel.addViewModel(nextModel)

    @staticmethod
    def __addVehicleRewards(rewardsModel, vehicle):
        rewardModel = Pm3OperationsTooltipRewardsModel()
        if vehicle is not None:
            rewardModel.setIcon(vehicle.iconBonus)
            rewardModel.setName(vehicle.userName)
        rewardsModel.addViewModel(rewardModel)
        return

    def __addBadgesRewards(self, rewardsModel, operation):
        ctrl = self.__personalMissionsCtrl
        isHonor = operation.isCompleted() and not operation.isFullCompleted()
        badges = ctrl.getAddBadgesForOperation(operation) if isHonor else ctrl.getMainBadgesForOperation(operation)
        if not badges:
            return
        for badge in badges:
            rewardModel = Pm3OperationsTooltipRewardsModel()
            rewardModel.setIcon(badge.getBonusIcon())
            rewardsModel.addViewModel(rewardModel)
