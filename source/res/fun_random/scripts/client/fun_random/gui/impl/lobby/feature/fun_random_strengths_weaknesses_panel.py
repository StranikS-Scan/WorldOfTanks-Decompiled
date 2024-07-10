# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_strengths_weaknesses_panel.py
import logging
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.doc_loaders import VehicleParameters
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_strengths_weaknesses_view_model import FunRandomStrengthsWeaknessesViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import hasVehicleConfig, packVehicleParameters
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
_logger = logging.getLogger(__name__)

class FunRandomStrengthsWeaknessesPanel(ViewImpl):

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.feature.FunRandomStrengthsWeaknessesView(), flags=flags, model=FunRandomStrengthsWeaknessesViewModel())
        super(FunRandomStrengthsWeaknessesPanel, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomStrengthsWeaknessesPanel, self).getViewModel()

    def clearModel(self):
        with self.viewModel.transaction() as model:
            packVehicleParameters(model.parameters, {}, VehicleParameters([], [], ''))

    def _onLoading(self, *args, **kwargs):
        super(FunRandomStrengthsWeaknessesPanel, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__invalidateAll),)

    def __invalidateAll(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            _logger.error('Missing current vehicle to show tooltip')
            return
        else:
            self.__packVehicleParameters(vehicle.name)
            return

    @hasVehicleConfig(abortAction='clearModel')
    def __packVehicleParameters(self, vehicleName, config=None):
        with self.viewModel.transaction() as model:
            packVehicleParameters(model.parameters, config.parameters, config.vehicles[vehicleName])
