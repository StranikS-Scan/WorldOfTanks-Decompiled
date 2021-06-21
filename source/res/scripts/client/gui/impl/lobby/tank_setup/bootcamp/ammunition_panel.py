# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/ammunition_panel.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, GroupData
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
_BOOTCAMP_GROUPS = (GroupData(AmmunitionPanelConstants.NO_GROUP, (TankSetupConstants.OPT_DEVICES, TankSetupConstants.CONSUMABLES)),)

class _BootcampAmmunitionGroupsController(AmmunitionGroupsController):
    __slots__ = ()

    def _getGroups(self):
        return [] if self._vehicle is None else _BOOTCAMP_GROUPS


class BootcampAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionGroupsController(self, vehicle):
        return _BootcampAmmunitionGroupsController(vehicle)


class BootcampAmmunitionPanelView(BaseAmmunitionPanelView):

    def _onLoading(self, *args, **kwargs):
        super(BootcampAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsBootcamp(True)

    def _createAmmunitionPanel(self):
        return BootcampAmmunitionPanel(self.viewModel.ammunitionPanel, self.vehItem)
