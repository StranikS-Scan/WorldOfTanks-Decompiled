# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/ammunition_panel.py
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_blocks_controller import AmmunitionBlocksController
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
_BOOTCAMP_SECTIONS = (TankSetupConstants.OPT_DEVICES, TankSetupConstants.CONSUMABLES)

class _BootcampAmmunitionBlocksController(AmmunitionBlocksController):

    def _getTabs(self):
        return [] if self._vehicle is None else _BOOTCAMP_SECTIONS


class BootcampAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionBlockController(self, vehicle):
        return _BootcampAmmunitionBlocksController(vehicle)


class BootcampAmmunitionPanelView(BaseAmmunitionPanelView):

    def _onLoading(self, *args, **kwargs):
        super(BootcampAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsBootcamp(True)

    def _createAmmunitionPanel(self):
        return BootcampAmmunitionPanel(self.viewModel.ammunitionPanel, g_currentVehicle.item)
