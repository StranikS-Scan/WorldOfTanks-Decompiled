# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/blocks_controller.py
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import AmmunitionBlocksController
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_shells_counter_mapping import ShellCounterMapping
from gui.prb_control import prbDispatcherProperty
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class HangarAmmunitionBlocksController(AmmunitionBlocksController):
    __slots__ = ()
    settingsCore = dependency.descriptor(ISettingsCore)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @tabUpdateFunc(TankSetupConstants.SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        if self._vehicle and not self.__isDisabled():
            for checkVehicleFunction, uiKey in ShellCounterMapping(self._vehicle).items():
                if checkVehicleFunction() and not self.settingsCore.serverSettings.getUIStorage2().get(uiKey):
                    viewModel.setNewItemsCount(1)
                    break
            else:
                viewModel.setNewItemsCount(0)

        super(HangarAmmunitionBlocksController, self)._updateShells(viewModel, isFirst)

    def __isDisabled(self):
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                if not permission.canChangeVehicle():
                    return True
        return self._vehicle.isInBattle or self._vehicle.isLocked or self._vehicle.isBroken if self._vehicle else True
