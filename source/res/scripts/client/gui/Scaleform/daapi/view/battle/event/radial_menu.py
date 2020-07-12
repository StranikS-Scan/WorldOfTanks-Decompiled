# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/radial_menu.py
from collections import namedtuple
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.radial_menu import RadialMenu
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
from gui.battle_control.controllers.chat_cmd_ctrl import BATTLE_CHAT_COMMAND_NAMES
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.Scaleform.daapi.view.meta.EventRadialMenuMeta import EventRadialMenuMeta
from gui.shared import EVENT_BUS_SCOPE, events
EventShortcut = namedtuple('EventShortcut', ('title', 'action', 'icon'))
EventShortcut.__new__.__defaults__ = (None, None, None)
_CMD_LOCALE_PFX = '#ingame_help:chatShortcuts/'
SHORTCUTS_EVENT = (EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_1', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_2', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_3', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_4', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_5', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_6', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_7', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_1_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1_EX),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_2_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2_EX),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_3_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3_EX),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_4_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4_EX),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_5_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5_EX),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_6_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6_EX),
 EventShortcut(title=_CMD_LOCALE_PFX + 'event_chat_7_ex', action=BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7_EX))
PAGE_DEFAULT = (BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 None,
 None,
 BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
 BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN)
PAGE_ALLY = (BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 None,
 None,
 None,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
 None)
PAGE_ENEMY = (None,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 None,
 None,
 None,
 None,
 None)
PAGE_CHAT_DEFAULT = (BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7)
PAGE_CHAT_ALLY = (BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7_EX)
SHORTCUT_BY_ACTION = {shortcut.action:shortcut for shortcut in SHORTCUTS_EVENT}

def __makeShortcutSet(commands):
    return tuple(((SHORTCUT_BY_ACTION[action] if action is not None else None) for action in commands))


SHORTCUT_SETS_EVENT = {RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT: tuple(),
 RADIAL_MENU_CONSTS.TARGET_STATE_ALLY: tuple(),
 RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY: tuple(),
 RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY: tuple()}

class EventRadialMenu(RadialMenu, EventRadialMenuMeta):

    def onAction(self, action):
        super(EventRadialMenu, self).onAction(action)
        self.fireEvent(events.RadialMenuEvent(events.RadialMenuEvent.RADIAL_MENU_ACTION), scope=EVENT_BUS_SCOPE.BATTLE)

    def showHandCursor(self):
        self.app.cursorMgr.setCursorForced(CursorManager.BUTTON)

    def hideHandCursor(self):
        self.app.cursorMgr.setCursorForced(CursorManager.ARROW)

    def leaveRadialMode(self):
        self.fireEvent(events.RadialMenuEvent(events.RadialMenuEvent.RADIAL_MENU_ACTION), scope=EVENT_BUS_SCOPE.BATTLE)

    def hide(self, allowAction=True):
        super(EventRadialMenu, self).hide()
        self.app.cursorMgr.hide()

    def _showInternal(self, radialState, offset, ratio):
        self.as_showWithNameS(radialState, offset, ratio, self._getTargetDisplayName())

    def _getTargetDisplayName(self):
        target = BigWorld.target()
        if target is not None:
            arenaDP = self.sessionProvider.getArenaDP()
            if arenaDP is not None:
                vInfo = arenaDP.getVehicleInfo(target.id)
                if vInfo is not None:
                    return vInfo.player.name
        return

    def _getShortcutSets(self):
        return SHORTCUT_SETS_EVENT
