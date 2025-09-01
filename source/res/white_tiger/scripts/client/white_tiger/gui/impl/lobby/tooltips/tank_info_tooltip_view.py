# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/tank_info_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.tank_info_tooltip_view_model import TankInfoTooltipViewModel
from white_tiger.gui.doc_loaders.gui_settings_loader import getVehicleCharacteristics
from white_tiger.gui.white_tiger_gui_constants import VehicleCharacteristics
from gui.impl.pub import ViewImpl
from CurrentVehicle import g_currentVehicle
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.white_tiger_lobby.ttx.description
_IMG_PATH = R.images.white_tiger.gui.maps.icons.characteristicPanel

class TankInfoTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.mono.lobby.tooltips.tank_info_tooltip(), model=TankInfoTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(TankInfoTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankInfoTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            parameter = kwargs.get('parameter')
            if parameter is None:
                _logger.error('There is no parameter name in args to build tooltip.')
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
        vehicle = g_currentVehicle.item
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
