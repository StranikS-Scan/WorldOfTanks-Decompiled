# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/vehicle_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from portal.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_crew import VehicleCrew
from portal.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_tooltip_model import VehicleTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl import backport
from portal.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_ttx import VehicleTtx
from portal.skeletons.portal_event_controller import IPortalEventController
from portal_constants import PORTAL_VEHICLE_TOOLTIP_DATA

class VehicleTooltip(ViewImpl):
    __slots__ = ('_vehicleId',)
    __portalController = dependency.descriptor(IPortalEventController)

    def __init__(self, vehicleId):
        settings = ViewSettings(R.views.portal.lobby.tooltips.VehicleTooltip())
        settings.model = VehicleTooltipModel()
        self._vehicleId = vehicleId
        super(VehicleTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            self.__fillModel(vm)

    def __fillModel(self, model):
        vehicle = self.__portalController.getPortalVehicleByInvID(self._vehicleId)
        model.setVehicleName(vehicle.userName)
        model.setVehicleType(vehicle.type)
        text = backport.text(R.strings.portal_tooltips.vehicle.ttx.description.dyn('c_' + str(vehicle.intCD))())
        model.setVehicleDescription(text)
        vehicleTooltipData = PORTAL_VEHICLE_TOOLTIP_DATA[vehicle.intCD]
        ttx = model.vehicleTtx
        ttx.setDamage(vehicleTooltipData['damage'])
        ttx.setMobility(vehicleTooltipData['mobility'])
        ttx.setArmor(vehicleTooltipData['armor'])
        ttx.setReload(vehicleTooltipData['reload'])
        ttx.setHp(vehicleTooltipData['hp'])
        crew = model.vehicleCrew
        crewID = vehicleTooltipData['crewID']
        crew.setId(crewID)
        crew.setName(backport.text(R.strings.portal_tooltips.vehicle.crew.name.dyn(crewID.value)()))
        crew.setDescription(backport.text(R.strings.portal_tooltips.vehicle.crew.description.dyn(crewID.value)()))
