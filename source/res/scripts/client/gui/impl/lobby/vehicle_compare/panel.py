# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/panel.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, GroupData
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import BaseAmmunitionBlocksController
from gui.impl.lobby.vehicle_compare.panel_blocks import CompareOptDeviceBlock, CompareShellsBlock, CompareConsumablesBlock, CompareBattleBoostersBlock, CompareCamouflageBlock
_COMPARE_GROUPS = (GroupData(AmmunitionPanelConstants.NO_GROUP, (TankSetupConstants.OPT_DEVICES,
  TankSetupConstants.TOGGLE_SHELLS,
  TankSetupConstants.CONSUMABLES,
  TankSetupConstants.BATTLE_BOOSTERS,
  TankSetupConstants.TOGGLE_CAMOUFLAGE)),)

class CompareAmmunitionBlocksController(BaseAmmunitionBlocksController):
    __slots__ = ()

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


class CompareAmmunitionGroupsController(AmmunitionGroupsController):
    __slots__ = ()

    def _getGroups(self):
        return [] if self._vehicle is None else _COMPARE_GROUPS

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return CompareAmmunitionBlocksController(vehicle, ctx=ctx)


class CompareAmmunitionPanel(BaseAmmunitionPanel):
    __slots__ = ()

    def _createAmmunitionGroupsController(self, vehicle):
        return CompareAmmunitionGroupsController(vehicle)
