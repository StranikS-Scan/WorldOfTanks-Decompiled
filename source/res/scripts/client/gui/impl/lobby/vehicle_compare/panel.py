# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/panel.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_blocks_controller import BaseAmmunitionBlocksController
from gui.impl.lobby.vehicle_compare.panel_blocks import CompareOptDeviceBlock, CompareShellsBlock, CompareConsumablesBlock, CompareBattleBoostersBlock, CompareCamouflageBlock
_COMPARE_TABS = (TankSetupConstants.OPT_DEVICES,
 TankSetupConstants.TOGGLE_SHELLS,
 TankSetupConstants.CONSUMABLES,
 TankSetupConstants.BATTLE_BOOSTERS,
 TankSetupConstants.TOGGLE_CAMOUFLAGE)

class CompareAmmunitionBlocksController(BaseAmmunitionBlocksController):
    __slots__ = ()

    def _getTabs(self):
        return _COMPARE_TABS

    @tabUpdateFunc(TankSetupConstants.OPT_DEVICES)
    def _updateOptDevices(self, viewModel, isFirst=False):
        CompareOptDeviceBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.TOGGLE_SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        CompareShellsBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.CONSUMABLES)
    def _updateConsumables(self, viewModel, isFirst=False):
        CompareConsumablesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.BATTLE_BOOSTERS)
    def _updateBattleBoosters(self, viewModel, isFirst=False):
        CompareBattleBoostersBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.TOGGLE_CAMOUFLAGE)
    def _updateCamouflage(self, viewModel, isFirst=False):
        CompareCamouflageBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    def _createViewModel(self, name):
        return AmmunitionItemsSection()


class CompareAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionBlockController(self, vehicle):
        return CompareAmmunitionBlocksController(vehicle)
