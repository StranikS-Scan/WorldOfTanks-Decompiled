# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar.py
import adisp
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.impl.lobby.tank_setup.ammunition_panel.groups_controller import HangarAmmunitionGroupsController
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.veh_post_progression.sounds import playSound, Sounds
from helpers import dependency
from post_progression_common import TankSetupGroupsId
from skeletons.account_helpers.settings_core import ISettingsCore

class HangarAmmunitionPanel(BaseAmmunitionPanel):
    _settingsCore = dependency.descriptor(ISettingsCore)

    @adisp.process
    def onChangeSetupLayoutIndex(self, hudGroupID, layoutIdx, callback=None):
        result = False
        if self.isNewSetupLayoutIndexValid(hudGroupID, layoutIdx) and hudGroupID in GROUPS_MAP:
            groupId = GROUPS_MAP[hudGroupID]
            self._updateSwitchingProgress(True)
            result = yield ActionsFactory.asyncDoAction(ActionsFactory.getAction(ActionsFactory.CHANGE_SETUP_EQUIPMENTS_INDEX, self._vehicle, groupId, layoutIdx))
            if result:
                self.__markHintUsed(groupId)
                playSound(Sounds.SETUP_SWITCH)
            self._updateSwitchingProgress(False)
        if callback is not None:
            callback(result)
        return

    def _createAmmunitionGroupsController(self, vehicle):
        return HangarAmmunitionGroupsController(vehicle, ctx=self._ctx)

    def __markHintUsed(self, groupId):
        key = None
        if groupId == TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS:
            key = OnceOnlyHints.SWITCH_EQUIPMENT_AUXILIARY_LOADOUT_HINT
        elif groupId == TankSetupGroupsId.EQUIPMENT_AND_SHELLS:
            key = OnceOnlyHints.SWITCH_EQUIPMENT_ESSENTIALS_LOADOUT_HINT
        serverSettings = self._settingsCore.serverSettings
        if key is not None and not serverSettings.getOnceOnlyHintsSetting(key):
            serverSettings.setOnceOnlyHintsSettings({key: True})
        return
