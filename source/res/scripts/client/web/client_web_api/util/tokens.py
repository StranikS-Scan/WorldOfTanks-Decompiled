# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/util/tokens.py
from web.client_web_api.api import C2WHandler, c2w
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class TokenListUpdateHandler(C2WHandler):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args):
        super(TokenListUpdateHandler, self).__init__(*args)
        self.__tokens = {}

    def init(self):
        super(TokenListUpdateHandler, self).init()
        for token, tokenData in self.__itemsCache.items.tokens.getTokens().iteritems():
            self.__tokens[token] = tokenData[1]

        self.__itemsCache.onSyncCompleted += self.__onItemsUpdate

    def fini(self):
        self.__tokens.clear()
        self.__itemsCache.onSyncCompleted -= self.__onItemsUpdate
        super(TokenListUpdateHandler, self).fini()

    def __onItemsUpdate(self, *_):
        diff = {}
        tokenItems = self.__itemsCache.items.tokens.getTokens()
        for token, count in self.__tokens.iteritems():
            if token not in tokenItems and count > 0:
                self.__tokens[token] = 0
                diff[token] = 0

        for token, tokenData in tokenItems.iteritems():
            if self.__tokens.get(token) != tokenData[1]:
                self.__tokens[token] = tokenData[1]
                diff[token] = tokenData[1]

        if diff:
            self.__sendTokenListUpdate(diff)

    @c2w(name='token_list_update')
    def __sendTokenListUpdate(self, diff):
        return diff
