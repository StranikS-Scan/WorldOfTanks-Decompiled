# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tank_setup_builder.py
from collections import namedtuple
from gui.impl.gen.view_models.views.lobby.tank_setup.main_tank_setup_model import MainTankSetupModel
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from gui.impl.lobby.tank_setup.interactors.battle_booster import BattleBoosterInteractor
from gui.impl.lobby.tank_setup.interactors.frontline import FrontlineInteractor
from gui.impl.lobby.tank_setup.interactors.opt_device import OptDeviceInteractor
from gui.impl.lobby.tank_setup.interactors.shell import ShellInteractor
from gui.impl.lobby.tank_setup.sub_views.consumable_setup import ConsumableSetupSubView
from gui.impl.lobby.tank_setup.sub_views.battle_booster_setup import BattleBoosterSetupSubView
from gui.impl.lobby.tank_setup.sub_views.frontline_setup import EpicBattleSetupSubView
from gui.impl.lobby.tank_setup.sub_views.opt_device_setup import OptDeviceSetupSubView
from gui.impl.lobby.tank_setup.sub_views.shell_setup import ShellSetupSubView
TankSetupComponent = namedtuple('_TankSetupComponent', 'subModel, subViewClazz, interactor')

class TankSetupBuilder(object):
    __slots__ = ('__viewModelClazz', '_vehItem')

    def __init__(self, viewModelClazz, vehItem):
        self.__viewModelClazz = viewModelClazz
        self._vehItem = vehItem

    @staticmethod
    def build(components):
        subViews = {}
        for component in components:
            subViews[component.interactor.getName()] = component.subViewClazz(component.subModel, component.interactor)

        return subViews

    def configureBuild(self, viewModel):
        components = self.configureComponents(viewModel)
        return self.build(components)

    def configureComponents(self, viewModel):
        return []

    def getViewModel(self):
        return self.__viewModelClazz()

    def clear(self):
        self.__viewModelClazz = None
        self._vehItem = None
        return

    @staticmethod
    def addComponent(components, subModel, subView, interactor):
        components.append(TankSetupComponent(subModel, subView, interactor))


class HangarTankSetupBuilder(TankSetupBuilder):
    __slots__ = ()

    def __init__(self, vehItem):
        super(HangarTankSetupBuilder, self).__init__(MainTankSetupModel, vehItem)

    def configureComponents(self, viewModel):
        components = super(HangarTankSetupBuilder, self).configureComponents(viewModel)
        self.addComponent(components, viewModel.consumablesSetup, ConsumableSetupSubView, ConsumableInteractor(self._vehItem))
        self.addComponent(components, viewModel.shellsSetup, ShellSetupSubView, ShellInteractor(self._vehItem))
        self.addComponent(components, viewModel.optDevicesSetup, OptDeviceSetupSubView, OptDeviceInteractor(self._vehItem))
        self.addComponent(components, viewModel.battleBoostersSetup, BattleBoosterSetupSubView, BattleBoosterInteractor(self._vehItem))
        return components


class EpicBattleTankSetupBuilder(HangarTankSetupBuilder):
    __slots__ = ()

    def configureComponents(self, viewModel):
        components = super(EpicBattleTankSetupBuilder, self).configureComponents(viewModel)
        self.addComponent(components, viewModel.frontlineSetup, EpicBattleSetupSubView, FrontlineInteractor(self._vehItem))
        return components
