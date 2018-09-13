# Embedded file name: scripts/client/messenger/proto/bw/search_porcessors.py
import weakref
import BigWorld
import chat_shared
from constants import USER_SEARCH_RESULTS_LIMIT, CHANNEL_SEARCH_RESULTS_LIMIT
from debug_utils import LOG_DEBUG
from external_strings_utils import isAccountNameValid
from external_strings_utils import _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH
from gui.Scaleform.locale.MESSENGER import MESSENGER
from helpers import i18n
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.bw import cooldown
from messenger.proto.interfaces import ISearchHandler, ISearchProcessor

class SearchProcessor(ISearchProcessor):

    def __init__(self):
        super(SearchProcessor, self).__init__()
        self._handlers = set()
        self._lastRequestID = None
        return

    def __del__(self):
        LOG_DEBUG('SearchProcessor deleted:', self)

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def init(self):
        pass

    def fini(self):
        self._lastRequestID = None
        self._handlers.clear()
        return

    def addHandler(self, handler):
        if isinstance(handler, ISearchHandler):
            self._handlers.add(weakref.ref(handler))
        else:
            raise ValueError, 'Handler must implement ISearchHandler'

    def removeHandler(self, handler):
        handlerRef = weakref.ref(handler)
        if handlerRef in self._handlers:
            self._handlers.remove(handlerRef)

    def find(self, token, **kwargs):
        raise NotImplementedError, 'Routine SearchProcessor.find must be implemented'

    def getChatCommand(self):
        raise NotImplementedError, 'Routine SearchProcessor.getChatCommand must be implemented'

    def getSearchResultLimit(self):
        raise NotImplementedError, 'Routine SearchProcessor.getSearchResultLimit must be implemented'

    def isInCooldown(self):
        chatCommand = self.getChatCommand()
        result = False
        message = ''
        if cooldown.isOperationInCooldownEx(chatCommand):
            result = True
            message = cooldown.getOperationInCooldownMsg(chatCommand, cooldown.getOperationCooldownPeriodEx(chatCommand))
        return (result, message)

    def _makeRequestID(self):
        return BigWorld.player().acquireRequestID()

    def _onSearchTokenComplete(self, requestID, result):
        if self._lastRequestID != requestID:
            return
        for handlerRef in self._handlers.copy():
            handler = handlerRef()
            if handler:
                handler.onSearchComplete(result)

    def _onSearchFailed(self, reason):
        for handlerRef in self._handlers.copy():
            handler = handlerRef()
            if handler:
                handler.onSearchFailed(reason)


class SearchChannelsProcessor(SearchProcessor):

    def init(self):
        super(SearchChannelsProcessor, self).init()
        self.proto.channels.onRequestChannelsComplete += self.__cm_onSearchTokenComplete
        self.proto.channels.onFindChannelsFailed += self.__cm_onSearchTokenFailed

    def fini(self):
        super(SearchChannelsProcessor, self).fini()
        self.proto.channels.onRequestChannelsComplete -= self.__cm_onSearchTokenComplete
        self.proto.channels.onFindChannelsFailed -= self.__cm_onSearchTokenFailed

    def find(self, token, **kwargs):
        result, message = self.isInCooldown()
        if result:
            self._onSearchFailed(message)
            return
        self._lastRequestID = self._makeRequestID()
        self.proto.channels.findChannels(token, requestID=self._lastRequestID)

    def getChatCommand(self):
        return chat_shared.CHAT_COMMANDS.findChatChannels.name()

    def getSearchResultLimit(self):
        return CHANNEL_SEARCH_RESULTS_LIMIT

    def __cm_onSearchTokenComplete(self, requestID, result):
        self._onSearchTokenComplete(requestID, result)

    def __cm_onSearchTokenFailed(self, requestID, actionResponse, data):
        if self._lastRequestID == requestID:
            if actionResponse == chat_shared.CHAT_RESPONSES.commandInCooldown:
                reason = cooldown.getOperationInCooldownMsg(self.getChatCommand(), data.get('cooldownPeriod', -1))
                self._onSearchFailed(reason)


class SearchUsersProcessor(SearchProcessor):

    def init(self):
        super(SearchUsersProcessor, self).init()
        self.proto.users.onFindUsersComplete += self.__um_onSearchTokenComplete
        self.proto.users.onFindUsersFailed += self.__um_onSearchTokenFailed

    def fini(self):
        super(SearchUsersProcessor, self).fini()
        self.proto.users.onFindUsersComplete -= self.__um_onSearchTokenComplete
        self.proto.users.onFindUsersFailed -= self.__um_onSearchTokenFailed

    def find(self, token, onlineMode = None):
        result, reason = self.isInCooldown()
        if result:
            self._onSearchFailed(reason)
            return
        token = token.strip()
        if not len(token):
            reason = i18n.makeString(MESSENGER.CLIENT_WARNING_EMPTYUSERSEARCHTOKEN_MESSAGE)
            self._onSearchFailed(reason)
            return
        if not isAccountNameValid(token):
            reason = i18n.makeString(MESSENGER.CLIENT_WARNING_INVALIDUSERSEARCHTOKEN_MESSAGE, _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH)
            self._onSearchFailed(reason)
            return
        self._lastRequestID = self._makeRequestID()
        self.proto.users.findUsers(token, onlineMode=onlineMode, requestID=self._lastRequestID)

    def getChatCommand(self):
        return chat_shared.CHAT_COMMANDS.findUser.name()

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
