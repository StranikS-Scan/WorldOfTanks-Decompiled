# Embedded file name: scripts/client/messenger/proto/bw/search_processors.py
import chat_shared
from constants import USER_SEARCH_RESULTS_LIMIT, CHANNEL_SEARCH_RESULTS_LIMIT
from external_strings_utils import _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH
from gui.Scaleform.locale.MESSENGER import MESSENGER
from helpers import i18n
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.bw import cooldown
from messenger.proto.search_processor import SearchProcessor
from messenger.ext import checkAccountName
from messenger.proto.events import g_messengerEvents

class SearchChannelsProcessor(SearchProcessor):

    def init(self):
        super(SearchChannelsProcessor, self).init()
        channels = self.proto.channels
        channels.onRequestChannelsComplete += self.__cm_onSearchTokenComplete
        channels.onFindChannelsFailed += self.__cm_onSearchTokenFailed
        channels.onChannelExcludeFromSearch += self.__cm_onChannelExcludeFromSearch

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def fini(self):
        super(SearchChannelsProcessor, self).fini()
        channels = self.proto.channels
        channels.onRequestChannelsComplete -= self.__cm_onSearchTokenComplete
        channels.onFindChannelsFailed -= self.__cm_onSearchTokenFailed
        channels.onChannelExcludeFromSearch -= self.__cm_onChannelExcludeFromSearch

    def isInCooldown(self):
        chatCommand = self.getChatCommand()
        result = False
        message = ''
        if cooldown.isOperationInCooldownEx(chatCommand):
            result = True
            message = cooldown.getOperationInCooldownMsg(chatCommand, cooldown.getOperationCooldownPeriodEx(chatCommand))
        return (result, message)

    def find(self, token, **kwargs):
        result, message = self.isInCooldown()
        if result:
            self._onSearchFailed(message)
            return
        self._lastRequestID = self._makeRequestID()
        self.proto.channels.findChannels(token, requestID=self._lastRequestID)

    def getSearchResultLimit(self):
        return CHANNEL_SEARCH_RESULTS_LIMIT

    def __cm_onSearchTokenComplete(self, requestID, result):
        self._onSearchTokenComplete(requestID, result)

    def __cm_onSearchTokenFailed(self, requestID, actionResponse, data):
        if self._lastRequestID == requestID:
            if actionResponse == chat_shared.CHAT_RESPONSES.commandInCooldown:
                reason = cooldown.getOperationInCooldownMsg(self.getChatCommand(), data.get('cooldownPeriod', -1))
                self._onSearchFailed(reason)

    def __cm_onChannelExcludeFromSearch(self, channel):
        self._onExcludeFromSearch(channel)


class SearchUsersProcessor(SearchProcessor):

    def init(self):
        super(SearchUsersProcessor, self).init()
        g_messengerEvents.users.onFindUsersComplete += self.__um_onSearchTokenComplete
        g_messengerEvents.users.onFindUsersFailed += self.__um_onSearchTokenFailed

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def fini(self):
        super(SearchUsersProcessor, self).fini()
        g_messengerEvents.users.onFindUsersComplete -= self.__um_onSearchTokenComplete
        g_messengerEvents.users.onFindUsersFailed -= self.__um_onSearchTokenFailed

    def isInCooldown(self):
        chatCommand = self.getChatCommand()
        result = False
        message = ''
        if cooldown.isOperationInCooldownEx(chatCommand):
            result = True
            message = cooldown.getOperationInCooldownMsg(chatCommand, cooldown.getOperationCooldownPeriodEx(chatCommand))
        return (result, message)

    def find(self, token, onlineMode = None):
        result, reason = self.isInCooldown()
        if result:
            self._onSearchFailed(reason)
            return False
        isCorrect, reason = checkAccountName(token)
        if not isCorrect:
            self._onSearchFailed(reason)
            return False
        self._lastRequestID = self._makeRequestID()
        self.proto.users.findUsers(token, onlineMode=onlineMode, requestID=self._lastRequestID)
        return True

    @classmethod
    def getSearchResultLimit(self):
        return USER_SEARCH_RESULTS_LIMIT

    def __um_onSearchTokenComplete(self, requestID, result):
        self._onSearchTokenComplete(requestID, result)

    def __um_onSearchTokenFailed(self, requestID, actionResponse, data):
        if self._lastRequestID == requestID:
            if actionResponse == chat_shared.CHAT_RESPONSES.commandInCooldown:
                reason = cooldown.getOperationInCooldownMsg(self.getChatCommand(), data.get('cooldownPeriod', -1))
                self._onSearchFailed(reason)
            elif actionResponse == chat_shared.CHAT_RESPONSES.incorrectCharacter:
                reason = i18n.makeString(MESSENGER.CLIENT_WARNING_INVALIDUSERSEARCHTOKEN_MESSAGE, _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH)
                self._onSearchFailed(reason)
