# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/battle_entry.py
import weakref
import BigWorld
import Keys
from debug_utils import LOG_ERROR
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent, ChannelManagementEvent
from messenger import g_settings
from messenger.formatters.users_messages import getUserActionReceivedMessage
from messenger.gui.Scaleform.data.message_formatters import getMessageFormatter
from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger.gui.interfaces import IGUIEntry
from messenger.gui.Scaleform import channels, FILL_COLORS
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

class BattleEntry(IGUIEntry):

    def __init__(self):
        self.__focused = False
        self.__initialized = 0
        self.__channelsCtrl = None
        self.__view = lambda : None
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

    def enable(self):
        import BattleReplay
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        else:
            view = self.__view()
            if view is not None:
                view.enableToSendMessage()
            return

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
        addListener = g_eventBus.addListener
        addListener(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, self.__handleChannelControllerInited, scope=EVENT_BUS_SCOPE.BATTLE)
        addListener(ChannelManagementEvent.REGISTER_BATTLE, self.__handleRegisterBattleView, scope=EVENT_BUS_SCOPE.BATTLE)
        addListener(ChannelManagementEvent.UNREGISTER_BATTLE, self.__handleUnregisterBattleView, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__channelsCtrl = channels.BattleControllers()
        self.__channelsCtrl.init()

    def close(self, _):
        g_messengerEvents.channels.onMessageReceived -= self.__me_onMessageReceived
        g_messengerEvents.channels.onCommandReceived -= self.__me_onCommandReceived
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        g_messengerEvents.onErrorReceived -= self.__me_onErrorReceived
        g_messengerEvents.onWarningReceived -= self.__me_onWarningReceived
        g_settings.onUserPreferencesUpdated -= self.__ms_onUserPreferencesUpdated
        g_settings.onColorsSchemesUpdated -= self.__ms_onColorsSchemesUpdated
        g_settings.resetBattleReceiverIfNeed()
        self.__initialized = 0
        self.__focused = False
        if self.__channelsCtrl is not None:
            self.__channelsCtrl.clear()
            self.__channelsCtrl = None
        removeListener = g_eventBus.removeListener
        removeListener(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, self.__handleChannelControllerInited, scope=EVENT_BUS_SCOPE.BATTLE)
        removeListener(ChannelManagementEvent.REGISTER_BATTLE, self.__handleRegisterBattleView, scope=EVENT_BUS_SCOPE.BATTLE)
        removeListener(ChannelManagementEvent.UNREGISTER_BATTLE, self.__handleUnregisterBattleView, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__view = lambda : None
        return

    def addClientMessage(self, message, isCurrentPlayer=False):
        if isCurrentPlayer:
            fillColor = FILL_COLORS.BROWN
        else:
            fillColor = FILL_COLORS.BLACK
        view = self.__view()
        if view is not None:
            view.addMessage(message, fillColor=fillColor)
        return

    def handleKey(self, event):
        key = event.key
        isFocused = self.isFocused()
        if not isFocused and BigWorld.isKeyDown(Keys.KEY_TAB):
            return False
        if event.isKeyDown() and not event.isAltDown() and key in (Keys.KEY_RETURN, Keys.KEY_NUMPADENTER):
            return self.__handleEnterPressed()
        if isFocused:
            if event.isKeyDown():
                if key == Keys.KEY_ESCAPE:
                    self.__setFocused(False)
                elif key == Keys.KEY_TAB:
                    self.__setNextReceiver()
            return event.key != Keys.KEY_SYSRQ
        return False

    def isFocused(self):
        view = self.__view()
        if view is not None:
            return view.isFocused()
        else:
            return False
            return

    def __setEnable(self):
        if self.__view() is None or not BATTLE_CHANNEL.isInitialized(self.__initialized):
            return
        else:
            import BattleReplay
            if BattleReplay.g_replayCtrl.isPlaying:
                return
            view = self.__view()
            if view is not None:
                view.enableToSendMessage()
            return

    def __setFocused(self, value):
        result = False
        view = self.__view()
        if view is not None:
            result = view.setFocused(value)
        return result

    def __setNextReceiver(self):
        result = False
        view = self.__view()
        if view is not None:
            result = view.setNextReceiver()
        return result

    def __handleEnterPressed(self):
        result = False
        view = self.__view()
        if view is not None:
            result = view.handleEnterPressed()
        return result

    def __showErrorMessage(self, message):
        formatted = g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': message})
        view = self.__view()
        if view is not None:
            view.addMessage(formatted, fillColor=FILL_COLORS.BLACK)
        return

    def __showWarningMessage(self, actionMessage):
        formatter = getMessageFormatter(actionMessage)
        formatted = formatter.getFormattedMessage()
        fillColor = formatter.getFillColor()
        view = self.__view()
        if view is not None:
            view.addMessage(formatted, fillColor=fillColor)
        return

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
        view = self.__view()
        if view is not None:
            view.invalidateUserPreferences()
        return

    def __ms_onColorsSchemesUpdated(self):
        view = self.__view()
        if view is not None:
            view.invalidateReceivers()
        return

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
            view = self.__view()
            if view is not None:
                controller.setView(view)
            self.__setEnable()
            return

    def __handleRegisterBattleView(self, event):
        ctx = event.ctx
        component = ctx.get('component')
        if component is None:
            LOG_ERROR('UI component is not defined', ctx)
            return
        else:
            ctx.clear()
            self.__view = weakref.ref(component)
            if self.__channelsCtrl is not None:
                for controller in self.__channelsCtrl.getControllersIterator():
                    controller.setView(component)

            self.__setEnable()
            return

    def __handleUnregisterBattleView(self, _):
        if self.__channelsCtrl is not None:
            for controller in self.__channelsCtrl.getControllersIterator():
                controller.removeView()

        self.__view = lambda : None
        return
