# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/ammunition_setup.py
from gui.impl.lobby.tank_setup.ammunition_setup.hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.bootcamp.ammunition_panel import BootcampAmmunitionPanel
from gui.impl.lobby.tank_setup.bootcamp.setup_builder import BootcampTankSetupBuilder
from gui.impl.lobby.tank_setup.main_tank_setup.base import MainTankSetupView

class BootcampAmmunitionSetupView(BaseHangarAmmunitionSetupView):

    def _onLoading(self, **kwargs):
        super(BootcampAmmunitionSetupView, self)._onLoading(**kwargs)
        self.viewModel.setIsBootcamp(True)

    def _createMainTankSetup(self):
        return MainTankSetupView(self.viewModel.tankSetup, BootcampTankSetupBuilder(self._vehItem))

    def _createAmmunitionPanel(self):
        return BootcampAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem())
