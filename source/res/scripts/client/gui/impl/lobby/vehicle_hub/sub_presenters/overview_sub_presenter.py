# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/overview_sub_presenter.py
from __future__ import absolute_import
import json
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.loadout.crew.slot_model import SlotModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleMechanicsArray
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.shared.event_dispatcher import showVehicleHubMechanicsVideo
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.overview_model import OverviewModel, BenefitsEnum

class OverviewSubPresenter(SubPresenterBase):

    @property
    def viewModel(self):
        return self.getViewModel()

    def setVehicleHubCtx(self, vhCtx):
        super(OverviewSubPresenter, self).setVehicleHubCtx(vhCtx)
        self.__updateModel()

    def initialize(self, vhCtx, *args, **kwargs):
        super(OverviewSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        self.__updateModel()

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        tooltipArgs = event.getArgument('tooltipArgs', None)
        if tooltipId == TooltipConstants.VEHICLE_PREVIEW_CREW_MEMBER:
            args = json.loads(tooltipArgs)
            slotIdx = args['slotIdx']
            tankmanID = args['tankmanID']
            if tankmanID == NO_TANKMAN:
                role = self.currentVehicle.descriptor.type.crewRoles[slotIdx][0]
            else:
                tankman = self._itemsCache.items.getTankman(tankmanID)
                role = tankman.role
                for idx, roles in enumerate(tankman.vehicleNativeDescr.type.crewRoles):
                    if roles and role == roles[0]:
                        slotIdx = idx
                        break

            args = [role,
             tankmanID,
             slotIdx,
             None,
             None,
             None,
             None,
             None]
            return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER, specialArgs=args)
        else:
            return super(OverviewSubPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        eventsTuple = super(OverviewSubPresenter, self)._getEvents()
        return eventsTuple + ((self.viewModel.onWatchMechanicsVideo, self.__onShowSpecialMechanicsVideo),)

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            model.setHistoricalReference(self.currentVehicle.fullDescription)
            model.setCustomDescription(self.currentVehicle.longDescriptionSpecial)
            self.__updateVehicleMechanics(model)
            self.__updateCrewMembers(model)
            benefits = model.getBenefits()
            benefits.clear()
            for benefit in self.__getBenefits():
                benefits.addString(str(benefit.value))

            benefits.invalidate()

    def __updateVehicleMechanics(self, model=None):
        if model is not None:
            fillVehicleMechanicsArray(model.getMechanics(), self.currentVehicle)
        return

    def __updateCrewMembers(self, model=None):
        if model is not None:
            crew = model.getCrew()
            crew.clear()
            for i, tman in self.currentVehicle.crew:
                crewSlot = SlotModel()
                crewSlot.setId(i)
                roles = crewSlot.getRoles()
                for role in self.currentVehicle.descriptor.type.crewRoles[i]:
                    roles.addString(role)

                crewSlot.setTankmanId(tman.invID if tman else NO_TANKMAN)
                crew.addViewModel(crewSlot)

            crew.invalidate()
        return

    def __getBenefits(self):
        veh = self.currentVehicle
        if not veh.isPremium:
            return []
        benefits = []
        if not veh.isOnlyForEpicBattles:
            benefits.append(BenefitsEnum.EXPERIENCE)
            if not veh.isSpecial:
                benefits.append(BenefitsEnum.CREDITS)
        if veh.isEarnCrystals:
            benefits.append(BenefitsEnum.BONDS)
        if not veh.isCrewLocked:
            benefits.append(BenefitsEnum.CREWS_TRAIN)
        equipmentsMap = {'builtinRepairkit': BenefitsEnum.REPAIR_KIT}
        for builtinEquipment in veh.descriptor.type.builtins:
            if builtinEquipment in equipmentsMap:
                benefits.append(equipmentsMap[builtinEquipment])

        return benefits

    @args2params(str)
    def __onShowSpecialMechanicsVideo(self, mechanicsName):
        showVehicleHubMechanicsVideo(mechanicsName)
