# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/radial_menu.py
from chat_commands_consts import MarkerType
from gui.Scaleform.daapi.view.battle.shared import radial_menu
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
ATTACK_BOSS = 'AttackBoss'
HB_OVERRIDE_SHORTCUTS_BY_ACTION = {BATTLE_CHAT_COMMAND_NAMES.OBJECTIVES_POINT: (radial_menu.Shortcut(title=INGAME_HELP.RADIALMENU_GOING_THERE, action=BATTLE_CHAT_COMMAND_NAMES.OBJECTIVES_POINT, icon=ATTACK_BOSS, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),)}

class HistoricalRadialMenu(radial_menu.RadialMenu):

    def _getSubtypeMapByMarkersType(self, targetMarkerType):
        return radial_menu.MARKERS_TYPE_TO_SUBTYPE_MAP[targetMarkerType] if targetMarkerType != MarkerType.BASE_MARKER_TYPE else {}

    def _getCanReplyShortcut(self, shortcut, canReplyAction):
        override = self.__overrideShortcut(shortcut, canReplyAction)
        return override if override else super(HistoricalRadialMenu, self)._getCanReplyShortcut(shortcut, canReplyAction)

    def _getAlterCanReplyShortcut(self, shortcut, canReplyAction):
        override = self.__overrideShortcut(shortcut, canReplyAction)
        return override if override else super(HistoricalRadialMenu, self)._getAlterCanReplyShortcut(shortcut, canReplyAction)

    def __overrideShortcut(self, shortcut, canReplyAction):
        if self.crosshairData is not None:
            for override in HB_OVERRIDE_SHORTCUTS_BY_ACTION.get(self.crosshairData.replyToAction, []):
                if override.indexInGroup == shortcut.indexInGroup:
                    return radial_menu.Shortcut(title=override.title, action=canReplyAction, icon=override.icon, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=override.indexInGroup)

        return
