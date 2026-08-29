# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/stats_sub_presenter.py
from __future__ import absolute_import
import json
import logging
from constants import SHELL_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.special_vehicle_param_model import SpecialVehicleParamModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.special_shell_param_model import SpecialShellParamModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.shell_model import ShellModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.stats_model import StatsModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleMechanicModel, clearVehicleMechanicModel
from gui.impl.lobby.hangar.sub_views.veh_param_helpers import formatParameterValue
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.shared.gui_items import VEHICLE_ATTR_TO_KPI_NAME_MAP, KPI
from gui.shared.items_parameters.formatters import getMeasureUnitsForParameter
from gui.shared.items_parameters.functions import getShellParamsSwitcherModifiedShells
from gui.shared.items_parameters.comparator import PARAM_STATE
from shared_utils import first
from vehicles.mechanics.mechanic_constants import VehicleMechanic
SUPPORTED_SHELL_TYPES = {VehicleMechanic.SHELL_PARAMS_SWITCHER: (SHELL_TYPES.HOLLOW_CHARGE,
                                         SHELL_TYPES.HIGH_EXPLOSIVE,
                                         SHELL_TYPES.ARMOR_PIERCING,
                                         SHELL_TYPES.ARMOR_PIERCING_CR)}
_logger = logging.getLogger(__name__)

class StatsSubPresenter(SubPresenterBase):

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vhCtx, *args, **kwargs):
        super(StatsSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        currentVehicle = self.currentVehicle
        mechanics = sorted((m for m in currentVehicle.getVehicleMechanicItems() if m.priority >= VehicleMechanicModel.MIN_SPECIAL_PRIORITY), key=lambda m: m.priority, reverse=True)
        specialMechanic = first(mechanics)
        if specialMechanic is None:
            with self.viewModel.transaction() as model:
                clearVehicleMechanicModel(model.specialMechanic)
            return
        else:
            with self.viewModel.transaction() as model:
                fillVehicleMechanicModel(model.specialMechanic, specialMechanic)
                specialParams = model.getSpecialMechanicParams()
                specialParams.clear()
                for paramName, data in specialMechanic.staticParams:
                    paramState = (PARAM_STATE.NORMAL, None)
                    item = {'id': paramName,
                     'value': formatParameterValue(paramName, data['value'], False, paramState, allowSmartRound=False),
                     'measureUnit': getMeasureUnitsForParameter(currentVehicle, paramName),
                     'template': data['template'],
                     'name': self.__getKpiName(paramName, data['kpiSign']),
                     'tooltipID': TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_ADVANCED_PARAMETERS}
                    specialParams.addViewModel(self.__fillModel(SpecialVehicleParamModel(), item))

                specialParams.invalidate()
                shellParams = model.getShellParams()
                shellParams.clear()
                items = SpecialShellParamModel()
                if self.__fillViewModelsArray(items.getShellArray(), specialMechanic.mechanic):
                    shellParams.set(specialMechanic.mechanic.value, items)
            return

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(StatsSubPresenter, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL:
            currentVehicle = self.currentVehicle
            vehicleId = int(event.getArgument('vehicleId', 0))
            if currentVehicle is None or vehicleId != currentVehicle.intCD:
                return
            shellCD = int(event.getArgument('shellCD', 0))
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(shellCD,
             0,
             None,
             None,
             vehicleId))
        else:
            return

    def __fillViewModelsArray(self, shellArrayModel, mechanic):
        shellArrayModel.clear()
        modifiedShells = getShellParamsSwitcherModifiedShells(self.currentVehicle.descriptor)
        supportedShellType = SUPPORTED_SHELL_TYPES.get(mechanic, [])
        for shell in self.currentVehicle.shells.layout.getItems():
            if shell.intCD in modifiedShells:
                if shell.type in supportedShellType:
                    sp = ShellModel()
                    sp.setIntCD(shell.intCD)
                    sp.setItemType(shell.type)
                    sp.setIsPremium(shell.descriptor.isGold)
                    shellArrayModel.addViewModel(sp)
                else:
                    _logger.error('"%s" mechanic do not support "%s" shell type', mechanic.value, shell.type)

        shellArrayModel.invalidate()
        return shellArrayModel

    def __getKpiName(self, paramName, kpiSign):
        kpiName = VEHICLE_ATTR_TO_KPI_NAME_MAP.get(paramName, paramName)
        return json.dumps({'name': kpiName,
         'key': kpiSign}) if KPI.Name.hasValue(kpiName) else None

    def __fillModel(self, model, params):
        for k, v in params.items():
            setter = getattr(model, 'set{}{}'.format(k[0].upper(), k[1:]), None)
            if setter is not None:
                setter(v)

        return model
