# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/battle/messenger_view.py
import weakref
import BigWorld
from constants import CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.BattleMessengerMeta import BattleMessengerMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import ChannelManagementEvent
from messenger import g_settings
from messenger.ext import isBattleChatEnabled
from messenger.gui.Scaleform import FILL_COLORS
from messenger.gui.interfaces import IBattleChannelView
from messenger.m_constants import BATTLE_CHANNEL
_UNKNOWN_RECEIVER_LABEL = 'N/A'
_UNKNOWN_RECEIVER_ORDER = 100
_CONSUMERS_LOCK_ENTER = (BATTLE_VIEW_ALIASES.RADIAL_MENU,)

def _getToolTipText():
    settings = g_settings.battle
    if g_settings.userPrefs.disableBattleChat:
        result = settings.chatIsLockedToolTipText
    else:
        result = settings.toolTipText
    return result


def _makeSettingsVO():
    settings = g_settings.battle
    return {'lifeTime': settings.messageLifeCycle.lifeTime * 1000,
     'alphaSpeed': settings.messageLifeCycle.alphaSpeed * 1000,
     'maxLinesCount': -1,
     'inactiveStateAlpha': settings.inactiveStateAlpha / 100.0,
     'maxMessageLength': CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE,
     'hintStr': settings.hintText,
     'toolTipStr': _getToolTipText(),
     'numberOfMessagesInHistory': settings.numberOfMessagesInHistory,
     'lastMessageAlpha': settings.alphaForLastMessages / 100.0,
     'recoveredLatestMessagesAlpha': settings.recoveredLatestMessages / 100.0,
     'recoveredMessagesLifeTime': settings.lifeTimeRecoveredMessages * 1000,
     'isHistoryEnabled': settings.numberOfMessagesInHistory > 0}


def _makeReceiverVO(clientID, settings, isChatEnabled):
    """
    Makes receiver VO.
    
    :param clientID: number containing unique ID that is generated on client.
    :param settings: settings of receiver or None.
    :param isChatEnabled: is chat with given receiver enabled.
    :return: tuple(vo, reset) where are:
        vo is dictionary containing:
            clientID - client indentificator.
            labelStr - string containing i18n name of receiver.
            orderIndex - number containing order to show receiver in the view.
            isByDefault - is receiver selected (boolean).
            inputColor - string containing color of input text for given
                receiver.
            isEnabled - is receiver enabled (boolean).
    """
    if settings is not None:
        name = settings.name
        getter = g_settings.getColorScheme
        color = getter('battle/receiver').getHexStr(name)
        inputColor = getter('battle/message').getColor(name)
        orderIndex = settings.order
        isByDefault = False
        if g_settings.userPrefs.storeReceiverInBattle:
            isByDefault = name == g_settings.battle.lastReceiver
        if isChatEnabled:
            if not isBattleChatEnabled() and settings == BATTLE_CHANNEL.SQUAD:
                isByDefault = True
            recvLabelStr = settings.label % color
        else:
            recvLabelStr = makeHtmlString('html_templates:battle', 'battleChatIsLocked', {})
    else:
        recvLabelStr = _UNKNOWN_RECEIVER_LABEL
        isByDefault = False
        inputColor = ''
        orderIndex = _UNKNOWN_RECEIVER_ORDER
    vo = {'clientId': clientID,
     'labelStr': recvLabelStr,
     'orderIndex': orderIndex,
     'isByDefault': isByDefault,
     'inputColor': inputColor,
     'isEnabled': isChatEnabled}
    return vo


class BattleMessengerView(BattleMessengerMeta, IBattleChannelView):

    def __init__(self):
        super(BattleMessengerView, self).__init__()
        self.__controllers = {}
        self.__receivers = []
        self.__receiverIndex = 0
        self.__isEnabled = False
        self.__isFocused = False

    def handleEnterPressed(self):
        if self.app.isModalViewShown() or self.app.hasGuiControlModeConsumers(*_CONSUMERS_LOCK_ENTER):
            return False
        if not self.__isFocused:
            self.__findReceiverIndexByModifiers()
        self.as_enterPressedS(self.__receiverIndex)
        return True

    def setFocused(self, value):
        if not self.__isEnabled or self.__isFocused == value:
            return False
        self.__isFocused = value
        LOG_DEBUG('Sets focus to the battle chat', value)
        if self.__isFocused:
            self.as_setFocusS()
        else:
            self.as_unSetFocusS()
        return True

    def isFocused(self):
        return self.__isFocused

    def focusReceived(self):
        if self.__isEnabled:
            LOG_DEBUG('Battle chat is in focus')
            self.__setGuiMode(True)

    def focusLost(self):
        if self.__isEnabled:
            LOG_DEBUG('Battle chat is not in focus')
            self.__setGuiMode(False)

    def sendMessageToChannel(self, receiverIndex, rawMsgText):
        if receiverIndex < 0 or receiverIndex >= len(self.__receivers):
            LOG_ERROR('Index of receiver is not valid', receiverIndex)
            return False
        else:
            clientID = self.__receivers[receiverIndex][0]
            result = self.__canSendMessage(clientID)
            if result:
                controller = self.__getController(clientID)
                if not rawMsgText:
                    self.setFocused(False)
                if controller is not None:
                    controller.sendMessage(rawMsgText)
                else:
                    LOG_ERROR('Channel is not found to send message', clientID)
                return True
            return False
            return

    def enableToSendMessage(self):
        self.__isEnabled = True
        self.as_enableToSendMessageS()

    def setNextReceiver(self):
        if self.__isFocused and self.__findNextReceiverIndex():
            LOG_DEBUG('Sets receiver in the battle chat', self.__receiverIndex)
            self.as_changeReceiverS(self.__receiverIndex)
            return True
        else:
            return False

    def invalidateReceivers(self):
        self.__receivers = []
        vos = []
        for clientID, ctrlRef in self.__controllers.iteritems():
            controller = ctrlRef()
            if controller is not None and controller.getChannel().isJoined():
                receiver, isReset = self.__addReceiver(clientID, controller)
                if receiver is not None:
                    if isReset:
                        vos = []
                    vos.append(_makeReceiverVO(*receiver))

        self.as_setReceiversS(vos)
        return

    def invalidateUserPreferences(self):
        self.as_setUserPreferencesS(_getToolTipText())
        self.invalidateReceivers()

    def addController(self, controller):
        channel = controller.getChannel()
        clientID = channel.getClientID()
        self.__controllers[clientID] = weakref.ref(controller)
        receiver, isReset = self.__addReceiver(clientID, controller)
        if receiver is not None:
            self.as_setReceiverS(_makeReceiverVO(*receiver), isReset)
        return

    def removeController(self, controller):
        self.__controllers.pop(controller.getChannel().getClientID(), None)
        return

    def addMessage(self, message, fillColor=FILL_COLORS.BLACK):
        if fillColor == FILL_COLORS.BLACK:
            self.as_showBlackMessageS(message)
        elif fillColor == FILL_COLORS.RED:
            self.as_showRedMessageS(message)
        elif fillColor == FILL_COLORS.BROWN:
            self.as_showSelfMessageS(message)
        elif fillColor == FILL_COLORS.GREEN:
            self.as_showGreenMessageS(message)

    def _populate(self):
        super(BattleMessengerView, self)._populate()
        self.__receivers = []
        self.as_setupListS(_makeSettingsVO())
        self.fireEvent(ChannelManagementEvent(0, ChannelManagementEvent.REGISTER_BATTLE, {'component': self}), scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(ChannelManagementEvent.MESSAGE_FADING_ENABLED, self.__handleMessageFadingEnabled, EVENT_BUS_SCOPE.GLOBAL)

    def _dispose(self):
        self.__receivers = []
        self.fireEvent(ChannelManagementEvent(0, ChannelManagementEvent.UNREGISTER_BATTLE), scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(ChannelManagementEvent.MESSAGE_FADING_ENABLED, self.__handleMessageFadingEnabled, EVENT_BUS_SCOPE.GLOBAL)
        super(BattleMessengerView, self)._dispose()

    def __canSendMessage(self, clientID):
        result = True
        controller = self.__getController(clientID)
        if controller is None:
            return result
        else:
            result, errorMsg = controller.canSendMessage()
            if not result:
                message = g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': errorMsg})
                self.addMessage(message, fillColor=FILL_COLORS.BLACK)
            return result

    def __getController(self, clientID):
        controller = None
        if clientID in self.__controllers:
            ctrlRef = self.__controllers[clientID]
            if ctrlRef:
                controller = ctrlRef()
        return controller

    def __addReceiver(self, clientID, controller):
        isReset = False
        settings = controller.getSettings()
        isChatEnabled = controller.isEnabled()
        if isChatEnabled:
            if not isBattleChatEnabled() and settings == BATTLE_CHANNEL.SQUAD:
                self.__receivers = []
                isReset = True
        elif settings == BATTLE_CHANNEL.TEAM:
            return (None, isReset)
        receivers = g_settings.battle.receivers
        receiverName = settings.name
        if receiverName in receivers:
            guiSettings = receivers[receiverName]
        else:
            LOG_ERROR('Settings of receiver is not found', receiverName)
            guiSettings = None
        receiver = (clientID, guiSettings, isChatEnabled)
        self.__receivers.append(receiver)
        self.__receivers = sorted(self.__receivers, key=lambda item: item[1].order)
        return (receiver, isReset)

    def __setGuiMode(self, value):
        if value:
            self.__isFocused = True
            self.app.enterGuiControlMode('chat')
            self.__findReceiverIndexByModifiers()
            LOG_DEBUG('Sets receiver in the battle chat', self.__receiverIndex)
            self.as_changeReceiverS(self.__receiverIndex)
        else:
            self.__isFocused = False
            self.app.leaveGuiControlMode('chat')

    def __findReceiverIndexByModifiers(self):
        for idx, (clientID, settings, _) in enumerate(self.__receivers):
            modifiers = settings.bwModifiers
            for modifier in modifiers:
                if BigWorld.isKeyDown(modifier):
                    self.__receiverIndex = idx

        if not g_settings.userPrefs.storeReceiverInBattle:
            self.__receiverIndex = 0

    def __findNextReceiverIndex(self):
        index = self.__receiverIndex + 1
        if index >= len(self.__receivers):
            index = 0
        if index != self.__receiverIndex:
            self.__receiverIndex = index
            return True
        else:
            return False

    def __handleShowCursor(self, _):
        self.as_toggleCtrlPressFlagS(True)

    def __handleHideCursor(self, _):
        self.as_toggleCtrlPressFlagS(False)

    def __handleMessageFadingEnabled(self, event):
        self.as_setActiveS(not event.ctx['isEnabled'])
