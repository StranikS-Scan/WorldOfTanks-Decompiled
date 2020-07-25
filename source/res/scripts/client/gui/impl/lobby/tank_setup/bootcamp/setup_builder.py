# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/setup_builder.py
from gui.impl.gen.view_models.views.lobby.tank_setup.main_tank_setup_model import MainTankSetupModel
from gui.impl.lobby.tank_setup.bootcamp.consumable import BootcampConsumableSetupSubView
from gui.impl.lobby.tank_setup.bootcamp.opt_device import BootcampOptDeviceSetupSubView
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from gui.impl.lobby.tank_setup.interactors.opt_device import OptDeviceInteractor
from gui.impl.lobby.tank_setup.tank_setup_builder import TankSetupBuilder

class BootcampTankSetupBuilder(TankSetupBuilder):
    __slots__ = ()

    def __init__(self, vehItem):
        super(BootcampTankSetupBuilder, self).__init__(MainTankSetupModel, vehItem)

    def configureComponents(self, viewModel):
        components = super(BootcampTankSetupBuilder, self).configureComponents(viewModel)
        self.addComponent(components, viewModel.optDevicesSetup, BootcampOptDeviceSetupSubView, OptDeviceInteractor(self._vehItem))
        self.addComponent(components, viewModel.consumablesSetup, BootcampConsumableSetupSubView, ConsumableInteractor(self._vehItem))
        return components
