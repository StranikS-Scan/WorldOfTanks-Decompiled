# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/radial_menu.py
from collections import namedtuple, defaultdict
import logging
import GUI
import Keys
import CommandMapping
from AvatarInputHandler import aih_global_binding
from aih_constants import CTRL_MODE_NAME
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, ReplyState, MarkerType, DefaultMarkerSubType, ONE_SHOT_COMMANDS_TO_REPLIES, INVALID_MARKER_SUBTYPE, LocationMarkerSubType
from gui.Scaleform.daapi.view.meta.RadialMenuMeta import RadialMenuMeta
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import event_dispatcher as gui_event_dispatcher, avatar_getter
from gui.battle_control.controllers.chat_cmd_ctrl import KB_MAPPING, getAimedAtPositionWithinBorders
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.utils.key_mapping import getScaleformKey, BW_TO_SCALEFORM
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_SHORTCUTS_IN_GROUP = 6
Shortcut = namedtuple('Shortcut', ('title', 'action', 'icon', 'groups', 'bState', 'indexInGroup'))
CrosshairData = namedtuple('CrosshairData', ('targetID', 'targetMarkerType', 'targetMarkerSubtype', 'replyState', 'replyToAction'))
REGULAR_BOTTOM_STATIC_SHORTCUTS = (Shortcut(title=INGAME_HELP.RADIALMENU_RELOADINGGUN, action=BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN, icon=RADIAL_MENU_CONSTS.RELOAD, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_THIRD), Shortcut(title=INGAME_HELP.RADIALMENU_HELPME, action=BATTLE_CHAT_COMMAND_NAMES.SOS, icon=RADIAL_MENU_CONSTS.SOS, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FOURTH))
REGULAR_UPPER_STATIC_SHORTCUTS = (Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
  RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT], bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
  RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY,
  RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY,
  RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT], bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND),
 Shortcut(title=INGAME_HELP.RADIALMENU_GOING_THERE, action=BATTLE_CHAT_COMMAND_NAMES.GOING_THERE, icon=RADIAL_MENU_CONSTS.GOING_THERE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKAREASPG, action=BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA, icon=RADIAL_MENU_CONSTS.SPG_AREA, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTENTION_TO_POSITION, action=BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION, icon=RADIAL_MENU_CONSTS.ATTENTION_TO, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT, RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_SUPPORTING_ALLY, action=BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, icon=RADIAL_MENU_CONSTS.SUPPORTING_ALLY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_HELPMEEX, action=BATTLE_CHAT_COMMAND_NAMES.HELPME, icon=RADIAL_MENU_CONSTS.HELP_ME_EX, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_TURN_BACK, action=BATTLE_CHAT_COMMAND_NAMES.TURNBACK, icon=RADIAL_MENU_CONSTS.TURN_BACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIFTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_THANKS, action=BATTLE_CHAT_COMMAND_NAMES.THANKS, icon=RADIAL_MENU_CONSTS.THANK_YOU, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SECOND),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKING_ENEMY, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY, icon=RADIAL_MENU_CONSTS.ATTACKING_ENEMY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACK_ENEMY_WITH_SPG, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG, icon=RADIAL_MENU_CONSTS.ATTACKING_ENEMY, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACK_ENEMY, action=BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY, icon=RADIAL_MENU_CONSTS.ATTACK, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY, RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_DEFENDING_BASE, action=BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE, icon=RADIAL_MENU_CONSTS.DEFENDING_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTENTION_TO_BASE_DEF, action=BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE, icon=RADIAL_MENU_CONSTS.DEFEND_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTACKING_BASE, action=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, icon=RADIAL_MENU_CONSTS.ATTACKING_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST),
 Shortcut(title=INGAME_HELP.RADIALMENU_ATTENTION_TO_BASE_ATK, action=BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE, icon=RADIAL_MENU_CONSTS.ATTACK_BASE, groups=[RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY], bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH))
_MARKERS_TYPE_TO_SUBTYPE_MAP = {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_ALLY,
                                  DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY},
 MarkerType.BASE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ALLY,
                               DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_BASE_ENEMY},
 MarkerType.LOCATION_MARKER_TYPE: {LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT,
                                   LocationMarkerSubType.SPG_AIM_AREA_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT},
 MarkerType.INVALID_MARKER_TYPE: {INVALID_MARKER_SUBTYPE: RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT}}
_EMPTY_CROSSHAIRDATA = CrosshairData(targetID=0, targetMarkerType=MarkerType.INVALID_MARKER_TYPE, targetMarkerSubtype=RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT, replyState=ReplyState.NO_REPLY, replyToAction='')
_CAN_CANCEL_REPLY_SHORTCUT = Shortcut(title=INGAME_HELP.RADIALMENU_CANCEL_REPLY, action=BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY, icon=RADIAL_MENU_CONSTS.NO, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
_CONFIRM_SHORTCUT = Shortcut(title=INGAME_HELP.RADIALMENU_POSITIVE, action=BATTLE_CHAT_COMMAND_NAMES.REPLY, icon=RADIAL_MENU_CONSTS.YES, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
_EMPTY_BUTTON_SHORTCUT = Shortcut(title=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, action=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, icon=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE, indexInGroup=RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST)
BOTTOM_SHORTCUT_SETS = {}
UPPER_SHORTCUT_SETS = {}
for s in REGULAR_BOTTOM_STATIC_SHORTCUTS:
    for group in s.groups:
        if group not in BOTTOM_SHORTCUT_SETS:
            BOTTOM_SHORTCUT_SETS[group] = list()
        BOTTOM_SHORTCUT_SETS[group].append(s)

for s in REGULAR_UPPER_STATIC_SHORTCUTS:
    for group in s.groups:
        if group not in UPPER_SHORTCUT_SETS:
            UPPER_SHORTCUT_SETS[group] = list()
        UPPER_SHORTCUT_SETS[group].append(s)

def getKeyFromAction(action):
    if action in (BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE,
     BATTLE_CHAT_COMMAND_NAMES.HELPME,
     BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
     BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
     BATTLE_CHAT_COMMAND_NAMES.REPLY,
     BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY):
        shortcut = CommandMapping.g_instance.getName(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND)
        scaleFormKey = getScaleformKey(CommandMapping.g_instance.get(shortcut))
    elif action in (BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
     BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
     BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA,
     BATTLE_CHAT_COMMAND_NAMES.GOING_THERE):
        shortcut = CommandMapping.g_instance.getName(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMIT)
        scaleFormKey = getScaleformKey(CommandMapping.g_instance.get(shortcut))
    elif action in KB_MAPPING:
        cmd = KB_MAPPING[action]
        shortcut = CommandMapping.g_instance.getName(cmd)
        scaleFormKey = getScaleformKey(CommandMapping.g_instance.get(shortcut))
    else:
        return 0
    return scaleFormKey


class RadialMenu(RadialMenuMeta, BattleGUIKeyHandler):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def __init__(self):
        super(RadialMenu, self).__init__()
        self.__crosshairData = _EMPTY_CROSSHAIRDATA
        self.__stateData = None
        self.__isVisible = False
        return

    def handleEscKey(self, isDown):
        return True

    def onAction(self, action):
        chatCommands = self.sessionProvider.shared.chatCommands
        if chatCommands is None:
            return
        elif action == RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE or self.__crosshairData is _EMPTY_CROSSHAIRDATA:
            self.__setVisibility(False)
            return
        else:
            if action == BATTLE_CHAT_COMMAND_NAMES.REPLY:
                if self.__crosshairData.replyState == ReplyState.CAN_CONFIRM and self.__crosshairData.replyToAction in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                    chatCommands.handleChatCommand(ONE_SHOT_COMMANDS_TO_REPLIES[self.__crosshairData.replyToAction], targetID=self.__crosshairData.targetID)
                else:
                    chatCommands.sendReplyChatCommand(self.__crosshairData.targetID, self.__crosshairData.replyToAction)
            elif action == BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY:
                chatCommands.sendCancelReplyChatCommand(self.__crosshairData.targetID, self.__crosshairData.replyToAction)
            elif action in (BATTLE_CHAT_COMMAND_NAMES.GOING_THERE, BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION, BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA):
                chatCommands.sendAdvancedPositionPing(action, isInRadialMenu=True)
            else:
                chatCommands.handleChatCommand(action, targetID=self.__crosshairData.targetID, isInRadialMenu=True)
            self.__crosshairData = _EMPTY_CROSSHAIRDATA
            self.__setVisibility(False)
            return

    def onSelect(self):
        self.__playSound(SoundEffectsId.SELECT_RADIAL_BUTTON)

    def onHideCompleted(self):
        self.__setVisibility(False)

    def show(self, reshowPreviousState=False):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            chatCommands = self.sessionProvider.shared.chatCommands
            if chatCommands is None:
                return
            if reshowPreviousState:
                targetID, targetMarkerType, crosshairType, _, _ = self.__crosshairData
            else:
                targetID, targetMarkerType, crosshairType = chatCommands.getAimedAtTargetData()
            replyState, replyToAction = advChatCmp.getReplyStateForTargetIDAndMarkerType(targetID, targetMarkerType)
            menuState = self.__getRadialMenuState(targetID, targetMarkerType, crosshairType, replyState, replyToAction)
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
            return

    def hide(self, allowAction=True):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        if self.__isVisible is False:
            return
        else:
            self.as_hideS(allowAction)
            return

    def _populate(self):
        super(RadialMenu, self)._populate()
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.__refreshShortcutsAndState()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        return

    def _dispose(self):
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        super(RadialMenu, self)._dispose()
        return

    def _showInternal(self, radialState, diff, position):
        self.as_showS(radialState, diff, position)

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
            bottomShortcuts = map(createShortcut, BOTTOM_SHORTCUT_SETS[state])
            regularShortcuts = map(createShortcut, UPPER_SHORTCUT_SETS[state])
            self.__stateData.append({'state': state,
             'bottomShortcuts': bottomShortcuts,
             'regularShortcuts': regularShortcuts})

        self.as_buildDataS(self.__stateData)

    def __getRadialMenuState(self, targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction):
        if targetMarkerType in _MARKERS_TYPE_TO_SUBTYPE_MAP and targetMarkerSubtype in _MARKERS_TYPE_TO_SUBTYPE_MAP[targetMarkerType]:
            viewState = _MARKERS_TYPE_TO_SUBTYPE_MAP[targetMarkerType][targetMarkerSubtype]
        else:
            _logger.warning("Marker subtype name '%s' is not defined for '%s'.", targetMarkerSubtype, targetMarkerType)
            viewState = RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT
        if self.sessionProvider.getArenaDP().getVehicleInfo().isSPG():
            if viewState == RADIAL_MENU_CONSTS.TARGET_STATE_ENEMY:
                viewState = RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY
            elif viewState == RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT:
                if replyState == ReplyState.CAN_REPLY:
                    viewState = RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT
                else:
                    viewState = RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT
        self.__crosshairData = CrosshairData(targetID, targetMarkerType, targetMarkerSubtype, replyState, replyToAction)
        return viewState if viewState in RADIAL_MENU_CONSTS.ALL_TARGET_STATES else RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT

    def __playSound(self, soundName):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(soundName)
        return

    def __generateDiffStateDict(self, targetState, replyState, replyAction, targetID):
        if targetState not in UPPER_SHORTCUT_SETS or targetState not in BOTTOM_SHORTCUT_SETS or self.__stateData is None:
            return
        else:
            resultingDiffList = []
            if replyState in (ReplyState.CAN_CANCEL_REPLY, ReplyState.CAN_REPLY, ReplyState.CAN_CONFIRM):
                for shortcut in UPPER_SHORTCUT_SETS[targetState]:
                    buttonData = defaultdict()
                    RadialMenu.__copyShortcutData(buttonData=buttonData, shortcut=shortcut)
                    if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST:
                        if replyState == ReplyState.CAN_REPLY:
                            defaultShortcut = Shortcut(title=shortcut.title, action=BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY if replyAction in (BATTLE_CHAT_COMMAND_NAMES.HELPME, BATTLE_CHAT_COMMAND_NAMES.SOS) else BATTLE_CHAT_COMMAND_NAMES.REPLY, icon=shortcut.icon, groups=RADIAL_MENU_CONSTS.ALL_TARGET_STATES, bState=RADIAL_MENU_CONSTS.NORMAL_BUTTON_STATE, indexInGroup=shortcut.indexInGroup)
                        elif replyState == ReplyState.CAN_CANCEL_REPLY:
                            defaultShortcut = _CAN_CANCEL_REPLY_SHORTCUT
                        else:
                            defaultShortcut = _CONFIRM_SHORTCUT
                        RadialMenu.__copyShortcutData(buttonData=buttonData, shortcut=defaultShortcut)
                        buttonData['key'] = getKeyFromAction(BATTLE_CHAT_COMMAND_NAMES.REPLY)
                    elif shortcut.bState != RADIAL_MENU_CONSTS.EMPTY_BUTTON_STATE:
                        if targetState == RADIAL_MENU_CONSTS.TARGET_STATE_ALLY and replyState in (ReplyState.CAN_REPLY, ReplyState.CAN_CANCEL_REPLY):
                            if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH:
                                buttonData['key'] = BW_TO_SCALEFORM[Keys.KEY_NONE]
                        else:
                            buttonData['bState'] = RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE
                    if 'key' not in buttonData:
                        buttonData['key'] = getKeyFromAction(shortcut.action)
                    resultingDiffList.append(buttonData)

            self.__handleSpgView(resultingDiffList, targetState)
            self.__ensureHelpIsNotPossible(resultingDiffList, targetID, targetState)
            self.__fillWithEmptyButtonsIfPositionNotValid(targetState, replyState, resultingDiffList)
            return resultingDiffList

    def __handleSpgView(self, resultingDiffList, targetState):
        if self.sessionProvider.getArenaDP().getVehicleInfo().isSPG() and avatar_getter.getInputHandler().ctrlModeName in (CTRL_MODE_NAME.STRATEGIC, CTRL_MODE_NAME.ARTY, CTRL_MODE_NAME.MAP_CASE) and targetState in (RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT, RADIAL_MENU_CONSTS.TARGET_STATE_SPG_ENEMY) and not resultingDiffList:
            for shortcut in UPPER_SHORTCUT_SETS[targetState]:
                buttonData = defaultdict()
                RadialMenu.__copyShortcutData(buttonData, shortcut)
                if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH:
                    buttonData['key'] = BW_TO_SCALEFORM[Keys.KEY_NONE]
                elif shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_FIRST:
                    buttonData['key'] = getKeyFromAction(BATTLE_CHAT_COMMAND_NAMES.REPLY)
                resultingDiffList.append(buttonData)

    def __ensureHelpIsNotPossible(self, resultingDiffList, targetID, targetState):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is not None and advChatCmp.isTargetAllyCommitedToMe(targetID) and targetState == RADIAL_MENU_CONSTS.TARGET_STATE_ALLY:
            if not resultingDiffList:
                for shortcut in UPPER_SHORTCUT_SETS[targetState]:
                    buttonData = defaultdict()
                    RadialMenu.__copyShortcutData(buttonData, shortcut)
                    if shortcut.indexInGroup == RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH:
                        buttonData['bState'] = RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE
                        buttonData['key'] = BW_TO_SCALEFORM[Keys.KEY_NONE]
                    else:
                        buttonData['key'] = getKeyFromAction(shortcut.action)
                    resultingDiffList.append(buttonData)

            else:
                for buttData in resultingDiffList:
                    if buttData['indexInGroup'] == RADIAL_MENU_CONSTS.ELEMENT_INDEX_SIXTH:
                        buttData['bState'] = RADIAL_MENU_CONSTS.DISABLED_BUTTON_STATE
                        buttData['key'] = BW_TO_SCALEFORM[Keys.KEY_NONE]

        return

    def __fillWithEmptyButtonsIfPositionNotValid(self, targetState, replyState, resultingDiffList):
        if (targetState == RADIAL_MENU_CONSTS.TARGET_STATE_DEFAULT or targetState == RADIAL_MENU_CONSTS.TARGET_STATE_SPG_DEFAULT) and replyState == ReplyState.NO_REPLY and getAimedAtPositionWithinBorders(self._aimOffset[0], self._aimOffset[1]) is None:
            for shortcut in UPPER_SHORTCUT_SETS[targetState]:
                buttonData = defaultdict()
                RadialMenu.__copyShortcutData(buttonData, _EMPTY_BUTTON_SHORTCUT)
                buttonData['key'] = BW_TO_SCALEFORM[Keys.KEY_NONE]
                buttonData['indexInGroup'] = shortcut.indexInGroup
                resultingDiffList.append(buttonData)

        return

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

    def __reshow(self, removedID, markerType, shouldReevaluate):
        if self.__isVisible is False:
            return
        if self.__crosshairData is not _EMPTY_CROSSHAIRDATA:
            if self.__crosshairData.targetID == removedID and markerType == self.__crosshairData.targetMarkerType:
                self.hide(allowAction=False)
                self.show(shouldReevaluate)
