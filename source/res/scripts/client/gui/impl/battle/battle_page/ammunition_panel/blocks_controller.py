# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/blocks_controller.py
from typing import TYPE_CHECKING
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import AmmunitionBlocksController
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_shell_ammunition_slot import PrebattleShellAmmunitionSlot, ShellBattleState
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import ShellsBlock
if TYPE_CHECKING:
    from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_vehicle_mock import PrbAmmunitionVehicleMock
EMPTY_INT_COMPACT_DESCRIPTOR = 0

class PrebattleShellsBlock(ShellsBlock):

    def __init__(self, vehicle, currentSection, nextShellIntCD, currentShellIntCD):
        super(PrebattleShellsBlock, self).__init__(vehicle, currentSection)
        self.__nextShellIntCD = nextShellIntCD
        self.__currentShellIntCD = currentShellIntCD

    def _getAmmunitionSlotModel(self):
        return PrebattleShellAmmunitionSlot()

    def _getKeySettings(self):
        pass

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(PrebattleShellsBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setShellState(self.__getShellState(slotItem.intCD))

    def __getShellState(self, shellItnCD):
        return ShellBattleState.NORAML


class PrebattleAmmunitionBlocksController(AmmunitionBlocksController):
    __slots__ = ('__nextShellIntCD', '__currentShellIntCD')

    def __init__(self, vehicle, autoCreating=True, ctx=None):
        super(PrebattleAmmunitionBlocksController, self).__init__(vehicle, autoCreating, ctx)
        self.__nextShellIntCD = EMPTY_INT_COMPACT_DESCRIPTOR
        self.__currentShellIntCD = EMPTY_INT_COMPACT_DESCRIPTOR

    def onNextShellChanged(self, intCD):
        self.__nextShellIntCD = intCD

    def onCurrentShellChanged(self, intCD):
        self.__currentShellIntCD = intCD

    @tabUpdateFunc(TankSetupConstants.SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        PrebattleShellsBlock(self._vehicle, self._currentSection, self.__nextShellIntCD, self.__currentShellIntCD).adapt(viewModel, isFirst)
