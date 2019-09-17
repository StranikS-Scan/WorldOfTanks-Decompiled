# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/tech_parameters_cmp.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.lobby.race.user_tech_parameter_model import UserTechParameterModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from racing_event_config import RacingVehicles

class TechParametersComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return TechParametersView()


class TechParametersView(ViewImpl):

    def __init__(self, *args, **kwargs):
        super(TechParametersView, self).__init__(R.views.lobby.race.tech_parameters_cmp.TechParametersCmp(), ViewFlags.COMPONENT, UserTechParameterModel, *args, **kwargs)
        self.__isVehSwitching = False

    @property
    def viewModel(self):
        return super(TechParametersView, self).getViewModel()

    def _initialize(self):
        super(TechParametersView, self)._initialize()
        self.__isVehSwitching = False
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_currentVehicle.onChangeStarted += self.__onCurrentVehicleChangeStarted
        self.__updateModel()

    def _finalize(self):
        g_currentVehicle.onChangeStarted -= self.__onCurrentVehicleChangeStarted
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        super(TechParametersView, self)._finalize()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if vehicle is None or vehicle.intCD not in RacingVehicles.ALL:
            return
        else:
            vehIntCD = vehicle.intCD
            self.viewModel.setVehicleIntCD(vehIntCD)
            return

    def __onCurrentVehicleChangeStarted(self):
        self.__isVehSwitching = True

    def __onCurrentVehicleChanged(self):
        if self.__isVehSwitching:
            self.__updateModel()
        self.__isVehSwitching = False
