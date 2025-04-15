# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/subdivision_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from items import vehicles
from gui.impl import backport
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.subdivision_tooltip_model import SubdivisionTooltipModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.tankset_item_model import TanksetItemModel
from gui.shared.gui_items.Vehicle import getIconResourceName
import logging
_logger = logging.getLogger(__name__)

class SubdivisionTooltip(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, divisionID):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.SubdivisionTooltip())
        settings.model = model = SubdivisionTooltipModel()
        super(SubdivisionTooltip, self).__init__(settings)
        currentFront = self.gameEventController.frontController.getSelectedFront()
        subDivision = self.gameEventController.frontController.getSubdivisionById(divisionID)
        model.setFrontName(currentFront.getName())
        model.setSubdivisionID(divisionID)
        model.setExperience(subDivision.getEXP())
        model.setMaxExperience(subDivision.getMaxExpForCurrentLevel())
        model.setLevel(subDivision.getProgressionLevel())
        self.__fillTankSet(model, subDivision)

    def __fillTankSet(self, model, subDivision):
        tankSetModel = model.getTankSet()
        tankSet = subDivision.getTanksIntCDByProgressionLevel(subDivision.getProgressionLevel())
        for vehicleCD in tankSet:
            vehType = vehicles.getItemByCompactDescr(vehicleCD)
            resId = R.images.gui.maps.icons.vehicle.dyn(getIconResourceName(vehType.name))()
            if resId == -1:
                _logger.error('no background image for tooltip for tank %s', vehType.name)
                resId = R.images.gui.maps.icons.vehicle.dyn('tank_empty')()
            iconPath = backport.image(resId)
            tankSetItemModel = TanksetItemModel()
            tankSetItemModel.setName(vehType.userString)
            tankSetItemModel.setIcon(iconPath)
            tankSetItemModel.setVehicleType(vehType.classTag)
            tankSetModel.addViewModel(tankSetItemModel)
