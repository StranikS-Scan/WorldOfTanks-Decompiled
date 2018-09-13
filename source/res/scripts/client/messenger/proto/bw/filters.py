# Embedded file name: scripts/client/messenger/proto/bw/filters.py
import BigWorld
from constants import CHAT_MESSAGE_MAX_LENGTH, CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE
from debug_utils import LOG_CURRENT_EXCEPTION
from external_strings_utils import normalized_unicode_trim
from helpers import html
from messenger import g_settings
from messenger.ext import g_olDictionary, g_dnDictionary
from messenger.ext.player_helpers import isCurrentPlayer
from messenger.m_constants import MESSAGE_FLOOD_COOLDOWN, MESSENGER_SCOPE
from messenger.proto.FiltersChain import FiltersChain
from messenger.proto.interfaces import IIncomingMessageFilter, IOutgoingMessageFilter
from messenger.storage import storage_getter

class ObsceneLanguageFilter(IIncomingMessageFilter):

    def __init__(self):
        super(ObsceneLanguageFilter, self).__init__()
        g_olDictionary.resetReplacementFunction()

    def filter(self, chatAction):
        text = chatAction.data
        if isCurrentPlayer(chatAction.originator):
            return text
        return g_olDictionary.searchAndReplace(text)


class ColoringObsceneLanguageFilter(IIncomingMessageFilter):

    def __init__(self):
        super(ColoringObsceneLanguageFilter, self).__init__()
        self.__currentID = None
        g_olDictionary.overrideReplacementFunction(lambda world: self.__processBadWord(world))
        return

    def __del__(self):
        if self.usersStorage is not None:
            self.usersStorage._clearBreakers()
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    def __processBadWord(self, word):
        self.usersStorage._markAsBreaker(self.__currentID, True)
        return g_settings.lobby.badWordFormat.format(word)

    def filter(self, chatAction):
        self.__currentID = chatAction.originator
        text = chatAction.data
        self.usersStorage._markAsBreaker(self.__currentID, False)
        if isCurrentPlayer(chatAction.originator):
            return text
        return g_olDictionary.searchAndReplace(text)


class SpamFilter(IIncomingMessageFilter):

    def __init__(self):
        super(SpamFilter, self).__init__()
        try:
            self._filter = BigWorld.WGSpamFilter()
            self._filter.removeSpam('')
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

            class Dummy(object):

                def removeSpam(self, text):
                    return text

            self._filter = Dummy()

    def filter(self, chatAction):
        text = chatAction.data
        if isCurrentPlayer(chatAction.originator):
            return text
        return self._filter.removeSpam(text)


class FloodFilter(IIncomingMessageFilter):

    def __init__(self):
        super(FloodFilter, self).__init__()
        self.__history = {}

    def filter(self, chatAction):
        text = chatAction.data
        userId = chatAction.originator
        if isCurrentPlayer(userId):
            return text
        else:
            userHistory = self.__history.get(userId)
            if userHistory is None:
                userHistory = self.__history[userId] = []
            currTime = BigWorld.time()
            recentCount = len(userHistory) + 1
            for msgTime, msgText in userHistory:
                if currTime - msgTime > MESSAGE_FLOOD_COOLDOWN:
                    recentCount -= 1
                elif text == msgText:
                    text = ''
                    break

            userHistory.append((currTime, text))
            if recentCount < len(userHistory):
                self.__history[userId] = userHistory[-recentCount:]
            return text


class DomainNameFilter(IIncomingMessageFilter):

    def __init__(self):
        super(DomainNameFilter, self).__init__()
        g_dnDictionary.resetReplacementFunction()

    def filter(self, chatAction):
        text = chatAction.data
        if isCurrentPlayer(chatAction.originator):
            return text
        return g_dnDictionary.searchAndReplace(text)


class HtmlEscapeFilter(IIncomingMessageFilter):

    def filter(self, chatAction):
        return html.escape(chatAction.data)


class NormalizeLobbyMessageFilter(IOutgoingMessageFilter):

    def filter(self, message):
        truncated = normalized_unicode_trim(message.strip(), CHAT_MESSAGE_MAX_LENGTH)
        return ' '.join(truncated.split())


class NormalizeBattleMessageFilter(IOutgoingMessageFilter):

    def filter(self, message):
        truncated = normalized_unicode_trim(message.strip(), CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE)
        return ' '.join(truncated.split())


class BWFiltersChain(FiltersChain):

    def __init__(self):
        inFilters = [{'name': 'htmlEscape',
          'filter': HtmlEscapeFilter(),
          'order': 0,
          'lock': True}]
        outFilters = [{'name': 'normalizeLobbyMessage',
          'filter': NormalizeLobbyMessageFilter(),
          'order': 0,
          'lock': False}]
        super(BWFiltersChain, self).__init__(inFilters, outFilters)

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def addListeners(self):
        g_settings.onUserPreferencesUpdated += self.__ms_onUserPreferencesUpdated
        self.playerCtx.onAccountAttrsChanged += self.__pc_onAccountAttrsChanged
        self.__ms_onUserPreferencesUpdated()

    def removeListeners(self):
        g_settings.onUserPreferencesUpdated -= self.__ms_onUserPreferencesUpdated
        self.playerCtx.onAccountAttrsChanged -= self.__pc_onAccountAttrsChanged

    def switch(self, scope):
        if scope is MESSENGER_SCOPE.LOBBY and not self.hasFilter('normalizeLobbyMessage'):
            self.addFilter('normalizeLobbyMessage', NormalizeLobbyMessageFilter(), removed=['normalizeBattleMessage'], order=0)
        elif scope is MESSENGER_SCOPE.BATTLE and not self.hasFilter('normalizeBattleMessage'):
            self.addFilter('normalizeBattleMessage', NormalizeBattleMessageFilter(), removed=['normalizeLobbyMessage'], order=0)

    def __ms_onUserPreferencesUpdated(self):
        if g_settings.userPrefs.enableOlFilter:
            if not self.hasFilter('enableOlFilter'):
                self.addFilter('olFilter', ObsceneLanguageFilter(), removed=['coloringOlFilter'])
        elif self.playerCtx.isChatAdmin() and not self.hasFilter('coloringOlFilter'):
            self.addFilter('coloringOlFilter', ColoringObsceneLanguageFilter(), removed=['olFilter'])
        else:
            self.removeFilter('olFilter')
        if g_settings.userPrefs.enableSpamFilter:
            self.addFilter('domainFilter', DomainNameFilter())
            self.addFilter('spamFilter', SpamFilter())
            self.addFilter('floodFilter', FloodFilter())
        else:
            self.removeFilter('domainFilter')
            self.removeFilter('spamFilter')
            self.removeFilter('floodFilter')

    def __pc_onAccountAttrsChanged(self):
        if self.playerCtx.isChatAdmin():
            if not g_settings.userPrefs.enableOlFilter and not self.hasFilter('coloringOlFilter'):
                self.addFilter('coloringOlFilter', ColoringObsceneLanguageFilter(), removed=['olFilter'])
        else:
            self.removeFilter('coloringOlFilter')
