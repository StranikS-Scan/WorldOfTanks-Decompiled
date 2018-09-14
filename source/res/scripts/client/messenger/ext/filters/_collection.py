# Embedded file name: scripts/client/messenger/ext/filters/_collection.py
import re
import sre_compile
import pickle
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from external_strings_utils import normalized_unicode_trim
from gui import GUI_SETTINGS
from gui.shared.utils import functions
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.formatters import icons
from helpers import html
from messenger import g_settings
from messenger.ext import g_olDictionary, g_dnDictionary
from messenger.ext.filters._chain import IIncomingMessageFilter
from messenger.ext.filters._chain import IOutgoingMessageFilter
from messenger.ext.player_helpers import isCurrentPlayer
from messenger.m_constants import MESSAGE_FLOOD_COOLDOWN
from messenger.storage import storage_getter

class ObsceneLanguageFilter(IIncomingMessageFilter):

    def __init__(self):
        super(ObsceneLanguageFilter, self).__init__()
        g_olDictionary.resetReplacementFunction()

    def filter(self, senderID, text):
        if isCurrentPlayer(senderID):
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

    def filter(self, senderID, text):
        self.__currentID = senderID
        self.usersStorage._markAsBreaker(self.__currentID, False)
        if isCurrentPlayer(senderID):
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

    def filter(self, senderID, text):
        if isCurrentPlayer(senderID):
            return text
        return self._filter.removeSpam(text)


class FloodFilter(IIncomingMessageFilter):

    def __init__(self):
        super(FloodFilter, self).__init__()
        self.__history = {}

    def filter(self, senderID, text):
        if isCurrentPlayer(senderID):
            return text
        else:
            userHistory = self.__history.get(senderID)
            if userHistory is None:
                userHistory = self.__history[senderID] = []
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
                self.__history[senderID] = userHistory[-recentCount:]
            return text


class DomainNameFilter(IIncomingMessageFilter):

    def __init__(self):
        super(DomainNameFilter, self).__init__()
        g_dnDictionary.resetReplacementFunction()

    def filter(self, senderID, text):
        if isCurrentPlayer(senderID):
            return text
        return g_dnDictionary.searchAndReplace(text)


class HtmlEscapeFilter(IIncomingMessageFilter):

    def filter(self, senderID, text):
        return html.escape(text)


class PostBattleLinksFilter(IIncomingMessageFilter):

    def __init__(self):
        try:
            self.__pattern = re.compile('(%s)/(.*)/(.*)' % self.__getUrl(), re.M | re.S | re.U | re.I)
        except sre_compile.error:
            LOG_CURRENT_EXCEPTION()

    def filter(self, senderID, text):
        return self.__pattern.sub(self.__reSubHandler, text)

    @classmethod
    def __reSubHandler(cls, match):
        return match.group()

    @classmethod
    def __getUrl(cls):
        return re.escape(GUI_SETTINGS.postBattleExchange.url)


class NormalizeMessageFilter(IOutgoingMessageFilter):

    def filter(self, message, limits):
        truncated = normalized_unicode_trim(message.strip(), limits.getMessageMaxLength())
        return ' '.join(truncated.split())
