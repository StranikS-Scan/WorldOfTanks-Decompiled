# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_blocks_controller.py
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_shells_section import AmmunitionShellsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tabs_controller import TabsController, tabUpdateFunc
from gui.impl.lobby.tank_setup.ammunition_panel_blocks import OptDeviceBlock, ShellsBlock, ConsumablesBlock, BattleBoostersBlock, BattleAbilitiesBlock
from gui.prb_control import prbDispatcherProperty
RANDOM_BATTLE_TABS = (TankSetupConstants.OPT_DEVICES,
 TankSetupConstants.SHELLS,
 TankSetupConstants.CONSUMABLES,
 TankSetupConstants.BATTLE_BOOSTERS)
FRONTLINE_TABS = RANDOM_BATTLE_TABS + (TankSetupConstants.BATTLE_ABILITIES,)

class BaseAmmunitionBlocksController(TabsController):
    __slots__ = ('_vehicle', '_currentSection')

    def __init__(self, vehicle, autoCreating=True):
        super(BaseAmmunitionBlocksController, self).__init__(autoCreating)
        self._vehicle = vehicle
        self._currentSection = None
        return

    def updateVehicle(self, vehicle):
        self._vehicle = vehicle

    def updateCurrentSection(self, currentSection):
        self._currentSection = currentSection


class AmmunitionBlocksController(BaseAmmunitionBlocksController):
    __slots__ = ()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _getTabs(self):
        if self._vehicle is None:
            return []
        else:
            return FRONTLINE_TABS if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) else RANDOM_BATTLE_TABS

    @tabUpdateFunc(TankSetupConstants.OPT_DEVICES)
    def _updateOptDevices(self, viewModel, isFirst=False):
        OptDeviceBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        ShellsBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.CONSUMABLES)
    def _updateConsumables(self, viewModel, isFirst=False):
        ConsumablesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.BATTLE_BOOSTERS)
    def _updateBattleBoosters(self, viewModel, isFirst=False):
        BattleBoostersBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.BATTLE_ABILITIES)
    def _updateBattleAbilities(self, viewModel, isFirst=False):
        BattleAbilitiesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    def _createViewModel(self, name):
        return AmmunitionShellsSection() if name == TankSetupConstants.SHELLS else AmmunitionItemsSection()
