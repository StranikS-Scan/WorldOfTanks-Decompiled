# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/search_interfaces.py
# Compiled at: 2011-07-29 13:15:51
import BigWorld
from constants import CHANNEL_SEARCH_RESULTS_LIMIT, USER_SEARCH_RESULTS_LIMIT
from debug_utils import LOG_DEBUG
from external_strings_utils import _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH, isAccountNameValid
from helpers import i18n
from gui import SystemMessages
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from messenger import g_settings, MESSENGER_I18N_FILE, getOperationInCooldownMsg
from messenger.gui.interfaces import DispatcherProxyHolder
import chat_shared

class SearchInterface(DispatcherProxyHolder):

    def __init__(self, commandPrefix):
        self.__movieViewHandler = None
        self.__commandPrefix = commandPrefix
        self.__refreshListCommand = '%s.RefreshList' % commandPrefix
        self.__findFailedCommand = '%s.FindFailed' % commandPrefix
        self.__searchCache = []
        self.__searchRequiestID = None
        return

    def __del__(self):
        LOG_DEBUG('Deleted: SearchInterface')

    def populateUI(self, movieViewHandler):
        self.__movieViewHandler = movieViewHandler
        self.__movieViewHandler.addExternalCallbacks({'%s.SearchToken' % self.__commandPrefix: self.onSearchToken,
         '%s.RequestItemAt' % self.__commandPrefix: self.onSearchResultRequestItemAt,
         '%s.RequestItemRange' % self.__commandPrefix: self.onSearchResultRequestItemRange,
         '%s.RequestSearchLimitLabel' % self.__commandPrefix: self.onRequestSearchLimitLabel})

    def dispossessUI(self):
        self.__movieViewHandler.removeExternalCallbacks('%s.SearchToken' % self.__commandPrefix, '%s.RequestItemAt' % self.__commandPrefix, '%s.RequestItemRange' % self.__commandPrefix, '%s.RequestSearchLimitLabel' % self.__commandPrefix)
        self.__movieViewHandler = None
        self.__searchProcessor = None
        self.__searchCache = []
        self.__searchRequiestID = None
        return

    @property
    def processor(self):
        return self.__searchProcessor

    @property
    def handler(self):
        return self.__movieViewHandler

    @property
    def prefix(self):
        return self.__commandPrefix

    @property
    def cache(self):
        return self.__searchCache

    def find(self, requestID, token):
        pass

    def parse(self, result):
        pass

    def parseFailedResponse(self, actionResponse, data):
        pass

    def _getSearchResultLimit(self):
        return None

    def refresh(self):
        self.__movieViewHandler.call(self.__refreshListCommand, [len(self.__searchCache)])

    def setErrorMessage(self, message, messageType=SystemMessages.SM_TYPE.Error):
        SystemMessages.pushMessage(message, type=messageType)
        self.__movieViewHandler.call(self.__findFailedCommand)

    def onSearchTokenFailed(self, requestID, actionResponse, data):
        if requestID == self.__searchRequiestID:
            self.parseFailedResponse(actionResponse, data)

    def onSearchTokenComplete(self, requestID, result):
        if requestID != self.__searchRequiestID:
            return
        if not len(result):
            SystemMessages.pushI18nMessage('#messenger:client/information/emptySearchResult/message', type=SystemMessages.SM_TYPE.Warning)
        result = self.parse(result)
        self.__searchCache = result
        self.__movieViewHandler.call(self.__refreshListCommand, [len(result)])

    def onSearchToken(self, *args):
        parser = CommandArgsParser(self.onSearchToken.__name__, 1, [str])
        token = parser.parse(*args)
        self.__searchRequiestID = BigWorld.player().acquireRequestID()
        self.find(self.__searchRequiestID, token)

    def onSearchResultRequestItemAt(self, *args):
        parser = CommandArgsParser(self.onSearchResultRequestItemAt.__name__, 1, [int])
        index = parser.parse(*args)
        if len(self.__searchCache) > index:
            parser.addArgs(self.__searchCache[index], [long])
        self.__movieViewHandler.respond(parser.args())

    def onSearchResultRequestItemRange(self, *args):
        parser = CommandArgsParser(self.onSearchResultRequestItemRange.__name__, 2, [int, int])
        startIndex, endIndex = parser.parse(*args)
        list = self.__searchCache
        for item in list[startIndex:endIndex + 1]:
            parser.addArgs(item, [long])

        self.__movieViewHandler.respond(parser.args())

    def onRequestSearchLimitLabel(self, *args):
        parser = CommandArgsParser(self.onRequestSearchLimitLabel.__name__, 1, [str])
        i18nKey = parser.parse(*args)
        limit = self._getSearchResultLimit()
        args = [limit] if limit is not None else []
        parser.addArg(i18n.makeString(i18nKey, *args))
        self.__movieViewHandler.respond(parser.args())
        return


class SearchChannelsInterface(SearchInterface):

    def __init__(self, prefix='Messenger.SearchChannels'):
        SearchInterface.__init__(self, prefix)

    def __del__(self):
        LOG_DEBUG('Deleted: SearchChannelsInterface')

    @property
    def processor(self):
        return self._dispatcherProxy.channels

    def populateUI(self, movieViewHandler):
        SearchInterface.populateUI(self, movieViewHandler)
        self.processor.onRequestChannelsComplete += self.onSearchTokenComplete
        self.processor.onFindChannelsFailed += self.onSearchTokenFailed
        self.handler.addExternalCallbacks({'%s.JoinToChannel' % self.prefix: self.onJoinToChannel})

    def dispossessUI(self):
        self.handler.removeExternalCallback('%s.JoinToChannel' % self.prefix)
        self.processor.onRequestChannelsComplete -= self.onSearchTokenComplete
        self.processor.onFindChannelsFailed -= self.onSearchTokenFailed
        SearchInterface.dispossessUI(self)

    def onJoinToChannel(self, *args):
        parser = CommandArgsParser(self.onJoinToChannel.__name__, 1, [int])
        index = parser.parse(*args)
        channelData = self.cache[index]
        self.processor.joinToChannel(channelData.cid, '')

    def find(self, requestID, token):
        self.processor.findChannels(token, requestID=requestID)

    def parse(self, result):
        return sorted(result, cmp=self.__comparator)

    def parseFailedResponse(self, actionResponse, data):
        if actionResponse == chat_shared.CHAT_RESPONSES.commandInCooldown:
            message = getOperationInCooldownMsg('findChatChannels', data.get('cooldownPeriod', -1))
            self.setErrorMessage(message)

    def _getSearchResultLimit(self):
        return CHANNEL_SEARCH_RESULTS_LIMIT

    def __comparator(self, channel, other):
        return cmp(channel.channelName.lower(), other.channelName.lower())


class SearchUsersInterface(SearchInterface):

    def __init__(self, prefix='Messenger.SearchUsers'):
        SearchInterface.__init__(self, prefix)
        self._onlineFlag = None
        return

    def __del__(self):
        LOG_DEBUG('Deleted: SearchUsersInterface')

    @property
    def processor(self):
        return self._dispatcherProxy.users

    def populateUI(self, movieViewHandler):
        SearchInterface.populateUI(self, movieViewHandler)
        self.processor.onUsersRosterUpdate += self.__onUsersRosterUpdate
        self.processor.onFindUsersComplete += self.onSearchTokenComplete
        self.processor.onFindUsersFailed += self.onSearchTokenFailed
        self.handler.addExternalCallbacks({'%s.AddToFriends' % self.prefix: self.onAddToFriends,
         '%s.AddToIgnored' % self.prefix: self.onAddToIgnored,
         '%s.SetOnlineFlag' % self.prefix: self.onSetOnlineFlag})

    def dispossessUI(self):
        self.handler.removeExternalCallbacks('%s.AddToFriends' % self.prefix, '%s.AddToIgnored' % self.prefix, '%s.SetOnlineFlag' % self.prefix)
        self.processor.onUsersRosterUpdate -= self.__onUsersRosterUpdate
        self.processor.onFindUsersComplete -= self.onSearchTokenComplete
        self.processor.onFindUsersFailed -= self.onSearchTokenFailed
        SearchInterface.dispossessUI(self)

    def onAddToFriends(self, *args):
        parser = CommandArgsParser(self.onAddToFriends.__name__, 1, [int])
        index = parser.parse(*args)
        userData = self.cache[index]
        self.processor.addFriend(userData[0], userData[1])

    def onAddToIgnored(self, *args):
        parser = CommandArgsParser(self.onAddToIgnored.__name__, 1, [int])
        index = parser.parse(*args)
        userData = self.cache[index]
        self.processor.addIgnored(userData[0], userData[1])

    def onSetOnlineFlag(self, *args):
        parser = CommandArgsParser(self.onSetOnlineFlag.__name__, 1)
        self._onlineFlag = parser.parse(*args)
        self.handler.respond(parser.args())

    def find(self, requestID, token):
        token = token.strip()
        if not len(token):
            message = i18n.makeString('#%s:client/warnning/emptyUserSearchToken/message' % MESSENGER_I18N_FILE)
            self.setErrorMessage(message)
            return
        if not isAccountNameValid(token):
            message = i18n.makeString('#%s:client/warnning/invalidUserSearchToken/message' % MESSENGER_I18N_FILE, _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH)
            self.setErrorMessage(message)
            return
        self.processor.findUsers(token, onlineMode=self._onlineFlag, requestID=requestID)

    def parse(self, result):
        result = sorted(result, cmp=self.__comparator)
        return [ user.list() + g_settings.getLobbyUserCS(user.roster, himself=user.himself) for user in result ]

    def parseFailedResponse(self, actionResponse, data):
        if actionResponse == chat_shared.CHAT_RESPONSES.commandInCooldown:
            message = getOperationInCooldownMsg('findUsers', data.get('cooldownPeriod', -1))
            self.setErrorMessage(message)
        elif actionResponse == chat_shared.CHAT_RESPONSES.incorrectCharacter:
            message = i18n.makeString('#%s:client/warnning/invalidUserSearchToken/message' % MESSENGER_I18N_FILE, _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH)
            self.setErrorMessage(message)

    def _getSearchResultLimit(self):
        return USER_SEARCH_RESULTS_LIMIT

    def __comparator(self, user, other):
        return cmp(user.userName.lower(), other.userName.lower())

    def __onUsersRosterUpdate(self, action, user):
        """
        Update search cache when changes user roster list
        """
        for idx, userData in enumerate(self.cache):
            if userData[0] == user.uid:
                newData = user.list()
                newData[3] = userData[3]
                self.cache[idx] = newData + g_settings.getLobbyUserCS(user.roster, himself=user.himself)
                break

        self.refresh()


class PrebattleSearchUsersInterface(SearchUsersInterface):

    def __init__(self, prefix='Training.SearchUsers'):
        SearchUsersInterface.__init__(self, prefix)

    def __del__(self):
        LOG_DEBUG('Deleted: PrebattleSearchUsersInterface')

    @property
    def processor(self):
        return self._dispatcherProxy.users

    def populateUI(self, movieViewHandler):
        SearchUsersInterface.populateUI(self, movieViewHandler)
        self.handler.addExternalCallbacks({'%s.RequestAllItems' % self.prefix: self.onRequestAllItems})

    def dispossessUI(self):
        self.handler.removeExternalCallbacks('%s.RequestAllItems' % self.prefix)
        SearchUsersInterface.dispossessUI(self)

    def parse(self, result):
        result = sorted(result, cmp=self.__comparator)
        users = []
        for user in result:
            if not user.himself:
                users.append(user.list() + g_settings.getLobbyUserCS(user.roster, himself=user.himself))

        return users

    def __comparator(self, user, other):
        return cmp(user.userName.lower(), other.userName.lower())

    def onRequestAllItems(self, *args):
        parser = CommandArgsParser(self.onRequestAllItems.__name__)
        parser.parse(*args)
        for item in self.cache:
            if not item[3]:
                continue
            parser.addArgs(item[:6], [int])

        self.handler.respond(parser.args())
