# Embedded file name: scripts/client/messenger/gui/Scaleform/BattleEntry.py
import Keys
import VOIP
from constants import CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from messenger import g_settings
from messenger.formatters.users_messages import getUserActionReceivedMessage
from messenger.gui.Scaleform.data.BattleSharedHistory import BattleSharedHistory
from messenger.gui.Scaleform.data.message_formatters import getMessageFormatter
from messenger.gui.Scaleform.view.BattleChannelView import BattleChannelView
from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE, MESSENGER_COMMAND_TYPE
from messenger.gui.interfaces import IGUIEntry
from messenger.gui.Scaleform import BTMS_COMMANDS, channels, FILL_COLORS
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

class BattleEntry(IGUIEntry):

    def __init__(self):
        self.__ui = None
        self.__focused = False
        self.__initialized = 0
        self.__channelsCtrl = None
        self.__view = None
        self.__sharedHistory = BattleSharedHistory(g_settings.battle.numberOfMessagesInHistory)
        self.__enableRecord = True
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @property
    def channelsCtrl(self):
        return self.__channelsCtrl

    def populateUI(self, parentUI):
        self.__ui = parentUI
        self.__ui.addExternalCallbacks({BTMS_COMMANDS.PopulateUI(): self.__onPopulateUI,
         BTMS_COMMANDS.ChangeFocus(): self.__onChangeFocus,
         BTMS_COMMANDS.AddToFriends(): self.__onAddToFriends,
         BTMS_COMMANDS.RemoveFromFriends(): self.__onRemoveFromFriends,
         BTMS_COMMANDS.AddToIgnored(): self.__onAddToIgnored,
         BTMS_COMMANDS.RemoveFromIgnored(): self.__onRemoveFromIgnored,
         BTMS_COMMANDS.AddMuted(): self.__onSetMuted,
         BTMS_COMMANDS.RemoveMuted(): self.__onUnsetMuted,
         BTMS_COMMANDS.upHistory(): self.__upHistory,
         BTMS_COMMANDS.downHistory(): self.__downHistory,
         BTMS_COMMANDS.GetLatestHistory(): self.__getLatestHistory,
         BTMS_COMMANDS.GetLastMessages(): self.__getLatestMessages})
        self.__flashCall(BTMS_COMMANDS.RefreshUI())
        self.__view = BattleChannelView(self.__sharedHistory)
        self.__view.populateUI(parentUI)
        if self.__channelsCtrl:
            for controller in self.__channelsCtrl.getControllersIterator():
                controller.setView(self.__view)

            self.__updateHistoryControls()
        if BATTLE_CHANNEL.isInitialized(self.__initialized):
            self.enable()

    def dispossessUI(self):
        self.__flashCall(BTMS_COMMANDS.ClearMessages())
        if self.__ui:
            self.__ui.removeExternalCallbacks(BTMS_COMMANDS.PopulateUI(), BTMS_COMMANDS.CheckCooldownPeriod(), BTMS_COMMANDS.SendMessage(), BTMS_COMMANDS.ChangeFocus(), BTMS_COMMANDS.AddToFriends(), BTMS_COMMANDS.RemoveFromFriends(), BTMS_COMMANDS.AddToIgnored(), BTMS_COMMANDS.RemoveFromIgnored(), BTMS_COMMANDS.AddMuted(), BTMS_COMMANDS.RemoveMuted(), BTMS_COMMANDS.upHistory(), BTMS_COMMANDS.downHistory(), BTMS_COMMANDS.GetLatestHistory())
        if self.__view:
            self.__view.dispossessUI()
            self.__view = None
        self.__ui = None
        return

    def enable(self):
        import BattleReplay
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        self.__flashCall(BTMS_COMMANDS.ChannelsInit())

    def enableRecord(self, enable):
        self.__enableRecord = enable

    def show(self):
        g_messengerEvents.channels.onMessageReceived += self.__me_onMessageReceived
        g_messengerEvents.channels.onCommandReceived += self.__me_onCommandReceived
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived
        g_messengerEvents.onErrorReceived += self.__me_onErrorReceived
        g_messengerEvents.onWarningReceived += self.__me_onWarningReceived
        g_settings.onUserPreferencesUpdated += self.__ms_onUserPreferencesUpdated
        g_settings.onColorsSchemesUpdated += self.__ms_onColorsSchemesUpdated
        self.__initialized = 0
        self.__focused = False
        g_eventBus.addListener(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, self.__handleChannelControllerInited, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__channelsCtrl = channels.BattleControllers()
        self.__channelsCtrl.init()

    def close(self, nextScope):
        g_messengerEvents.channels.onMessageReceived -= self.__me_onMessageReceived
        g_messengerEvents.channels.onCommandReceived -= self.__me_onCommandReceived
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        g_messengerEvents.onErrorReceived -= self.__me_onErrorReceived
        g_messengerEvents.onWarningReceived -= self.__me_onWarningReceived
        g_settings.onUserPreferencesUpdated -= self.__ms_onUserPreferencesUpdated
        g_settings.onColorsSchemesUpdated -= self.__ms_onColorsSchemesUpdated
        self.dispossessUI()
        self.__sharedHistory.clear()
        BattleChannelView.resetReceiver()
        self.__initialized = 0
        self.__focused = False
        if self.__channelsCtrl is not None:
            self.__channelsCtrl.clear()
            self.__channelsCtrl = None
        g_eventBus.removeListener(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, self.__handleChannelControllerInited, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def invoke(self, method, *args, **kwargs):
        if method in ('populateUI', 'dispossessUI'):
            try:
                getattr(self, method)(*args, **kwargs)
            except TypeError:
                LOG_CURRENT_EXCEPTION()

        else:
            LOG_ERROR('Method is not specific', method)

    def addClientMessage(self, message, isCurrentPlayer = False):
        if isCurrentPlayer:
            fillColor = FILL_COLORS.BROWN
        else:
            fillColor = FILL_COLORS.BLACK
        self.__sharedHistory.addMessage(message, fillColor=fillColor)
        self.__updateHistoryControls()
        self.__flashCall(BTMS_COMMANDS.ReceiveMessage(), [0, message, fillColor])

    def isEditing(self, event):
        return self.__focused and event.key != Keys.KEY_SYSRQ

    def isFocused(self):
        return self.__focused

    def __showErrorMessage(self, message):
        formatted = g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': message})
        self.__sharedHistory.addMessage(formatted)
        self.__flashCall(BTMS_COMMANDS.ShowActionFailureMessage(), [formatted, FILL_COLORS.BLACK])

    def __showWarningMessage(self, actionMessage):
        formatter = getMessageFormatter(actionMessage)
        formatted = formatter.getFormattedMessage()
        fillColor = formatter.getFillColor()
        self.__sharedHistory.addMessage(formatted, fillColor=fillColor)
        self.__flashCall(BTMS_COMMANDS.ShowActionFailureMessage(), [formatted, fillColor])

    def __me_onUserActionReceived(self, action, user):
        message = getUserActionReceivedMessage(action, user)
        if message:
            self.__showErrorMessage(message)

    def __me_onMessageReceived(self, message, channel):
        if channel is not None:
            controller = self.__channelsCtrl.getController(channel.getClientID())
            if controller is None or not controller.isEnabled():
                return
            import BattleReplay
            if BattleReplay.g_replayCtrl.isRecording and not self.__enableRecord:
                BattleReplay.g_replayCtrl.skipMessage()
            controller.addMessage(message)
            self.__updateHistoryControls()
        return

    def __me_onCommandReceived(self, command):
        controller = self.__channelsCtrl.getController(command.getClientID())
        if controller:
            import BattleReplay
            if BattleReplay.g_replayCtrl.isRecording and (not self.__enableRecord or command.getCommandType() == MESSENGER_COMMAND_TYPE.ADMIN):
                BattleReplay.g_replayCtrl.skipMessage()
            controller.addCommand(command)
        else:
            LOG_ERROR('Controller not found', command)

    def __me_onErrorReceived(self, error):
        self.__showErrorMessage(error.getMessage())

    def __me_onWarningReceived(self, message):
        self.__showWarningMessage(message)

    def __ms_onUserPreferencesUpdated(self):
        self.__flashCall(BTMS_COMMANDS.UserPreferencesUpdated(), [g_settings.userPrefs.storeReceiverInBattle, FILL_COLORS.BROWN, self.__getToolTipText()])
        if self.__view:
            self.__view.updateReceiversData()

    def __ms_onColorsSchemesUpdated(self):
        if self.__view:
            self.__view.updateReceiversLabels()

    def __handleChannelControllerInited(self, event):
        ctx = event.ctx
        controller = ctx.get('controller')
        if controller is None:
            LOG_ERROR('Controller is not defined', event.ctx)
            return
        elif not self.__channelsCtrl.hasController(controller):
            return
        else:
            flag = controller.getSettings().initFlag
            if flag & self.__initialized > 0:
                return
            self.__initialized |= flag
            if self.__view:
                controller.setView(self.__view)
            if self.__ui and BATTLE_CHANNEL.isInitialized(self.__initialized):
                self.enable()
            return

    def __upHistory(self, _):
        self.__sharedHistory.syncCursor(False)
        self.__sharedHistory.prev()
        self.__updateHistoryControls()
        self.__getLatestHistory()

    def __downHistory(self, *args):
        parser = CommandArgsParser(self.__downHistory.__name__, 1, [bool])
        toLastMessage, = parser.parse(*args)
        if toLastMessage == False:
            self.__sharedHistory.syncCursor(False)
            self.__sharedHistory.next()
        else:
            self.__sharedHistory.syncCursor(True)
        self.__updateHistoryControls()
        self.__getLatestHistory()

    def __updateHistoryControls(self):
        prevControl, nextControl, toLastControl = self.__sharedHistory.getNavControlsEnabled()
        self.__flashCall(BTMS_COMMANDS.EnabledHistoryControls(), [prevControl, nextControl, toLastControl])

    def __getLatestHistory(self, *args):
        toLastMessage = None
        if len(args) > 0:
            parser = CommandArgsParser(self.__getLatestHistory.__name__, 1, [bool])
            toLastMessage, = parser.parse(*args)
        if toLastMessage is not None and toLastMessage == True:
            self.__sharedHistory.syncCursor(True)
            self.__updateHistoryControls()
        historyList = self.__sharedHistory.getHistory()
        if len(historyList) == 0:
            return
        else:
            if toLastMessage is not None and toLastMessage == True:
                self.__flashCall(BTMS_COMMANDS.ClearMessages(), [])
            numberOfMessages = self.__sharedHistory.numberOfMessages()
            idx = len(historyList)
            for message, fillColor in historyList:
                numberOfMessages -= 1
                idx -= 1
                self.__flashCall(BTMS_COMMANDS.ShowHistoryMessages(), [message,
                 fillColor,
                 numberOfMessages,
                 idx])

            return

    def __getLatestMessages(self, *args):
        data = -1
        if len(args) > 0:
            parser = CommandArgsParser(self.__getLatestMessages.__name__, 1, [long])
            data, = parser.parse(*args)
        self.__sharedHistory.syncCursor(True)
        historyList = self.__sharedHistory.getHistory()
        if data > 0:
            numberOfMessages = self.__sharedHistory.numberOfMessages()
            idx = len(historyList)
            if idx >= numberOfMessages:
                numberOfMessages -= 1
                historyList = historyList[-numberOfMessages:]
        self.__flashCall(BTMS_COMMANDS.ClearMessages(), [])
        for message, fillColor in historyList:
            self.__flashCall(BTMS_COMMANDS.ShowLatestMessages(), [message, fillColor])

    def __flashCall(self, funcName, args = None):
        if self.__ui:
            self.__ui.call(funcName, args)

    def __flashRespond(self, args = None):
        self.__ui.respond(args)

    def __onChangeFocus(self, _, focused):
        self.__updateHistoryControls()
        if focused:
            responseHandler = VOIP.getVOIPManager()
            if responseHandler is not None and responseHandler.getCurrentChannel():
                responseHandler.setMicMute(muted=True)
        self.__focused = focused
        return

    def __onPopulateUI(self, *args):
        settings = g_settings.battle
        userSettings = g_settings.userPrefs
        parser = CommandArgsParser(self.__onPopulateUI.__name__)
        parser.parse(*args)
        parser.addArgs([settings.messageLifeCycle.lifeTime,
         settings.messageLifeCycle.alphaSpeed,
         settings.inactiveStateAlpha,
         CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE,
         settings.hintText,
         self.__getToolTipText(),
         userSettings.storeReceiverInBattle,
         not userSettings.disableBattleChat])
        self.__flashRespond(parser.args())
        if self.__sharedHistory.isEnabled():
            self.__sharedHistory.syncCursor(True)
        self.__flashCall(BTMS_COMMANDS.isHistoryEnabled(), [bool(self.__sharedHistory.isEnabled()),
         self.__sharedHistory.numberOfMessages(),
         g_settings.battle.alphaForLastMessages,
         g_settings.battle.recoveredLatestMessages,
         g_settings.battle.lifeTimeRecoveredMessages])
        self.__updateHistoryControls()

    def __getToolTipText(self):
        settings = g_settings.battle
        if g_settings.userPrefs.disableBattleChat:
            result = settings.chatIsLockedToolTipText
        else:
            result = settings.toolTipText
        return result

    def __onAddToFriends(self, _, uid, userName):
        self.proto.contacts.addFriend(uid, userName)

    def __onRemoveFromFriends(self, _, uid):
        self.proto.contacts.removeFriend(uid)

    def __onAddToIgnored(self, _, uid, userName):
        self.proto.contacts.addIgnored(uid, userName)

    def __onRemoveFromIgnored(self, _, uid):
        self.proto.contacts.removeIgnored(uid)

    def __onSetMuted(self, _, uid, userName):
        self.proto.contacts.setMuted(uid, userName)

    def __onUnsetMuted(self, _, uid):
        self.proto.contacts.unsetMuted(uid)
