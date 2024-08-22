# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/callout_ctrl.py
import logging
from collections import namedtuple
import BigWorld
import BattleReplay
import CommandMapping
from chat_commands_consts import _PERSONAL_MESSAGE_MUTE_DURATION, BATTLE_CHAT_COMMAND_NAMES
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import WindowLayer
from gui import GUI_CTRL_MODE_FLAG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import avatar_getter
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.event_dispatcher import _makeKeyCtx
from gui.battle_control.view_components import IViewComponentsController
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import GameEvent
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.account_helpers.settings_core import IBattleCommunicationsSettings
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_CALLOUT_MESSAGES_BLOCK_DURATION = 15
_HINT_TIMEOUT = 10
_DELAY_FOR_OPENING_RADIAL_MENU = 0.2
_CONSUMERS_LOCKS = (BATTLE_VIEW_ALIASES.FULL_STATS,
 VIEW_ALIAS.COMP7_BATTLE_PAGE,
 'chat',
 BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN,
 BATTLE_VIEW_ALIASES.BATTLE_ROYALE_WINNER_CONGRATS,
 BATTLE_VIEW_ALIASES.BR_PLAYER_STATS_IN_BATTLE,
 BATTLE_VIEW_ALIASES.FULLSCREEN_MAP)
CommandReceivedData = namedtuple('CommandReceivedData', ('name', 'targetIdToAnswer'))
_CALLOUT_COMMANDS_TO_REPLY_COMMANDS = {BATTLE_CHAT_COMMAND_NAMES.HELPME: BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK: BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.THANKS: BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY: BATTLE_CHAT_COMMAND_NAMES.THANKS}

class CalloutController(CallbackDelayer, IViewComponentsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    battleCommunications = dependency.descriptor(IBattleCommunicationsSettings)
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__isActive', '__isCalloutEnabled', '__isIBCEnabled', '__commandReceivedData', '__lastPersonalMsgTimestamp', '__lastCalloutTimestamp', '__ui', '__radialKeyDown', '__radialMenuIsOpen', '__previousForcedGuiControlModeFlags')

    def __init__(self, setup):
        super(CalloutController, self).__init__()
        self.__isActive = False
        self.__isCalloutEnabled = True
        self.__isIBCEnabled = None
        self.__commandReceivedData = None
        self.__lastPersonalMsgTimestamp = -_PERSONAL_MESSAGE_MUTE_DURATION
        self.__lastCalloutTimestamp = -_CALLOUT_MESSAGES_BLOCK_DURATION
        self.__ui = None
        self.__radialKeyDown = None
        self.__radialMenuIsOpen = False
        self.__previousForcedGuiControlModeFlags = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.CALLOUT

    def startControl(self):
        self.battleCommunications.onChanged += self.__onBattleCommunicationChanged
        self.__isCalloutEnabled = self.battleCommunications.showCalloutMessages
        self.__isIBCEnabled = self.battleCommunications.isEnabled
        if not self.__isIBCEnabled:
            return
        self.__activateListeners()

    def stopControl(self):
        CallbackDelayer.destroy(self)
        self.battleCommunications.onChanged -= self.__onBattleCommunicationChanged
        self.__deactivateListeners()
        self.__isActive = False
        self.__commandReceivedData = None
        self.__lastPersonalMsgTimestamp = -_PERSONAL_MESSAGE_MUTE_DURATION
        self.__lastCalloutTimestamp = -_CALLOUT_MESSAGES_BLOCK_DURATION
        self.resetRadialMenuData(onStop=True)
        return

    def setViewComponents(self, component):
        self.__ui = component
        self.__ui.onHidingFinished += self.__onCalloutHidingFinished

    def clearViewComponents(self):
        if self.__ui:
            self.__ui.onHidingFinished -= self.__onCalloutHidingFinished
        self.__ui = None
        return

    def isRadialMenuOpened(self):
        return self.__radialMenuIsOpen

    def resetRadialMenuData(self, onStop=False, reshow=False):
        if reshow:
            return
        else:
            isPlayerObserver = None if onStop else self.sessionProvider.getCtx().isPlayerObserver()
            if self.__radialKeyDown is not None and avatar_getter.isVehicleAlive() and not isPlayerObserver:
                self.__radialMenuIsOpen = False
                self.__radialKeyDown = None
                if self.hasDelayedCallback(self.__delayOpenRadialMenu):
                    self.stopCallback(self.__delayOpenRadialMenu)
            return

    def handleCalloutAndRadialMenuKeyPress(self, key, isDown):
        cmdMap = CommandMapping.g_instance
        isRadialMenuKey = cmdMap.isFired(CommandMapping.CMD_RADIAL_MENU_SHOW, key) or cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND, key)
        if not isRadialMenuKey:
            return False
        elif not self.__enabledForArenaBonusType():
            return False
        else:
            containerManager = self.__appLoader.getApp().containerManager
            if not containerManager.isContainerShown(WindowLayer.VIEW):
                return False
            elif containerManager.isModalViewsIsExists() or self.__appLoader.getApp().hasGuiControlModeConsumers(*_CONSUMERS_LOCKS):
                return False
            isPlayerObserver = self.sessionProvider.getCtx().isPlayerObserver()
            if self.__radialKeyDown is None and isDown:
                self.__radialKeyDown = key
                if not self.hasDelayedCallback(self.__delayOpenRadialMenu) and avatar_getter.isVehicleAlive() and not isPlayerObserver:
                    if self.__commandReceivedData is None and cmdMap.isFired(CommandMapping.CMD_RADIAL_MENU_SHOW, key):
                        self.__openRadialMenu()
                    else:
                        self.delayCallback(_DELAY_FOR_OPENING_RADIAL_MENU, self.__delayOpenRadialMenu)
                return True
            if self.__radialKeyDown is not None and not isDown:
                if not self.__radialMenuIsOpen:
                    if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND, key) and not avatar_getter.getForcedGuiControlModeFlags() & GUI_CTRL_MODE_FLAG.CURSOR_VISIBLE:
                        self.sessionProvider.handleContexChatCommand(key)
                    elif cmdMap.isFired(CommandMapping.CMD_RADIAL_MENU_SHOW, key) and not isPlayerObserver:
                        gui_event_dispatcher.setRespondToCalloutCmd(self.__radialKeyDown, isDown)
                    self.resetRadialMenuData()
                    return True
                if self.__radialKeyDown == key:
                    if self.__radialMenuIsOpen and avatar_getter.isVehicleAlive() and not isPlayerObserver:
                        gui_event_dispatcher.setRadialMenuCmd(key, False)
                    self.resetRadialMenuData()
                    return True
            return False

    def __activateListeners(self):
        g_messengerEvents.channels.onCommandReceived += self.__onCommandReceived
        g_eventBus.addListener(GameEvent.RESPOND_TO_CALLOUT, self.__handleCalloutButtonEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        BattleReplay.g_replayCtrl.onCommandReceived += self.__onCommandReceived

    def __deactivateListeners(self):
        g_messengerEvents.channels.onCommandReceived -= self.__onCommandReceived
        g_eventBus.removeListener(GameEvent.RESPOND_TO_CALLOUT, self.__handleCalloutButtonEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        BattleReplay.g_replayCtrl.onCommandReceived -= self.__onCommandReceived

    def __onCommandReceived(self, cmd):
        if not self.__isCalloutEnabled or not self.__isIBCEnabled or cmd.getCommandType() != MESSENGER_COMMAND_TYPE.BATTLE:
            return
        else:
            vehicleIDToAnswer = self.sessionProvider.getArenaDP().getVehIDBySessionID(cmd.getSenderID())
            commandName = _ACTIONS.battleChatCommandFromActionID(cmd.getID()).name
            if self.__isActive is True and vehicleIDToAnswer == avatar_getter.getPlayerVehicleID() and self.__commandReceivedData is not None and self.__commandReceivedData.name is not None and commandName == _CALLOUT_COMMANDS_TO_REPLY_COMMANDS[self.__commandReceivedData.name]:
                self.__executeHide(True, self.__commandReceivedData.name)
            if commandName not in _CALLOUT_COMMANDS_TO_REPLY_COMMANDS.keys():
                return
            if cmd.isReceiver():
                currentTime = BigWorld.serverTime()
                isCalloutBlocked = currentTime < self.__lastCalloutTimestamp
                hasRecentPersonalMsg = currentTime < self.__lastPersonalMsgTimestamp
                if self.__isActive is False and not isCalloutBlocked and not hasRecentPersonalMsg:
                    self.__commandReceivedData = CommandReceivedData(commandName, vehicleIDToAnswer)
                    if self.__ui:
                        self.__ui.setShowData(vehicleIDToAnswer, commandName)
                        self.__isActive = True
                        self.delayCallback(_HINT_TIMEOUT, self.__executeHide)
                    self.__lastCalloutTimestamp = currentTime + _CALLOUT_MESSAGES_BLOCK_DURATION
                    CalloutController.fireCalloutDisplayEvent(True)
                if cmd.isPrivate() and not hasRecentPersonalMsg:
                    self.__lastPersonalMsgTimestamp = currentTime + _PERSONAL_MESSAGE_MUTE_DURATION
            return

    def __handleCalloutButtonEvent(self, event):
        if not self.__isActive or self.__commandReceivedData is None:
            return
        else:
            commands = self.sessionProvider.shared.chatCommands
            if commands is None:
                return
            if self.__commandReceivedData.name in _CALLOUT_COMMANDS_TO_REPLY_COMMANDS:
                commands.handleChatCommand(_CALLOUT_COMMANDS_TO_REPLY_COMMANDS[self.__commandReceivedData.name], self.__commandReceivedData.targetIdToAnswer)
            else:
                _logger.error('Unsupported chat command name(%s) for replying to player(%d)', self.__commandReceivedData.name, self.__commandReceivedData.targetIdToAnswer)
            self.__executeHide(True, self.__commandReceivedData.name)
            return

    def __onBattleCommunicationChanged(self):
        self.__isCalloutEnabled = self.battleCommunications.showCalloutMessages
        isEnabled = self.battleCommunications.isEnabled
        if isEnabled is None or self.__isIBCEnabled == isEnabled:
            return
        else:
            if isEnabled:
                self.__activateListeners()
            else:
                self.__deactivateListeners()
            self.__isIBCEnabled = isEnabled
            return

    def __executeHide(self, wasAnswered=False, commandReceived=None):
        if self.__isActive:
            self.__isActive = False
            self.__commandReceivedData = None
            if self.__ui:
                self.__ui.setHideData(wasAnswered, commandReceived)
            CalloutController.fireCalloutDisplayEvent(False)
        return

    def __delayOpenRadialMenu(self):
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager.isModalViewsIsExists() or self.__appLoader.getApp().hasGuiControlModeConsumers(*_CONSUMERS_LOCKS):
            return
        self.__openRadialMenu()

    def __openRadialMenu(self):
        self.__radialMenuIsOpen = True
        if avatar_getter.isVehicleAlive() and not self.sessionProvider.getCtx().isPlayerObserver():
            self.__executeHide()
            gui_event_dispatcher.setRadialMenuCmd(self.__radialKeyDown, self.__radialMenuIsOpen)

    @staticmethod
    def fireCalloutDisplayEvent(isShown):
        g_eventBus.handleEvent(GameEvent(GameEvent.CALLOUT_DISPLAY_EVENT, _makeKeyCtx(key=CommandMapping.CMD_RADIAL_MENU_SHOW, isDown=isShown)), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __onCalloutHidingFinished(self):
        self.__commandReceivedData = None
        return

    def __enabledForArenaBonusType(self):
        return self.sessionProvider.arenaVisitor.getArenaBonusType() not in (ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SOLO)


def createCalloutController(setup):
    return CalloutController(setup)
