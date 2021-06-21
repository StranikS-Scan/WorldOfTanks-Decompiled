# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/groups_controller.py
import CommandMapping
from gui.Scaleform.daapi.view.common.keybord_helpers import getHotKeyList
from constants import ARENA_GUI_TYPE
from gui.impl.battle.battle_page.ammunition_panel.blocks_controller import PrebattleAmmunitionBlocksController
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_items_group import PrebattleAmmunitionItemsGroup
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, FRONTLINE_GROUPS, RANDOM_GROUPS
COMMAND_MAPPING = {CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1: AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS,
 CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2: AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS}
_GROUPS_COMMANDS = {value:key for key, value in COMMAND_MAPPING.iteritems()}

class PrebattleAmmunitionGroupsController(AmmunitionGroupsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onNextShellChanged(self, intCD):
        self._controller.onNextShellChanged(intCD)

    def onCurrentShellChanged(self, intCD):
        self._controller.onCurrentShellChanged(intCD)

    def _getGroups(self):
        if self._vehicle is None:
            return []
        else:
            arenaGuiType = self.sessionProvider.arenaVisitor.getArenaGuiType()
            if arenaGuiType is not None:
                if arenaGuiType in (ARENA_GUI_TYPE.EPIC_BATTLE, ARENA_GUI_TYPE.EPIC_TRAINING):
                    return FRONTLINE_GROUPS
                if arenaGuiType in (ARENA_GUI_TYPE.RANDOM,
                 ARENA_GUI_TYPE.TRAINING,
                 ARENA_GUI_TYPE.EPIC_RANDOM,
                 ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING):
                    return RANDOM_GROUPS
            return super(PrebattleAmmunitionGroupsController, self)._getGroups()

    def _createViewModel(self):
        return PrebattleAmmunitionItemsGroup()

    def _setupStates(self, setupSelectorModel, groupSettings):
        super(PrebattleAmmunitionGroupsController, self)._setupStates(setupSelectorModel, groupSettings)
        hotKeys = setupSelectorModel.getHotKeys()
        hotKeys.clear()
        if setupSelectorModel.getIsSwitchEnabled():
            hudGroupID = groupSettings.groupID
            command = _GROUPS_COMMANDS.get(hudGroupID)
            if command is not None:
                for key in getHotKeyList(command):
                    hotKeys.addString(key)

        hotKeys.invalidate()
        return

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return PrebattleAmmunitionBlocksController(vehicle)
