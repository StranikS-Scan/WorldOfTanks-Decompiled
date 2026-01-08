# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/radial_menu.py
from gui.Scaleform.daapi.view.battle.shared.radial_menu import RadialMenu, CrosshairData, Shortcut, buildShortcutMap
from supply_shared import Supply
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
__UPPER_SUPPLY_SHORTCUTS = (Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKING_SUPPLY, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_SUPPLY, icon=RADIAL_MENU_CONSTS.ATTACKING_ENEMY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACK_SUPPLY, action=BATTLE_CHAT_COMMAND_NAMES.ATTACK_SUPPLY, icon=RADIAL_MENU_CONSTS.ATTACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_DEFENDING_SUPPLY, action=BATTLE_CHAT_COMMAND_NAMES.DEFENDING_SUPPLY, icon=RADIAL_MENU_CONSTS.DEFENDING_SUPPLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_DEFEND_SUPPLY, action=BATTLE_CHAT_COMMAND_NAMES.DEFEND_SUPPLY, icon=RADIAL_MENU_CONSTS.DEFEND_SUPPLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_SUPPLY_SELF_REPAIR, action=BATTLE_CHAT_COMMAND_NAMES.SELF_REPAIR_SUPPLY, icon=RADIAL_MENU_CONSTS.SELFREPAIR_SUPPLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY, RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY, RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY, RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY, RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH))
_UPPER_SHORTCUT_SETS = buildShortcutMap(__UPPER_SUPPLY_SHORTCUTS)

class EpicRadialMenu(RadialMenu):

    def __init__(self):
        super(EpicRadialMenu, self).__init__()
        self._cachedUpperShortcuts = None
        return

    def _getRadialMenuState(self, targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction):
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(targetID)
        vType = vInfo.vehicleType
        if not Supply.isSupply(vType.tags):
            return super(EpicRadialMenu, self)._getRadialMenuState(targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction)
        viewState = self._getViewStateForMarker(targetMarkerType, targetMarkerSubtype)
        if viewState == RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY:
            viewState = RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY
        elif viewState == RADIAL_MENU_CONSTS.TARGET_STATE_ALLY:
            if vInfo.isAlive():
                viewState = RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY
            else:
                viewState = RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY
        else:
            viewState = RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT
        self._crosshairData = CrosshairData(targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction)
        return self._sanitizeViewState(viewState)

    def _getUpperShortcuts(self):
        if self._cachedUpperShortcuts is not None:
            return self._cachedUpperShortcuts
        else:
            base = super(EpicRadialMenu, self)._getUpperShortcuts().copy()
            for state, shortcuts in _UPPER_SHORTCUT_SETS.items():
                base.setdefault(state, []).extend(shortcuts)

            self._cachedUpperShortcuts = base
            return base
