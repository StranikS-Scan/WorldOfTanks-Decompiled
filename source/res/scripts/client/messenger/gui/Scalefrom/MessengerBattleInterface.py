# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/MessengerBattleInterface.py
# Compiled at: 2018-11-29 14:33:44
from debug_utils import LOG_DEBUG
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from messenger import isBroadcatInCooldown, BROADCAST_COOL_DOWN_MESSAGE, MESSENGER_I18N_FILE
from helpers import i18n
from messenger import MESSAGE_MAX_LENGTH, g_settings
from messenger.UsersManager import USERS_ROSTER_ACTIONS, UsersManager
from messenger.gui.interfaces import MessengerWindowInterface
from messenger.gui.Scalefrom import BTMS_COMMANDS
from messenger.gui.Scalefrom.MessengerBattlePageInterface import MessengerBattlePageInterface
import Vivox
import BattleReplay

class MessengerBattleInterface(MessengerWindowInterface):
    __userTransferUserMsgKeys = {USERS_ROSTER_ACTIONS.AddToFriend: '#{0:>s}:client/information/addToFriends/message'.format(MESSENGER_I18N_FILE),
     USERS_ROSTER_ACTIONS.AddToIgnored: '#{0:>s}:client/information/addToIgnored/message'.format(MESSENGER_I18N_FILE),
     USERS_ROSTER_ACTIONS.RemoveFromFriend: '#{0:>s}:client/information/removeFromFriends/message'.format(MESSENGER_I18N_FILE),
     USERS_ROSTER_ACTIONS.RemoveFromIgnored: '#{0:>s}:client/information/removeFromIgnored/message'.format(MESSENGER_I18N_FILE)}

    def __init__(self):
        self.__page = MessengerBattlePageInterface()
        self.__ui = None
        self.__focused = False
        return

    def start(self, parentUI):
        self.channels.exitFromAllLazyChannels()
        self.users.onUsersRosterUpdate += self.__onUsersRosterUpdate
        self.__ui = parentUI
        self.__ui.addExternalCallbacks({BTMS_COMMANDS.PopulateUI(): self.__onPopulateUI,
         BTMS_COMMANDS.CheckCooldownPeriod(): self.__onCheckCooldownPeriod,
         BTMS_COMMANDS.SendMessage(): self.__onSendChannelMessage,
         BTMS_COMMANDS.ChangeFocus(): self.__onChangeFocus,
         BTMS_COMMANDS.AddToFriends(): self.__onAddToFriends,
         BTMS_COMMANDS.RemoveFromFriends(): self.__onRemoveFromFriends,
         BTMS_COMMANDS.AddToIgnored(): self.__onAddToIgnored,
         BTMS_COMMANDS.RemoveFromIgnored(): self.__onRemoveFromIgnored,
         BTMS_COMMANDS.AddMuted(): self.__onSetMuted,
         BTMS_COMMANDS.RemoveMuted(): self.__onUnsetMuted})
        self.__flashCall(BTMS_COMMANDS.RefreshUI())
        if self.__page.teamCid != 0 and self.__page.commonCid != 0:
            self.enable()

    def destroy(self):
        self.__flashCall(BTMS_COMMANDS.ClearMessages())
        self.users.onUsersRosterUpdate -= self.__onUsersRosterUpdate
        if self.__ui:
            self.__ui.removeExternalCallbacks(BTMS_COMMANDS.PopulateUI(), BTMS_COMMANDS.CheckCooldownPeriod(), BTMS_COMMANDS.SendMessage(), BTMS_COMMANDS.ChangeFocus(), BTMS_COMMANDS.AddToFriends(), BTMS_COMMANDS.RemoveFromFriends(), BTMS_COMMANDS.AddToIgnored(), BTMS_COMMANDS.RemoveFromIgnored(), BTMS_COMMANDS.AddMuted(), BTMS_COMMANDS.RemoveMuted())
        self.__ui = None
        return

    def __onUsersRosterUpdate(self, action, user):
        messageKey = self.__userTransferUserMsgKeys.get(action)
        if messageKey is not None:
            self.showActionFailureMessage(i18n.makeString(messageKey) % user.userName)
        return

    def updateColors(self, **kwargs):
        self.__page.updateColors(**kwargs)

    def enable(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        self.users.requestUsersRoster()
        self.__flashCall(BTMS_COMMANDS.ChannelsInit())

    def show(self):
        pass

    def close(self):
        self.clear()

    def getChannelPage(self, cid):
        if cid in [self.__page.teamCid, self.__page.commonCid]:
            return self.__page
        else:
            return None

    def addChannel(self, channel):
        result = False
        if channel.isBattle:
            if channel.isBattleTeam:
                self.__page.teamCid = channel.cid
            else:
                self.__page.commonCid = channel.cid
            result = True
        if self.__page.teamCid != 0 and self.__page.commonCid != 0:
            self.enable()
        return result

    def removeChannel(self, cid):
        result = False
        if cid == self.__page.teamCid:
            self.__page.teamCid = 0
            result = True
        elif cid == self.__page.commonCid:
            self.__page.commonCid = 0
            result = True
        return result

    def addChannelMessage(self, message):
        messageText = self.__page.addMessage(message)
        self.__flashCall(BTMS_COMMANDS.RecieveMessage(), [message.channel, messageText, UsersManager.isCurrentPlayer(message.originator)])
        return messageText

    def addSystemMessage(self, message):
        pass

    def clear(self):
        self.__page.teamCid = 0
        self.__page.commonCid = 0

    def editing(self):
        return self.__focused

    def showActionFailureMessage(self, message, title=None, modal=False):
        if self.__ui:
            message = g_settings.getHtmlTemplate('battleErrorMessage') % message
            self.__flashCall(BTMS_COMMANDS.ShowActionFailureMessage(), [message])

    def __flashCall(self, funcName, args=None):
        if self.__ui:
            self.__ui.call(funcName, args)

    def __flashRespond(self, args=None):
        self.__ui.respond(args)

    def __onChangeFocus(self, _, focused):
        LOG_DEBUG('[BattleMessanger]', '__onChangeFocus = %s' % focused)
        if focused:
            responseHandler = Vivox.getResponseHandler()
            if responseHandler is not None and responseHandler.channelsMgr.currentChannel:
                responseHandler.setMicMute(muted=True)
        self.__focused = focused
        return

    def __onPopulateUI(self, *args):
        LOG_DEBUG('[BattleMessanger]', '__onPopulateUI')
        settings = g_settings.battleSettings
        parser = CommandArgsParser(self.__onPopulateUI.__name__)
        parser.parse(*args)
        parser.addArgs([MESSAGE_MAX_LENGTH,
         settings['messageLifeTime'],
         settings['messageAlphaSpeed'],
         settings['inactiveStateAlpha']])
        self.__flashRespond(parser.args())

    def __onCheckCooldownPeriod(self, *args):
        LOG_DEBUG('[BattleMessanger]', '__onCheckCooldownPeriod')
        parser = CommandArgsParser(self.__onCheckCooldownPeriod.__name__, 1, [bool])
        isCommonTeam = parser.parse(*args)
        flag = isBroadcatInCooldown()
        parser.addArgs([not flag, isCommonTeam])
        self.__flashRespond(parser.args())
        if flag:
            self.__flashCall(BTMS_COMMANDS.RecieveMessage(), [self.__page.teamCid, g_settings.getHtmlTemplate('battleErrorMessage') % BROADCAST_COOL_DOWN_MESSAGE, False])

    def __onSendChannelMessage(self, *args):
        LOG_DEBUG('[BattleMessanger]', '__onSendChannelMessage')
        parser = CommandArgsParser(self.__onSendChannelMessage.__name__, 2, [bool])
        isCommonTeam, rawMessageText = parser.parse(*args)
        self._dispatcherProxy.handleChannelMessageInput(self.__page.commonCid if isCommonTeam else self.__page.teamCid, rawMessageText)
        self.focused = False

    def __onAddToFriends(self, _, uid, userName):
        self.users.addFriend(uid, userName)

    def __onRemoveFromFriends(self, _, uid):
        self.users.removeFriend(uid)

    def __onAddToIgnored(self, _, uid, userName):
        self.users.addIgnored(uid, userName)

    def __onRemoveFromIgnored(self, _, uid):
        self.users.removeIgnored(uid)

    def __onSetMuted(self, _, uid, userName):
        self.users.setMuted(uid, userName)

    def __onUnsetMuted(self, _, uid):
        self.users.unsetMuted(uid)
