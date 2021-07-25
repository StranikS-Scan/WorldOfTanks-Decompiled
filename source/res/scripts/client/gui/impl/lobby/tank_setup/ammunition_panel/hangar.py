# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar.py
from gui.impl.lobby.tank_setup.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_blocks_controller import AmmunitionBlocksController

class HangarAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionBlockController(self, vehicle):
        return AmmunitionBlocksController(vehicle)
