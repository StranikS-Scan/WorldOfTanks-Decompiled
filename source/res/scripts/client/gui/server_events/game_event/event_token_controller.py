# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/event_token_controller.py
from collections import defaultdict
from helpers import dependency
from Event import Event, EventManager
from constants import HE19_SHOP_ITEM_TOKEN, HE19_MONEY_TOKEN_ID, HE19_SHOP_PACK_PREFIX
from account_helpers.AccountSettings import AccountSettings, HALLOWEEN_NOTES_SEEN
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.game_control import IEventTokenController, ITokensController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
HALLOWEEN_TOKEN_PREFIX = 'he19l:'

class TokensController(ITokensController):

    def __init__(self):
        self.__handlers = defaultdict(set)

    def init(self):
        super(TokensController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate})

    def fini(self):
        self.__handlers.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TokensController, self).fini()

    def addTokensListener(self, token, handler):
        self.__handlers[token].add(handler)

    def removeTokensListener(self, token, handler):
        if handler in self.__handlers[token]:
            self.__handlers[token].discard(handler)

    def __handleTokensUpdate(self, tokens):
        handled = []
        for token in (t for t in tokens if t.startswith((t,))):
            for handler in (h for h in self.__handlers[token] if h is not None):
                handled.append((token, handler))
                handler()

        for token, handler in handled:
            self.removeTokensListener(token, handler)


class EventTokenController(IEventTokenController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__eventsManager = EventManager()
        self.onNotesUpdated = Event(self.__eventsManager)
        self.onShopItemUpdated = Event(self.__eventsManager)
        self.onEventMoneyUpdated = Event(self.__eventsManager)

    def init(self):
        super(EventTokenController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(EventTokenController, self).fini()

    def getNewNotesCount(self):
        readTokens = AccountSettings.getSettings(HALLOWEEN_NOTES_SEEN)
        tokens = self.__itemsCache.items.tokens.getTokens()
        tokensReceived = 0
        for token in tokens.iterkeys():
            if token.startswith(HALLOWEEN_TOKEN_PREFIX):
                tokensReceived += 1

        return tokensReceived - len(readTokens) if tokensReceived > len(readTokens) else 0

    def getReadNotes(self):
        return AccountSettings.getSettings(HALLOWEEN_NOTES_SEEN)

    def markNoteRead(self, note):
        readTokens = AccountSettings.getSettings(HALLOWEEN_NOTES_SEEN)
        if readTokens:
            if note not in readTokens:
                readTokens.append(note)
        else:
            readTokens = [note]
        AccountSettings.setSettings(HALLOWEEN_NOTES_SEEN, readTokens)
        self.onNotesUpdated()

    def __onTokensUpdate(self, diff):
        for token in diff.iterkeys():
            if token.startswith(HALLOWEEN_TOKEN_PREFIX):
                self.onNotesUpdated()
            if token.startswith(HE19_SHOP_ITEM_TOKEN) or token.startswith(HE19_SHOP_PACK_PREFIX):
                self.onShopItemUpdated()
            if token.startswith(HE19_MONEY_TOKEN_ID):
                self.onEventMoneyUpdated()
