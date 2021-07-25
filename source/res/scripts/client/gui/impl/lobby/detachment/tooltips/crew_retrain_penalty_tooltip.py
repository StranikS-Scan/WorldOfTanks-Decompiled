# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/crew_retrain_penalty_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.crew_retrain_penalty_item import CrewRetrainPenaltyItem
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.crew_retrain_penalty_tooltip_model import CrewRetrainPenaltyTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.serializers import makePercentLoss
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class CrewRetrainPenaltyTooltip(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, operationID, vehIntCD, crewIDs, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.CrewRetrainPenaltyTooltip())
        settings.model = CrewRetrainPenaltyTooltipModel()
        super(CrewRetrainPenaltyTooltip, self).__init__(settings, *args, **kwargs)
        self._operationID = operationID
        self._vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
        self._crewIDs = crewIDs

    def _onLoading(self, *args, **kwargs):
        vm = self.getViewModel()
        items = vm.getItems()
        vehicleType = self._vehicle.type
        trainingCostsActual = self.itemsCache.items.shop.tankmanCost[int(self._operationID)]
        minRoleLevel = trainingCostsActual['roleLevel']
        baseRoleLoss = trainingCostsActual['baseRoleLoss']
        classChangeRoleLoss = trainingCostsActual['classChangeRoleLoss']
        totalPenaltyXP = 0
        for tmanInvID in self._crewIDs:
            tman = self.itemsCache.items.getTankman(tmanInvID)
            if not tman:
                continue
            sameVehicleType = vehicleType == tman.vehicleNativeType
            if sameVehicleType:
                lossLevel = tman.descriptor.calculateRealDecreaseXP(baseRoleLoss, minRoleLevel)
                percentLoss = makePercentLoss(minRoleLevel, sameVehicleType)
            else:
                lossLevel = tman.descriptor.calculateRealDecreaseXP(classChangeRoleLoss, minRoleLevel)
                percentLoss = makePercentLoss(minRoleLevel, sameVehicleType)
            totalPenaltyXP += lossLevel
            item = CrewRetrainPenaltyItem()
            item.setIcon(R.images.gui.maps.icons.tankmen.roles.medium.dyn(tman.descriptor.role)())
            item.setRole(R.strings.item_types.tankman.roles.dyn(tman.descriptor.role)())
            item.setPercents(-percentLoss)
            item.setValue(-lossLevel)
            items.addViewModel(item)

        vm.setTotal(-totalPenaltyXP)
