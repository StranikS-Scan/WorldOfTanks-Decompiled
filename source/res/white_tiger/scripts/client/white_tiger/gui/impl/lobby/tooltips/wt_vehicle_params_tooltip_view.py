# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_vehicle_params_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_vehicle_params_tooltip_view_model import WtVehicleParamsTooltipViewModel
from white_tiger.gui.impl.lobby.wt_event_constants import VehicleCharacteristics
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.event.ttx.description
_IMG_PATH = R.images.white_tiger.gui.maps.icons.characteristicPanel

class WtVehicleParamsTooltipView(ViewImpl):
    __slots__ = ()
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.VehicleParamsTooltipView(), model=WtVehicleParamsTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtVehicleParamsTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtVehicleParamsTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            parameter = kwargs.get('parameter')
            if parameter is None:
                _logger.error('There is not parameter name in args to build tooltip.')
                return
            aspect = self.__getAspect(parameter)
            if aspect is None:
                _logger.error('Parameter %s is absent in vehicle characteristics', parameter)
                return
            model.setParameter(parameter)
            model.setIcon(_IMG_PATH.dyn(aspect.value).dyn(parameter)())
            model.setDescription(_STR_PATH.dyn(parameter)())
        return

    def __getAspect(self, parameter):
        vehicle = self.__prebattleVehicle.item
        if vehicle is None:
            return
        else:
            info = getVehicleCharacteristics().get(vehicle.name)
            if info is not None:
                if parameter in info.pros:
                    return VehicleCharacteristics.PROS
                if parameter in info.cons:
                    return VehicleCharacteristics.CONS
            return
