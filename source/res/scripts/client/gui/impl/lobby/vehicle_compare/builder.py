# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/builder.py
from gui.impl.gen.view_models.views.lobby.tank_setup.main_tank_setup_model import MainTankSetupModel
from gui.impl.lobby.vehicle_compare.battle_booster import CompareBattleBoosterSetupSubView
from gui.impl.lobby.vehicle_compare.consumable import CompareConsumableSetupSubView
from gui.impl.lobby.vehicle_compare.interactors import CompareConsumableInteractor, CompareOptDeviceInteractor, CompareBattleBoosterInteractor
from gui.impl.lobby.vehicle_compare.opt_device import CompareOptDeviceSetupSubView
from gui.impl.lobby.tank_setup.tank_setup_builder import TankSetupBuilder

class CompareTankSetupBuilder(TankSetupBuilder):
    __slots__ = ()

    def __init__(self, vehItem):
        super(CompareTankSetupBuilder, self).__init__(MainTankSetupModel, vehItem)

    def configureComponents(self, viewModel):
        components = super(CompareTankSetupBuilder, self).configureComponents(viewModel)
        self.addComponent(components, viewModel.consumablesSetup, CompareConsumableSetupSubView, CompareConsumableInteractor(self._vehItem))
        self.addComponent(components, viewModel.optDevicesSetup, CompareOptDeviceSetupSubView, CompareOptDeviceInteractor(self._vehItem))
        self.addComponent(components, viewModel.battleBoostersSetup, CompareBattleBoosterSetupSubView, CompareBattleBoosterInteractor(self._vehItem))
        return components
