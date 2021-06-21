# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel.py
from gui.impl.battle.battle_page.ammunition_panel.groups_controller import PrebattleAmmunitionGroupsController
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants

class PrebattleAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionGroupsController(self, vehicle):
        return PrebattleAmmunitionGroupsController(vehicle)

    def onNextShellChanged(self, intCD):
        self._controller.onNextShellChanged(intCD)
        self.updateSection(TankSetupConstants.SHELLS)

    def onCurrentShellChanged(self, intCD):
        self._controller.onCurrentShellChanged(intCD)
        self.updateSection(TankSetupConstants.SHELLS)
