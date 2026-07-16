# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/shared/ls_radial_menu.py
from __future__ import absolute_import
import CommandMapping
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, MarkerType, DefaultMarkerSubType, INVALID_MARKER_SUBTYPE
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
from gui.Scaleform.daapi.view.battle.shared.radial_menu import Shortcut, _MARKERS_TYPE_TO_SUBTYPE_MAP
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from last_stand.gui.scaleform.daapi.view.meta.LSRadialMenuMeta import LSRadialMenuMeta
from last_stand.gui.scaleform.genConsts.LS_RADIAL_MENU_CONSTS import LS_RADIAL_MENU_CONSTS
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import LS_BATTLE_CHAT_COMMANDS
REGULAR_BOTTOM_STATIC_SHORTCUTS = (Shortcut(title=INGAME_HELP.RADIALMENU_RELOADINGGUN, action=BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN, icon=RADIAL_MENU_CONSTS.RELOAD, groups=LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_THIRD), Shortcut(title=INGAME_HELP.RADIALMENU_HELPME, action=BATTLE_CHAT_COMMAND_NAMES.SOS, icon=RADIAL_MENU_CONSTS.SOS, groups=LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FOURTH))
REGULAR_UPPER_STATIC_SHORTCUTS = (Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES, bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES, bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND),
 Shortcut(title='#last_stand.last_stand_battle:radialMenu/move_to_magnus', action=BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT, icon=LS_RADIAL_MENU_CONSTS.LS_MAGNUS, groups=[LS_RADIAL_MENU_CONSTS.TARGET_STATE_LS_MAGNUS], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title='#last_stand.last_stand_battle:radialMenu/attention_here', action=BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT, icon=LS_RADIAL_MENU_CONSTS.LS_MAGNUS_HELP, groups=[LS_RADIAL_MENU_CONSTS.TARGET_STATE_LS_MAGNUS], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title='#last_stand.last_stand_battle:radialMenu/move_to_camp', action=BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT, icon=LS_RADIAL_MENU_CONSTS.LS_CAMP, groups=[LS_RADIAL_MENU_CONSTS.TARGET_STATE_LS_CAMP], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title='#last_stand.last_stand_battle:radialMenu/attention_here', action=BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT, icon=LS_RADIAL_MENU_CONSTS.LS_CAMP_HELP, groups=[LS_RADIAL_MENU_CONSTS.TARGET_STATE_LS_CAMP], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title='#last_stand.last_stand_battle:radialMenu/obeliskHelp', action=LS_BATTLE_CHAT_COMMANDS.LS_OBELISK_HELP, icon=LS_RADIAL_MENU_CONSTS.LS_OBELISK_HELP, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT, RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title='#last_stand.last_stand_battle:radialMenu/obelisk', action=LS_BATTLE_CHAT_COMMANDS.LS_OBELISK, icon=LS_RADIAL_MENU_CONSTS.LS_OBELISK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT, RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND))
_CAN_CANCEL_REPLY_SHORTCUT = Shortcut(title='#last_stand.last_stand_battle:radialMenu/cancel', action=BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY, icon=LS_RADIAL_MENU_CONSTS.LS_CANCEL, groups=LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
_MARKERS_TYPE_TO_SUBTYPE_MAP.update({MarkerType.TARGET_POINT_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: LS_RADIAL_MENU_CONSTS.TARGET_STATE_LS_MAGNUS,
                                       DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: LS_RADIAL_MENU_CONSTS.TARGET_STATE_LS_CAMP,
                                       INVALID_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT}})

class LSRadialMenu(LSRadialMenuMeta):
    _lsCtrl = dependency.descriptor(ILSController)
    _CMD_CHAT_SHORTCUT_CONTEXT_COMMAND = (BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE,
     BATTLE_CHAT_COMMAND_NAMES.HELPME,
     BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
     BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE,
     BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
     BATTLE_CHAT_COMMAND_NAMES.REPLY,
     BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY,
     BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT)
    _CMD_CHAT_SHORTCUT_CONTEXT_COMMIT = (BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE,
     BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
     BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
     BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA,
     BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
     BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT)
    _ALL_TARGET_STATES = RADIAL_MENU_CONSTS.ALL_TARGET_STATES + LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES

    def getKeyFromAction(self, action):
        if action == LS_BATTLE_CHAT_COMMANDS.LS_OBELISK:
            shortcut = CommandMapping.g_instance.getName(CommandMapping.CMD_CHAT_SHORTCUT_THANKYOU)
            return getScaleformKey(CommandMapping.g_instance.get(shortcut))
        if action == LS_BATTLE_CHAT_COMMANDS.LS_OBELISK_HELP:
            shortcut = CommandMapping.g_instance.getName(CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE)
            return getScaleformKey(CommandMapping.g_instance.get(shortcut))
        return super(LSRadialMenu, self).getKeyFromAction(action)

    def _populate(self):
        super(LSRadialMenu, self)._populate()
        self.as_setObeliskEnabledS(self._lsCtrl.getModeSettings().isObeliskRadialMenuEnabled)

    def _initShortCuts(self):
        super(LSRadialMenu, self)._initShortCuts()
        isObeliskDisabled = not self._lsCtrl.getModeSettings().isObeliskRadialMenuEnabled
        for shotCut in REGULAR_BOTTOM_STATIC_SHORTCUTS:
            for shotCutGroup in shotCut.groups:
                if shotCutGroup not in self.bottomShortcutSets:
                    self.bottomShortcutSets[shotCutGroup] = []
                self.bottomShortcutSets[shotCutGroup].append(shotCut)

        for shotCut in REGULAR_UPPER_STATIC_SHORTCUTS:
            for shotCutGroup in shotCut.groups:
                if isObeliskDisabled and shotCut.action in (LS_BATTLE_CHAT_COMMANDS.LS_OBELISK, LS_BATTLE_CHAT_COMMANDS.LS_OBELISK_HELP):
                    continue
                if shotCutGroup not in self.upperShortcutSets:
                    self.upperShortcutSets[shotCutGroup] = []
                self.upperShortcutSets[shotCutGroup].append(shotCut)

    def _getCanReplayShortcut(self, shortcut, canReplyAction):
        return Shortcut(title='#last_stand.last_stand_battle:radialMenu/confirm', action=canReplyAction, icon=RADIAL_MENU_CONSTS.YES, groups=LS_RADIAL_MENU_CONSTS.WHITE_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=shortcut.indexInGroup) if shortcut.action == BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT else super(LSRadialMenu, self)._getCanReplayShortcut(shortcut, canReplyAction)

    def _getCanCancelReplyShortcut(self):
        return _CAN_CANCEL_REPLY_SHORTCUT
