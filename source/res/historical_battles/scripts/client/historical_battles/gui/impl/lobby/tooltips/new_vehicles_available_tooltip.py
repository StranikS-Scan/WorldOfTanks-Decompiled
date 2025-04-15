# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/new_vehicles_available_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from items import vehicles
from gui.impl import backport
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.new_vehicles_available_tooltip_model import NewVehiclesAvailableTooltipModel, NewVehicleItemModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.shared.gui_items.Vehicle import getIconResourceName
import logging
_logger = logging.getLogger(__name__)

class NewVehiclesAvailableTooltip(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, divisionID):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.NewVehiclesAvailableTooltip())
        settings.model = NewVehiclesAvailableTooltipModel()
        super(NewVehiclesAvailableTooltip, self).__init__(settings)
        subDivision = self.gameEventController.frontController.getSubdivisionById(divisionID)
        self.__fillVehicles(subDivision)

    @property
    def viewModel(self):
        return super(NewVehiclesAvailableTooltip, self).getViewModel()

    def __fillVehicles(self, subDivision):
        with self.viewModel.transaction() as tx:
            vehiclesModel = tx.getVehicles()
            vehiclesModel.clear()
            vehiclesSet = subDivision.getTanksIntCDByProgressionLevel(subDivision.getProgressionLevel())
            for vehicleCD in vehiclesSet:
                vehType = vehicles.getItemByCompactDescr(vehicleCD)
                resId = R.images.gui.maps.icons.vehicle.small.dyn(getIconResourceName(vehType.name))()
                if resId == -1:
                    _logger.error('no background image for tooltip for tank %s', vehType.name)
                    resId = R.images.gui.maps.icons.vehicle.small.dyn('tank_empty')()
                iconPath = backport.image(resId)
                vehModel = NewVehicleItemModel()
                vehModel.setName(vehType.userString)
                vehModel.setIcon(iconPath)
                vehModel.setVehicleType(vehType.classTag)
                vehiclesModel.addViewModel(vehModel)

            vehiclesModel.invalidate()
