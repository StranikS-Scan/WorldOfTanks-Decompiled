# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/stats_sub_presenter.py
from __future__ import absolute_import
import json
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.views.lobby.vehicle_hub.special_vehicle_param_model import SpecialVehicleParamModel
from gui.impl.lobby.hangar.sub_views.veh_param_helpers import formatParameterValue
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.stats_model import StatsModel
from gui.shared.gui_items import VEHICLE_ATTR_TO_KPI_NAME_MAP, KPI
from gui.shared.items_parameters.formatters import getMeasureUnitsForParameter
from gui.shared.items_parameters.comparator import PARAM_STATE
from shared_utils import findFirst

class StatsSubPresenter(SubPresenterBase):

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vhCtx, *args, **kwargs):
        super(StatsSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        currentVehicle = self.currentVehicle
        specialMechanic = findFirst(lambda mechanic: mechanic.isSpecial, currentVehicle.getVehicleMechanicItems())
        specialMechanicName = specialMechanic.guiName.value if specialMechanic is not None else ''
        specialStaticParams = specialMechanic.staticParams if specialMechanic is not None else ()
        with self.viewModel.transaction() as model:
            model.setSpecialMechanicName(specialMechanicName)
            specialParams = model.getSpecialMechanicParams()
            specialParams.clear()
            for paramName, data in specialStaticParams:
                paramState = (PARAM_STATE.NORMAL, None)
                item = {'id': paramName,
                 'value': formatParameterValue(paramName, data['value'], False, paramState, allowSmartRound=False),
                 'measureUnit': getMeasureUnitsForParameter(currentVehicle, paramName),
                 'template': data['template'],
                 'name': self.__getKpiName(paramName, data['kpiSign']),
                 'tooltipID': TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_ADVANCED_PARAMETERS}
                specialParams.addViewModel(self.__fillModel(SpecialVehicleParamModel(), item))

            specialParams.invalidate()
        return

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
