# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/radial_menu.py
import logging
import GUI
import Keys
import CommandMapping
from collections import namedtuple, defaultdict
from AvatarInputHandler import aih_global_binding
from aih_constants import CTRL_MODE_NAME
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, ReplyState, MarkerType, DefaultMarkerSubType, ONE_SHOT_COMMANDS_TO_REPLIES, INVALID_MARKER_SUBTYPE, LocationMarkerSubType
from gui.Scaleform.daapi.view.meta.RadialMenuMeta import RadialMenuMeta
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import event_dispatcher as gui_event_dispatcher, avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.controllers.chat_cmd_ctrl import KB_MAPPING, CONTEXT_ACTIONS, COMMIT_ACTIONS
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.utils.key_mapping import getScaleformKey, BW_TO_SCALEFORM
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.chat_hotkey.loggers import ChatHotkeyLogger
_logger = logging.getLogger(__name__)
_SHORTCUTS_IN_GROUP = 6
Shortcut = namedtuple('Shortcut', ('title', 'action', 'icon', 'groups', 'bState', 'indexInGroup'))
CrosshairData = namedtuple('CrosshairData', ('targetID', 'targetMarkerType', 'targetMarkerSubtype', 'replyState', 'replyToAction'))
REGULAR_BOTTOM_STATIC_SHORTCUTS = (Shortcut(title=INGAME_HELP.RADIALMENU_RELOADINGGUN, action=BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN, icon=RADIAL_MENU_CONSTS.RELOAD, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_THIRD), Shortcut(title=INGAME_HELP.RADIALMENU_HELPME, action=BATTLE_CHAT_COMMAND_NAMES.SOS, icon=RADIAL_MENU_CONSTS.SOS, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FOURTH))
REGULAR_UPPER_STATIC_SHORTCUTS = (Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
  RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ALLY,
  RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT,
  RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY], bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
  RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ALLY,
  RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT,
  RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY], bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY], bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY], bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_GOING_THERE, action=BATTLE_CHAT_COMMAND_NAMES.GOING_THERE, icon=RADIAL_MENU_CONSTS.GOING_THERE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKAREASPG, action=BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA, icon=RADIAL_MENU_CONSTS.SPG_AREA, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTENTION_TO_POSITION, action=BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION, icon=RADIAL_MENU_CONSTS.ATTENTION_TO, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT, RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKING_ENEMY, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY, icon=RADIAL_MENU_CONSTS.ATTACKING_ENEMY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACK_ENEMY_WITH_SPG, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY, icon=RADIAL_MENU_CONSTS.ATTACKING_ENEMY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACK_ENEMY, action=BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY, icon=RADIAL_MENU_CONSTS.ATTACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY, RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_DEFENDING_BASE, action=BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE, icon=RADIAL_MENU_CONSTS.DEFENDING_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTENTION_TO_BASE_DEF, action=BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE, icon=RADIAL_MENU_CONSTS.DEFEND_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKING_BASE, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, icon=RADIAL_MENU_CONSTS.ATTACKING_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTENTION_TO_BASE_ATK, action=BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE, icon=RADIAL_MENU_CONSTS.ATTACK_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_ALLY_HQ_DEFEND_COMMIT, action=BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE, icon=RADIAL_MENU_CONSTS.DEFENDING_HQ, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ALLY_HQ_DEFEND_COMMAND, action=BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE, icon=RADIAL_MENU_CONSTS.DEFEND_HQ, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_ENEMY_HQ_ATTACK_COMMIT, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE, icon=RADIAL_MENU_CONSTS.ATTACKING_HQ, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ENEMY_HQ_ATTACK_COMMAND, action=BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE, icon=RADIAL_MENU_CONSTS.ATTACK_HQ, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH))
ALLY_UPPER_SHORTCUTS_DEFAULT = (Shortcut(title=INGAME_HELP.RADIALMENU_SUPPORTING_ALLY, action=BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, icon=RADIAL_MENU_CONSTS.SUPPORTING_ALLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_HELPMEEX, action=BATTLE_CHAT_COMMAND_NAMES.HELPME, icon=RADIAL_MENU_CONSTS.HELP_ME_EX, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_TURN_BACK, action=BATTLE_CHAT_COMMAND_NAMES.TURNBACK, icon=RADIAL_MENU_CONSTS.TURN_BACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_THANKS, action=BATTLE_CHAT_COMMAND_NAMES.THANKS, icon=RADIAL_MENU_CONSTS.THANK_YOU, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND))
ALLY_UPPER_SHORTCUTS_ONE_DISABLED = (Shortcut(title=INGAME_HELP.RADIALMENU_SUPPORTING_ALLY, action=BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, icon=RADIAL_MENU_CONSTS.SUPPORTING_ALLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_HELPMEEX, action=BATTLE_CHAT_COMMAND_NAMES.HELPME, icon=RADIAL_MENU_CONSTS.HELP_ME_EX, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_TURN_BACK, action=BATTLE_CHAT_COMMAND_NAMES.TURNBACK, icon=RADIAL_MENU_CONSTS.TURN_BACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_THANKS, action=BATTLE_CHAT_COMMAND_NAMES.THANKS, icon=RADIAL_MENU_CONSTS.THANK_YOU, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND))
ALLY_UPPER_SHORTCUTS_THREE_DISABLED = (Shortcut(title=INGAME_HELP.RADIALMENU_SUPPORTING_ALLY, action=BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, icon=RADIAL_MENU_CONSTS.SUPPORTING_ALLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_HELPMEEX, action=BATTLE_CHAT_COMMAND_NAMES.HELPME, icon=RADIAL_MENU_CONSTS.HELP_ME_EX, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_TURN_BACK, action=BATTLE_CHAT_COMMAND_NAMES.TURNBACK, icon=RADIAL_MENU_CONSTS.TURN_BACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_THANKS, action=BATTLE_CHAT_COMMAND_NAMES.THANKS, icon=RADIAL_MENU_CONSTS.THANK_YOU, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND))
_MARKERS_TYPE_TO_SUBTYPE_MAP = {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_ALLY,
                                  DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY},
 MarkerType.BASE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY,
                               DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY},
 MarkerType.HEADQUARTER_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ALLY,
                                      DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_HQ_ENEMY},
 MarkerType.LOCATION_MARKER_TYPE: {LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.SPG_AIM_AREA_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.SHOOTING_POINT_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.VEHICLE_SPOTPOINT_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.NAVIGATION_POINT_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   INVALID_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT},
 MarkerType.INVALID_MARKER_TYPE: {INVALID_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_EMPTY}}
_CAN_CANCEL_REPLY_SHORTCUT = Shortcut(title=INGAME_HELP.RADIALMENU_CANCEL_REPLY, action=BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY, icon=RADIAL_MENU_CONSTS.NO, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
_CONFIRM_SHORTCUT = Shortcut(title=INGAME_HELP.RADIALMENU_POSITIVE, action=BATTLE_CHAT_COMMAND_NAMES.REPLY, icon=RADIAL_MENU_CONSTS.YES, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
_THANKS_SHORTCUT = Shortcut(title=INGAME_HELP.RADIALMENU_THANKS, action=BATTLE_CHAT_COMMAND_NAMES.THANKS, icon=RADIAL_MENU_CONSTS.THANK_YOU, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
_EMPTY_BUTTON_SHORTCUT = Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)

def buildShortcutMap(shortcuts):
    result = {}
    for s in shortcuts:
        for group in s.groups:
            result.setdefault(group, []).append(s)

    return result


_BOTTOM_SHORTCUT_SETS = buildShortcutMap(REGULAR_BOTTOM_STATIC_SHORTCUTS)
_UPPER_SHORTCUT_SETS = buildShortcutMap(REGULAR_UPPER_STATIC_SHORTCUTS)

def getKeyFromAction(action):
    if action in CONTEXT_ACTIONS:
        shortcut = CommandMapping.g_instance.getName(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND)
    elif action in COMMIT_ACTIONS:
        shortcut = CommandMapping.g_instance.getName(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMIT)
    elif action in KB_MAPPING:
        cmd = KB_MAPPING[action]
        shortcut = CommandMapping.g_instance.getName(cmd)
    else:
        return 0
    return getScaleformKey(CommandMapping.g_instance.get(shortcut))


class RadialMenu(RadialMenuMeta, BattleGUIKeyHandler, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)
    _REFRESH_TIME_IN_SECONDS = 0.3

    def __init__(self):
        super(RadialMenu, self).__init__()
        self._crosshairData = None
        self.__stateData = None
        self.__isVisible = False
        self.__logger = ChatHotkeyLogger()
        return

    def handleEscKey(self, isDown):
        return True

    def onAction(self, action):
        chatCommands = self.sessionProvider.shared.chatCommands
        if chatCommands is None:
            return
        elif action == RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE or self._crosshairData is None:
            self.__setVisibility(False)
            return
        else:
            self.__logger.logCommandSelected(action, self._crosshairData.targetMarkerType)
            if action == BATTLE_CHAT_COMMAND_NAMES.REPLY:
                if self._crosshairData.replyState == ReplyState.CAN_CONFIRM and self._crosshairData.replyToAction in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                    chatCommands.handleChatCommand(ONE_SHOT_COMMANDS_TO_REPLIES[self._crosshairData.replyToAction], targetID=self._crosshairData.targetID)
                else:
                    chatCommands.sendReplyChatCommand(self._crosshairData.targetID, self._crosshairData.replyToAction)
            elif action == BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY:
                chatCommands.sendCancelReplyChatCommand(self._crosshairData.targetID, self._crosshairData.replyToAction)
            elif action in (BATTLE_CHAT_COMMAND_NAMES.GOING_THERE, BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION, BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA):
                chatCommands.sendAdvancedPositionPing(action, isInRadialMenu=True)
            else:
                chatCommands.handleChatCommand(action, targetID=self._crosshairData.targetID, isInRadialMenu=True)
            self._crosshairData = None
            self.__setVisibility(False)
            return

    def onSelect(self):
        self.__playSound(SoundEffectsId.SELECT_RADIAL_BUTTON)

    def onHideCompleted(self):
        self.__setVisibility(False)
        ctrl = self.sessionProvider.shared.calloutCtrl
        if ctrl is not None and ctrl.isRadialMenuOpened():
            ctrl.resetRadialMenuData()
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
            if self.app.hasGuiControlModeConsumers(self.getAlias()):
                self.app.leaveGuiControlMode(self.getAlias())
        return

    def onRefresh(self):
        if self.__isVisible:
            self.show()

    def show(self, reshowPreviousState=False):
        chatCommands = self.sessionProvider.shared.chatCommands
        if chatCommands is None:
            return
        else:
            if reshowPreviousState:
                targetID, targetMarkerType, crosshairType, _, _ = self._crosshairData
                replyState, replyToAction = chatCommands.getReplyStateForTargetIDAndMarkerType(targetID, targetMarkerType)
            else:
                targetID, targetMarkerType, crosshairType, replyState, replyToAction = chatCommands.getAimedAtTargetData()
            menuState = self._getRadialMenuState(targetID, targetMarkerType, crosshairType, replyState, replyToAction)
            replyStateDiff = self.__generateDiffStateDict(menuState, replyState, replyToAction, targetID)
            ctrl = self.sessionProvider.shared.crosshair
            if ctrl is not None:
                position = ctrl.getDisaredPosition()
            else:
                guiScreenWidth, guiScreenHeight = GUI.screenResolution()
                position = (guiScreenWidth * 0.5, guiScreenHeight * 0.5)
            if self.app is not None:
                self.app.registerGuiKeyHandler(self)
            self.__setVisibility(True)
            self._showInternal(menuState, replyStateDiff, position)
            if RadialMenu.__isMarkerEmptyLocationOrOutOfBorder(self._crosshairData.targetMarkerType, self._crosshairData.targetMarkerSubtype):
                self.delayCallback(self._REFRESH_TIME_IN_SECONDS, self.__checkForValidLocationMarkerLoop)
            if RadialMenu.__isCanRespondToAlly(self._crosshairData.targetMarkerType, self._crosshairData.targetMarkerSubtype, self._crosshairData.replyState):
                self.delayCallback(self._REFRESH_TIME_IN_SECONDS, self.__checkForTemporaryRespondUpdateLoop)
            return

    def hide(self, allowAction=True):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        if not self.__isVisible:
            return
        else:
            self.as_hideS(allowAction)
            self.stopCallback(self.__checkForValidLocationMarkerLoop)
            self.stopCallback(self.__checkForTemporaryRespondUpdateLoop)
            return

    def _populate(self):
        super(RadialMenu, self)._populate()
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.__refreshShortcutsAndState()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            ctrl.onAddCommandReceived += self.__onAddCommandReceived
        return

    def _dispose(self):
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            ctrl.onAddCommandReceived -= self.__onAddCommandReceived
        super(RadialMenu, self)._dispose()
        return

    def _showInternal(self, radialState, diff, position):
        cursorX, cursorY = GUI.mcursor().position
        self.as_showS(cursorX, cursorY, radialState, diff, position)

    def _getRadialMenuState(self, targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction):
        viewState = self._getViewStateForMarker(targetMarkerType, targetMarkerSubtype)
        viewState = self.__adjustStateForSPG(viewState, replyState)
        self._crosshairData = CrosshairData(targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction)
        return self._sanitizeViewState(viewState)

    def _getViewStateForMarker(self, targetMarkerType, targetMarkerSubtype):
        if targetMarkerType in _MARKERS_TYPE_TO_SUBTYPE_MAP and targetMarkerSubtype in _MARKERS_TYPE_TO_SUBTYPE_MAP[targetMarkerType]:
            return _MARKERS_TYPE_TO_SUBTYPE_MAP[targetMarkerType][targetMarkerSubtype]
        _logger.warning("Marker subtype name '%s' is not defined for '%s'.", targetMarkerSubtype, targetMarkerType)
        return RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT

    def _sanitizeViewState(self, viewState):
        return viewState if viewState in RADIAL_MENU_CONSTS.ALL_TARGET_STATES else RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT

    def _getUpperShortcuts(self):
        return _UPPER_SHORTCUT_SETS

    def __setVisibility(self, newState):
        if newState == self.__isVisible:
            return
        self.__isVisible = newState
        gui_event_dispatcher.toggleCrosshairVisibility()

    def __onMappingChanged(self, *args):
        self.__refreshShortcutsAndState()

    def __refreshShortcutsAndState(self):
        self.__stateData = []

        def createShortcut(shortcutData):
            return {'title': shortcutData.title,
             'action': shortcutData.action,
             'icon': shortcutData.icon,
             'bState': shortcutData.bState,
             'indexInGroup': shortcutData.indexInGroup,
             'key': getKeyFromAction(shortcutData.action)}

        for state in RADIAL_MENU_CONSTS.ALL_TARGET_STATES:
            bottomShortcuts = map(createShortcut, _BOTTOM_SHORTCUT_SETS[state])
            if state == RADIAL_MENU_CONSTS.TARGET_STATE_ALLY:
                regularShortcuts = map(createShortcut, ALLY_UPPER_SHORTCUTS_DEFAULT)
            else:
                regularShortcuts = map(createShortcut, self._getUpperShortcuts().get(state, []))
            self.__stateData.append({'state': state,
             'bottomShortcuts': bottomShortcuts,
             'regularShortcuts': regularShortcuts})

        self.as_buildDataS(self.__stateData)

    def __adjustStateForSPG(self, viewState, replyState):
        if not self.sessionProvider.getArenaDP().getVehicleInfo().isSPG():
            return viewState
        if viewState == RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY:
            return RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY
        return RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT if viewState == RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT and replyState != ReplyState.CAN_REPLY else viewState

    def __playSound(self, soundName):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(soundName)
        return

    def __generateDiffStateDict(self, targetState, replyState, replyAction, targetID):
        resultingDiffList = []
        if targetState not in self._getUpperShortcuts() and targetState != RADIAL_MENU_CONSTS.TARGET_STATE_ALLY or targetState not in _BOTTOM_SHORTCUT_SETS or self.__stateData is None:
            return resultingDiffList
        else:
            if targetState == RADIAL_MENU_CONSTS.TARGET_STATE_ALLY:
                self.__populateWithAllyData(replyAction, replyState, resultingDiffList, targetID)
            else:
                if replyState in (ReplyState.CAN_CANCEL_REPLY, ReplyState.CAN_REPLY, ReplyState.CAN_CONFIRM):
                    self.__populateWithNonAllyData(replyState, resultingDiffList, targetState)
                self.__handleSpgView(resultingDiffList, targetState)
            return resultingDiffList

    def __populateWithNonAllyData(self, replyState, resultingDiffList, targetState):
        for shortcut in self._getUpperShortcuts()[targetState]:
            buttonData = defaultdict()
            RadialMenu.__copyShortcutData(buttonData=buttonData, shortcut=shortcut)
            if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST:
                defaultShortcut = self.__adjustPrimaryRadialButton(replyState, shortcut, BATTLE_CHAT_COMMAND_NAMES.REPLY)
                RadialMenu.__copyShortcutData(buttonData=buttonData, shortcut=defaultShortcut)
                buttonData['key'] = getKeyFromAction(BATTLE_CHAT_COMMAND_NAMES.REPLY)
            elif shortcut.bState != RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE:
                buttonData['bState'] = RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE
            if 'key' not in buttonData:
                buttonData['key'] = getKeyFromAction(shortcut.action)
            resultingDiffList.append(buttonData)

    def __populateWithAllyData(self, replyAction, replyState, resultingDiffList, targetID):
        buttonDataTemplate = ALLY_UPPER_SHORTCUTS_DEFAULT
        chatCommands = self.sessionProvider.shared.chatCommands
        if chatCommands is not None and chatCommands.isTargetAllyCommittedToMe(targetID):
            buttonDataTemplate = ALLY_UPPER_SHORTCUTS_ONE_DISABLED
        if (replyState == ReplyState.CAN_CONFIRM or replyState == ReplyState.CAN_RESPOND) and replyAction != BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN:
            buttonDataTemplate = ALLY_UPPER_SHORTCUTS_THREE_DISABLED
        for shortcut in buttonDataTemplate:
            buttonData = defaultdict()
            RadialMenu.__copyShortcutData(buttonData=buttonData, shortcut=shortcut)
            if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST:
                canReplyAction = BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY if replyAction in (BATTLE_CHAT_COMMAND_NAMES.HELPME, BATTLE_CHAT_COMMAND_NAMES.SOS) else BATTLE_CHAT_COMMAND_NAMES.REPLY
                if replyState == ReplyState.CAN_RESPOND and replyAction is BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY:
                    defaultShortcut = _THANKS_SHORTCUT
                else:
                    defaultShortcut = self.__adjustPrimaryRadialButton(replyState, shortcut, canReplyAction)
                RadialMenu.__copyShortcutData(buttonData=buttonData, shortcut=defaultShortcut)
                if replyState in (ReplyState.CAN_CANCEL_REPLY, ReplyState.CAN_REPLY, ReplyState.CAN_CONFIRM):
                    buttonData['key'] = getKeyFromAction(BATTLE_CHAT_COMMAND_NAMES.REPLY)
            elif shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH and replyState in (ReplyState.CAN_REPLY, ReplyState.CAN_CANCEL_REPLY, ReplyState.CAN_CONFIRM):
                self.__unbindKeyShortcutFromButton(buttonData)
            if 'key' not in buttonData:
                buttonData['key'] = getKeyFromAction(shortcut.action)
            resultingDiffList.append(buttonData)

        return

    def __adjustPrimaryRadialButton(self, replyState, shortcut, canReplyAction):
        if replyState == ReplyState.CAN_REPLY:
            defaultShortcut = Shortcut(title=shortcut.title, action=canReplyAction, icon=shortcut.icon, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=shortcut.indexInGroup)
        elif replyState == ReplyState.CAN_CANCEL_REPLY:
            defaultShortcut = _CAN_CANCEL_REPLY_SHORTCUT
        elif replyState == ReplyState.CAN_CONFIRM:
            defaultShortcut = _CONFIRM_SHORTCUT
        else:
            defaultShortcut = shortcut
        return defaultShortcut

    def __handleSpgView(self, resultingDiffList, targetState):
        if self.sessionProvider.getArenaDP().getVehicleInfo().isSPG() and avatar_getter.getInputHandler().ctrlModeName in (CTRL_MODE_NAME.STRATEGIC, CTRL_MODE_NAME.ARTY, CTRL_MODE_NAME.MAP_CASE) and targetState in (RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT, RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY) and not resultingDiffList:
            for shortcut in self._getUpperShortcuts()[targetState]:
                buttonData = defaultdict()
                RadialMenu.__copyShortcutData(buttonData, shortcut)
                if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH:
                    self.__unbindKeyShortcutFromButton(buttonData)
                elif shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST:
                    buttonData['key'] = getKeyFromAction(BATTLE_CHAT_COMMAND_NAMES.REPLY)
                resultingDiffList.append(buttonData)

    def __disableButton(self, buttonData):
        buttonData['bState'] = RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE
        self.__unbindKeyShortcutFromButton(buttonData)

    def __unbindKeyShortcutFromButton(self, buttonData):
        buttonData['key'] = BW_TO_SCALEFORM[Keys.KEY_NONE]

    @staticmethod
    def __copyShortcutData(buttonData, shortcut):
        buttonData['title'] = shortcut.title
        buttonData['action'] = shortcut.action
        buttonData['icon'] = shortcut.icon
        buttonData['bState'] = shortcut.bState
        buttonData['indexInGroup'] = shortcut.indexInGroup

    def __onReplyFeedbackReceived(self, uniqueTargetID, replierID, markerType, oldReplyCount, newReplyCount):
        if oldReplyCount != 0 and newReplyCount != 0:
            return
        self.__reshow(uniqueTargetID, markerType, True)

    def __onRemoveCommandReceived(self, removedID, markerType):
        self.__reshow(removedID, markerType, markerType != MarkerType.LOCATION_MARKER_TYPE)

    def __reshow(self, removedID, markerType, reshowPreviousState):
        if not self.__isVisible or self._crosshairData is None:
            return
        else:
            if self._crosshairData.targetID == removedID and markerType == self._crosshairData.targetMarkerType:
                self.show(reshowPreviousState)
            return

    def __onVehicleMarkerRemoved(self, vehicleID):
        if self._crosshairData is not None and self._crosshairData.targetID == vehicleID:
            self.delayCallback(self._REFRESH_TIME_IN_SECONDS, self.__reshow, vehicleID, MarkerType.VEHICLE_MARKER_TYPE, False)
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD and self._crosshairData is not None and self._crosshairData.targetID == vehicleID:
            self.delayCallback(self._REFRESH_TIME_IN_SECONDS, self.__reshow, vehicleID, MarkerType.VEHICLE_MARKER_TYPE, False)
        return

    def __onAddCommandReceived(self, addedID, markerType):
        if markerType != MarkerType.LOCATION_MARKER_TYPE:
            self.__reshow(addedID, markerType, True)

    def __checkForValidLocationMarkerLoop(self):
        if self._crosshairData is None or not self.__isVisible:
            return
        else:
            chatCommands = self.sessionProvider.shared.chatCommands
            _, targetMarkerType, targetMarkerSubtype, _, _ = chatCommands.getAimedAtTargetData()
            if RadialMenu.__isMarkerEmptyLocationOrOutOfBorder(targetMarkerType, targetMarkerSubtype) and targetMarkerType != self._crosshairData.targetMarkerType:
                self.show(reshowPreviousState=False)
            hasDelayedCallback = self.hasDelayedCallback(self.__checkForValidLocationMarkerLoop)
            return self._REFRESH_TIME_IN_SECONDS if not hasDelayedCallback else None

    def __checkForTemporaryRespondUpdateLoop(self):
        if self._crosshairData is None or not self.__isVisible:
            return
        else:
            chatCommands = self.sessionProvider.shared.chatCommands
            _, targetMarkerType, targetMarkerSubtype, replyState, _ = chatCommands.getAimedAtTargetData()
            if RadialMenu.__isCanRespondToAlly(targetMarkerType, targetMarkerSubtype, replyState):
                return self._REFRESH_TIME_IN_SECONDS
            self.show(reshowPreviousState=False)
            return -1

    @staticmethod
    def __isMarkerEmptyLocationOrOutOfBorder(markerType, markerSubType):
        return markerType in (MarkerType.INVALID_MARKER_TYPE, MarkerType.LOCATION_MARKER_TYPE) and markerSubType == INVALID_MARKER_SUBTYPE

    @staticmethod
    def __isCanRespondToAlly(markerType, markerSubType, replyState):
        return replyState == ReplyState.CAN_RESPOND and markerType == MarkerType.VEHICLE_MARKER_TYPE and markerSubType == DefaultMarkerSubType.ALLY_MARKER_SUBTYPE
