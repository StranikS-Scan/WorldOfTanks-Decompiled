# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/battle/messenger_view.py
import weakref
import BigWorld
from helpers import dependency
from helpers import i18n
import BattleReplay
from constants import CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_UNEXPECTED
from gui import makeHtmlString
from gui.shared.utils import getAvatarDatabaseID
from gui.Scaleform.daapi.view.meta.BattleMessengerMeta import BattleMessengerMeta
from gui.Scaleform.genConsts.BATTLE_MESSAGES_CONSTS import BATTLE_MESSAGES_CONSTS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.battle_control.arena_info.interfaces import IContactsAndPersonalInvitationsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import EVENT_BUS_SCOPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from messenger import g_settings
from messenger.ext import isBattleChatEnabled
from messenger.gui.Scaleform import FILL_COLORS
from messenger.gui.interfaces import IBattleChannelView
from messenger.m_constants import BATTLE_CHANNEL, CLIENT_ACTION_ID, PROTO_TYPE
from gui.shared.formatters import text_styles
from gui.shared.events import ChannelManagementEvent
from gui.shared.utils.functions import makeTooltip
from gui.shared.events import CoolDownEvent
from gui.shared.view_helpers import CooldownHelper
from skeletons.gui.battle_session import IBattleSessionProvider
from ReplayEvents import g_replayEvents
_UNKNOWN_RECEIVER_LABEL = 'N/A'
_UNKNOWN_RECEIVER_ORDER = 100
_CONSUMERS_LOCK_ENTER = (BATTLE_VIEW_ALIASES.RADIAL_MENU,)

def _getToolTipText(arenaVisitor):
    settings = g_settings.battle
    if arenaVisitor is not None:
        if arenaVisitor.gui.isTrainingBattle():
            result = settings.toolTipText
        elif arenaVisitor.gui.isRandomBattle() and g_settings.userPrefs.disableBattleChat:
            result = settings.chatIsLockedToolTipText
        else:
            result = settings.toolTipTextWithMuteInfo
    else:
        result = settings.toolTipText
        LOG_ERROR('Can not get tooltip text for Chat, arenaVisitor is not defined.')
    return result


def _makeSettingsVO(arenaVisitor):
    settings = g_settings.battle
    return {'lifeTime': settings.messageLifeCycle.lifeTime * 1000,
     'alphaSpeed': settings.messageLifeCycle.alphaSpeed * 1000,
     'maxLinesCount': -1,
     'inactiveStateAlpha': settings.inactiveStateAlpha / 100.0,
     'maxMessageLength': CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE,
     'hintStr': settings.hintText,
     'toolTipStr': _getToolTipText(arenaVisitor),
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
            if not isBattleChatEnabled() and settings.name == BATTLE_CHANNEL.SQUAD.name:
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


def _isSet(number, mask):
    return number & mask > 0


class BattleMessengerView(BattleMessengerMeta, IBattleChannelView, IContactsAndPersonalInvitationsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleMessengerView, self).__init__()
        self.__controllers = {}
        self.__receivers = []
        self.__receiverIndex = 0
        self.__isEnabled = False
        self.__isFocused = False
        self._battleCtx = None
        self._arenaVisitor = None
        self._accDbID = 0
        self._toxicPanelMsgID = 0
        self._addedMsgIDs = set()
        self._ignoreActionCooldown = CooldownHelper((CLIENT_ACTION_ID.ADD_IGNORED, CLIENT_ACTION_ID.REMOVE_IGNORED), self._onIgnoreActionCooldownHandle, CoolDownEvent.XMPP)
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def protoMigration(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def protoBwChat2(self):
        return None

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def startControl(self, battleCtx, arenaVisitor):
        """Starts to controlling data of arena.
        
        :param battleCtx: proxy to battle context.
        :param arenaVisitor: proxy to arena visitor.
        """
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        return

    def getToxicStatus(self, accountDbID):
        """
        Invoked by the view at runtime to get VO of buttons panel.
        
        :param accountDbID: Message ID that corresponds to player database ID.
        :return: dict
        """
        vo = None
        accountDbID = long(accountDbID)
        if 0 < accountDbID != self._accDbID:
            vo = self.__buildToxicStateVO(accountDbID)
        if vo is not None:
            self._toxicPanelMsgID = accountDbID
        return vo

    def updateToxicStatus(self, accountDbID):
        self.as_updateToxicPanelS(accountDbID, self.__buildToxicStateVO(accountDbID))

    def onToxicButtonClicked(self, accountDbID, actionID):
        """
        Callback on user's action. Note that the same callback is invoked for all 'toxic' buttons.
        To determine which button is pressed, action ID is used. Action ID corresponds to the
        following constants from BATTLE_MESSAGES_CONSTS enum.
        
        :param accountDbID: Message ID that corresponds to player database ID.
        :param actionID: Action ID.
        """
        accDbID = long(accountDbID)
        if accDbID > 0:
            needUpdateUI = True
            if actionID == BATTLE_MESSAGES_CONSTS.ADD_IN_BLACKLIST:
                if not self._ignoreActionCooldown.isInCooldown():
                    self.protoMigration.contacts.addTmpIgnored(accDbID, self._battleCtx.getPlayerName(accID=accDbID))
            elif actionID == BATTLE_MESSAGES_CONSTS.REMOVE_FROM_BLACKLIST:
                if not self._ignoreActionCooldown.isInCooldown():
                    self.protoMigration.contacts.removeTmpIgnored(accDbID)
            else:
                needUpdateUI = False
            if needUpdateUI:
                self._invalidateToxicPanel(accDbID)

    def onToxicPanelClosed(self, messageID):
        """
        Callback on toxic panel close event.
        
        :param messageID: Message ID that corresponds to player database ID.
        """
        if 0 < self._toxicPanelMsgID == messageID:
            self._toxicPanelMsgID = 0

    def invalidateUsersTags(self):
        """
        New list of chat rosters has been received.
        """
        self._invalidateToxicPanel(self._toxicPanelMsgID)
        for msgID in self._addedMsgIDs:
            self._invalidatePlayerMessages(msgID)

    def invalidateUserTags(self, user):
        """
        Contact's chat roster has been changed.
        
        :param user: instance of UserEntity.
        """
        accDbID = user.getID()
        self._invalidatePlayerMessages(accDbID)
        self._invalidateToxicPanel(accDbID)

    def invalidateInvitationsStatuses(self, vos, arenaDP):
        """
        An invitation has been received.
        :param vos: invitations represented by list of VehicleArenaInfoVO objects.
        :param arenaDP: Reference to ArenaDataProvider
        """
        if self._toxicPanelMsgID > 0:
            for vInfo in vos:
                if vInfo.player.accountDBID == self._toxicPanelMsgID:
                    self._invalidateToxicPanel(self._toxicPanelMsgID)
                    break

    def handleEnterPressed(self):
        if not self.__isEnabled:
            return False
        if self.app.isModalViewShown() or self.app.hasGuiControlModeConsumers(*_CONSUMERS_LOCK_ENTER):
            return False
        if not self.__isFocused:
            self.__findReceiverIndexByModifiers()
        self.as_enterPressedS(self.__receiverIndex)
        return True

    def handleCTRLPressed(self, _, isDown):
        """
        Handler of Ctrl button press event.
        
        :param _: True if the event associated with the left Ctrl btn, False - if the right Ctrl.
        :param isDown: True if the Ctrl btn is down, False if it is up.
        """
        if self.app.isModalViewShown() or self.app.hasGuiControlModeConsumers(*_CONSUMERS_LOCK_ENTER):
            return False
        self.as_toggleCtrlPressFlagS(isDown)
        return True

    def setFocused(self, value):
        if self.__isFocused == value:
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
        LOG_DEBUG('Battle chat is in focus')
        self.__setGuiMode(True)
        self.protoBwChat2.voipController.setMicrophoneMute(True)

    def focusLost(self):
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
            g_settings.battle.lastReceiver = self.__receivers[self.__receiverIndex][1].name
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
        if self.__invalidateReceiverIndex():
            self.as_changeReceiverS(self.__receiverIndex)
        return

    def invalidateUserPreferences(self):
        self.as_setUserPreferencesS(_getToolTipText(self._arenaVisitor))
        self.invalidateReceivers()

    def addController(self, controller):
        channel = controller.getChannel()
        clientID = channel.getClientID()
        self.__controllers[clientID] = weakref.ref(controller)
        receiver, isReset = self.__addReceiver(clientID, controller)
        if receiver is not None:
            self.as_setReceiverS(_makeReceiverVO(*receiver), isReset)
        self.__restoreLastReceiverInBattle()
        if self.__invalidateReceiverIndex():
            self.as_changeReceiverS(self.__receiverIndex)
        return

    def removeController(self, controller):
        self.__controllers.pop(controller.getChannel().getClientID(), None)
        return

    def addMessage(self, message, fillColor=FILL_COLORS.BLACK, accountDBID=0):
        if self.__isInTimeWarp:
            return
        if accountDBID == self._accDbID:
            accountDBID = 0
        if fillColor == FILL_COLORS.BLACK:
            self.as_showBlackMessageS(message, accountDBID)
        elif fillColor == FILL_COLORS.RED:
            self.as_showRedMessageS(message, accountDBID)
        elif fillColor == FILL_COLORS.BROWN:
            self.as_showSelfMessageS(message, accountDBID)
        elif fillColor == FILL_COLORS.GREEN:
            self.as_showGreenMessageS(message, accountDBID)
        else:
            LOG_UNEXPECTED('Unexpected fill color: ', fillColor)
        if accountDBID > 0:
            self._addedMsgIDs.add(accountDBID)

    def isToxicPanelAvailable(self):
        """
        Returns True if the toxic panel is available, otherwise returns false.
        """
        return not BattleReplay.g_replayCtrl.isPlaying and self._arenaVisitor is not None and not self._arenaVisitor.gui.isTrainingBattle()

    def _populate(self):
        super(BattleMessengerView, self)._populate()
        self._accDbID = getAvatarDatabaseID()
        self.__isInTimeWarp = BattleReplay.g_replayCtrl.isTimeWarpInProgress
        self.__receivers = []
        self.fireEvent(ChannelManagementEvent(0, ChannelManagementEvent.REGISTER_BATTLE, {'component': self}), scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(ChannelManagementEvent.MESSAGE_FADING_ENABLED, self.__handleMessageFadingEnabled, EVENT_BUS_SCOPE.GLOBAL)
        self.__restoreLastReceiverInBattle()
        self.sessionProvider.addArenaCtrl(self)
        self.as_setupListS(_makeSettingsVO(self._arenaVisitor))
        self._ignoreActionCooldown.start()
        if self.isToxicPanelAvailable():
            self.as_enableToxicPanelS()
        if self.__invalidateReceiverIndex():
            self.as_changeReceiverS(self.__receiverIndex)
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinished

    def __onReplayTimeWarpFinished(self):
        self.__isInTimeWarp = False

    def __onReplayTimeWarpStart(self):
        self.__isInTimeWarp = True

    def _dispose(self):
        self.__receivers = []
        self._ignoreActionCooldown.stop()
        self._ignoreActionCooldown = None
        self.fireEvent(ChannelManagementEvent(0, ChannelManagementEvent.UNREGISTER_BATTLE), scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(ChannelManagementEvent.MESSAGE_FADING_ENABLED, self.__handleMessageFadingEnabled, EVENT_BUS_SCOPE.GLOBAL)
        self.sessionProvider.removeArenaCtrl(self)
        g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinished
        super(BattleMessengerView, self)._dispose()
        return

    def _invalidateToxicPanel(self, msgID):
        """
        Updates toxic panel if it is visible for the given message.
        
        :param msgID: Message ID that corresponds to player database ID.
        """
        if 0 < self._toxicPanelMsgID == msgID:
            self.updateToxicStatus(msgID)

    def _invalidatePlayerMessages(self, accountDbID):
        if accountDbID > 0:
            contact = self.usersStorage.getUser(accountDbID)
            if contact is not None and contact.isIgnored():
                pInfo = self._battleCtx.getPlayerFullNameParts(accID=accountDbID)
                template = i18n.makeString(MESSENGER.CHAT_TOXICMESSAGES_BLOCKEDMESSAGE, playerName=pInfo.playerName)
                self.as_updateMessagesS(accountDbID, text_styles.main(template))
            else:
                self.as_restoreMessagesS(accountDbID)
        return

    def _onIgnoreActionCooldownHandle(self, isInCooldown):
        self._invalidateToxicPanel(self._toxicPanelMsgID)

    def __buildToxicStateVO(self, accountDbID):
        """
        Builds vo related to the toxic panel.
        
        :param accountDbID: long representing account's database ID
        :return: dict
        """
        contact = self.usersStorage.getUser(accountDbID)
        return {'messageID': accountDbID,
         'vehicleID': self._battleCtx.getVehIDByAccDBID(accountDbID),
         'blackList': self.__buildBlackListVO(contact)}

    def __buildBlackListVO(self, contact):
        """
        Builds vo related to the Black List button.
        
        :param contact: an instance of UserEntity
        :return: dict
        """
        isEnabled = not self._ignoreActionCooldown.isInCooldown()
        if contact:
            if contact.isTemporaryIgnored():
                status = BATTLE_MESSAGES_CONSTS.REMOVE_FROM_BLACKLIST
                header = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_REMOVE_FROM_BLACKLIST_HEADER
                body = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_REMOVE_FROM_BLACKLIST_BODY
            elif contact.isIgnored():
                status = BATTLE_MESSAGES_CONSTS.ADD_IN_BLACKLIST
                header = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_CANT_ADD_IN_BLACKLIST_HEADER
                body = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_CANT_ADD_IN_BLACKLIST_BODY
                isEnabled = False
            else:
                status = BATTLE_MESSAGES_CONSTS.ADD_IN_BLACKLIST
                header = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_ADD_IN_BLACKLIST_HEADER
                body = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_ADD_IN_BLACKLIST_BODY
        else:
            status = BATTLE_MESSAGES_CONSTS.ADD_IN_BLACKLIST
            header = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_ADD_IN_BLACKLIST_HEADER
            body = INGAME_GUI.BATTLEMESSENGER_TOXIC_BLACKLIST_ADD_IN_BLACKLIST_BODY
        return {'status': status,
         'tooltip': makeTooltip(header=header, body=body),
         'enabled': isEnabled}

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
            if not isBattleChatEnabled() and settings.name == BATTLE_CHANNEL.SQUAD.name:
                self.__receivers = []
                self.__receiverIndex = 0
                isReset = True
        elif settings == BATTLE_CHANNEL.COMMON:
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

    def __restoreLastReceiverInBattle(self):
        """ WOTD-71200 Restore last receiver in battle
        """
        if g_settings.userPrefs.storeReceiverInBattle:
            for idx, receiver in enumerate(self.__receivers):
                if g_settings.battle.lastReceiver == receiver[1].name:
                    if self.__isReceiverAvailable(idx):
                        self.__receiverIndex = idx
                    break

    def __findReceiverIndexByModifiers(self):
        for idx, (clientID, settings, _) in enumerate(self.__receivers):
            modifiers = settings.bwModifiers
            for modifier in modifiers:
                if BigWorld.isKeyDown(modifier):
                    if self.__isReceiverAvailable(idx):
                        self.__receiverIndex = idx

        if not g_settings.userPrefs.storeReceiverInBattle:
            self.__receiverIndex = 0
        self.__invalidateReceiverIndex()

    def __invalidateReceiverIndex(self):
        """
        Try to find an available receiver if the current one is not available and update
        current receiver index.
        
        :return: True if current receiver index has been changed; otherwise - False.
        """
        return self.__findNextReceiverIndex() if not self.__isReceiverAvailable(self.__receiverIndex) else False

    def __findNextReceiverIndex(self):
        receiversCount = len(self.__receivers)
        if receiversCount > 0:
            leftReceiversCount = receiversCount - 1
        else:
            leftReceiversCount = 0
        index = self.__receiverIndex
        while leftReceiversCount:
            leftReceiversCount -= 1
            index += 1
            if index >= receiversCount:
                index = 0
            if self.__isReceiverAvailable(index):
                self.__receiverIndex = index
                return True

        return False

    def __isReceiverAvailable(self, index):
        if index < len(self.__receivers):
            _, _, isChatEnabled = self.__receivers[index]
            return isChatEnabled
        return False

    def __handleMessageFadingEnabled(self, event):
        self.as_setActiveS(not event.ctx['isEnabled'])
