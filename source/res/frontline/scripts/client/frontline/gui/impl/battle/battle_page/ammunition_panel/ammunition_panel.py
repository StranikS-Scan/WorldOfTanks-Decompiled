# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/battle/battle_page/ammunition_panel/ammunition_panel.py
from frontline.gui.impl.battle.battle_page.ammunition_panel.groups_controller import FLRespawnAmmunitionGroupsController
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel

class FLRespawnAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionGroupsController(self, vehicle):
        return FLRespawnAmmunitionGroupsController(vehicle, ctx=self._ctx)
