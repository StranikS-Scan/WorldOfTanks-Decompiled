# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/radial_menu.py
from collections import namedtuple
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.radial_menu import RadialMenu, SHORTCUT_STATES, CMD_LOCALE_PFX
from gui.Scaleform.genConsts.BATTLE_ICONS_CONSTS import BATTLE_ICONS_CONSTS
from gui.battle_control.controllers.chat_cmd_ctrl import CHAT_COMMANDS
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.Scaleform.daapi.view.meta.EventRadialMenuMeta import EventRadialMenuMeta
from gui.shared import EVENT_BUS_SCOPE, events
EventShortcut = namedtuple('EventShortcut', ('title', 'action', 'icon'))
EventShortcut.__new__.__defaults__ = (None, None, None)
SHORTCUTS_EVENT = (EventShortcut(title=CMD_LOCALE_PFX + 'attack', action=CHAT_COMMANDS.ATTACK, icon=BATTLE_ICONS_CONSTS.ATTACK),
 EventShortcut(title=CMD_LOCALE_PFX + 'backToBase', action=CHAT_COMMANDS.BACKTOBASE, icon=BATTLE_ICONS_CONSTS.BACK_TO_BASE),
 EventShortcut(title=CMD_LOCALE_PFX + 'positive', action=CHAT_COMMANDS.POSITIVE, icon=BATTLE_ICONS_CONSTS.YES),
 EventShortcut(title=CMD_LOCALE_PFX + 'negative', action=CHAT_COMMANDS.NEGATIVE, icon=BATTLE_ICONS_CONSTS.NO),
 EventShortcut(title=CMD_LOCALE_PFX + 'helpMe', action=CHAT_COMMANDS.SOS, icon=BATTLE_ICONS_CONSTS.HELP_ME),
 EventShortcut(title=CMD_LOCALE_PFX + 'reloadingGun', action=CHAT_COMMANDS.RELOADINGGUN, icon=BATTLE_ICONS_CONSTS.RELOAD),
 EventShortcut(title=CMD_LOCALE_PFX + 'followMe', action=CHAT_COMMANDS.FOLLOWME, icon=BATTLE_ICONS_CONSTS.FOLLOW_ME),
 EventShortcut(title=CMD_LOCALE_PFX + 'toBack', action=CHAT_COMMANDS.TURNBACK, icon=BATTLE_ICONS_CONSTS.TURN_BACK),
 EventShortcut(title=CMD_LOCALE_PFX + 'helpMeEx', action=CHAT_COMMANDS.HELPME, icon=BATTLE_ICONS_CONSTS.HELP_ME_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'stop', action=CHAT_COMMANDS.STOP, icon=BATTLE_ICONS_CONSTS.STOP),
 EventShortcut(title=CMD_LOCALE_PFX + 'supportMeWithFire', action=CHAT_COMMANDS.SUPPORTMEWITHFIRE, icon=BATTLE_ICONS_CONSTS.SUPPORT),
 EventShortcut(title=CMD_LOCALE_PFX + 'attackEnemy', action=CHAT_COMMANDS.ATTACKENEMY, icon=BATTLE_ICONS_CONSTS.ATTACK_SPG),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_1', action=CHAT_COMMANDS.EVENT_CHAT_1),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_2', action=CHAT_COMMANDS.EVENT_CHAT_2),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_3', action=CHAT_COMMANDS.EVENT_CHAT_3),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_4', action=CHAT_COMMANDS.EVENT_CHAT_4),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_5', action=CHAT_COMMANDS.EVENT_CHAT_5),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_6', action=CHAT_COMMANDS.EVENT_CHAT_6),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_7', action=CHAT_COMMANDS.EVENT_CHAT_7),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_1_ex', action=CHAT_COMMANDS.EVENT_CHAT_1_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_2_ex', action=CHAT_COMMANDS.EVENT_CHAT_2_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_3_ex', action=CHAT_COMMANDS.EVENT_CHAT_3_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_4_ex', action=CHAT_COMMANDS.EVENT_CHAT_4_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_5_ex', action=CHAT_COMMANDS.EVENT_CHAT_5_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_6_ex', action=CHAT_COMMANDS.EVENT_CHAT_6_EX),
 EventShortcut(title=CMD_LOCALE_PFX + 'event_chat_7_ex', action=CHAT_COMMANDS.EVENT_CHAT_7_EX))
PAGE_DEFAULT = (CHAT_COMMANDS.SOS,
 CHAT_COMMANDS.ATTACK,
 CHAT_COMMANDS.NEGATIVE,
 None,
 CHAT_COMMANDS.POSITIVE,
 CHAT_COMMANDS.BACKTOBASE,
 CHAT_COMMANDS.RELOADINGGUN)
PAGE_ALLY = (CHAT_COMMANDS.HELPME,
 CHAT_COMMANDS.FOLLOWME,
 None,
 None,
 None,
 CHAT_COMMANDS.TURNBACK,
 CHAT_COMMANDS.STOP)
PAGE_ENEMY = (None,
 CHAT_COMMANDS.ATTACKENEMY,
 None,
 None,
 None,
 None,
 None)
PAGE_CHAT_DEFAULT = (CHAT_COMMANDS.EVENT_CHAT_1,
 CHAT_COMMANDS.EVENT_CHAT_2,
 CHAT_COMMANDS.EVENT_CHAT_3,
 CHAT_COMMANDS.EVENT_CHAT_4,
 CHAT_COMMANDS.EVENT_CHAT_5,
 CHAT_COMMANDS.EVENT_CHAT_6,
 CHAT_COMMANDS.EVENT_CHAT_7)
PAGE_CHAT_ALLY = (CHAT_COMMANDS.EVENT_CHAT_1_EX,
 CHAT_COMMANDS.EVENT_CHAT_2_EX,
 CHAT_COMMANDS.EVENT_CHAT_3_EX,
 CHAT_COMMANDS.EVENT_CHAT_4_EX,
 CHAT_COMMANDS.EVENT_CHAT_5_EX,
 CHAT_COMMANDS.EVENT_CHAT_6_EX,
 CHAT_COMMANDS.EVENT_CHAT_7_EX)
SHORTCUT_BY_ACTION = {shortcut.action:shortcut for shortcut in SHORTCUTS_EVENT}

def __makeShortcutSet(commands):
    return tuple(((SHORTCUT_BY_ACTION[action] if action is not None else None) for action in commands))


SHORTCUT_SETS_EVENT = {SHORTCUT_STATES.DEFAULT: __makeShortcutSet(PAGE_DEFAULT + PAGE_CHAT_DEFAULT),
 SHORTCUT_STATES.ALLY: __makeShortcutSet(PAGE_ALLY + PAGE_CHAT_ALLY),
 SHORTCUT_STATES.ENEMY: __makeShortcutSet(PAGE_ENEMY),
 SHORTCUT_STATES.ENEMY_SPG: tuple()}

class EventRadialMenu(RadialMenu, EventRadialMenuMeta):

    def onAction(self, action):
        super(EventRadialMenu, self).onAction(action)
        self.fireEvent(events.RadialMenuEvent(events.RadialMenuEvent.RADIAL_MENU_ACTION), scope=EVENT_BUS_SCOPE.BATTLE)

    def showHandCursor(self):
        self.app.cursorMgr.setCursorForced(CursorManager.BUTTON)

    def hideHandCursor(self):
        self.app.cursorMgr.setCursorForced(CursorManager.ARROW)

    def hide(self):
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
