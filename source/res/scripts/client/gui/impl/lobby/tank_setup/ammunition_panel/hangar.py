# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar.py
import adisp
from gui.impl.lobby.tank_setup.ammunition_panel.groups_controller import HangarAmmunitionGroupsController
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.veh_post_porgression.sounds import playSound, Sounds

class HangarAmmunitionPanel(BaseAmmunitionPanel):

    @adisp.process
    def onChangeSetupLayoutIndex(self, hudGroupID, layoutIdx):
        if self.isNewSetupLayoutIndexValid(hudGroupID, layoutIdx) and hudGroupID in GROUPS_MAP:
            self._updateSwitchingProgress(True)
            result = yield ActionsFactory.asyncDoAction(ActionsFactory.getAction(ActionsFactory.CHANGE_SETUP_EQUIPMENTS_INDEX, self._vehicle, GROUPS_MAP[hudGroupID], layoutIdx))
            if result:
                playSound(Sounds.SETUP_SWITCH)
            self._updateSwitchingProgress(False)

    def _createAmmunitionGroupsController(self, vehicle):
        return HangarAmmunitionGroupsController(vehicle, ctx=self._ctx)
