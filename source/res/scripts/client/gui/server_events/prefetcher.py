# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/prefetcher.py
import json
import itertools
import weakref
import typing
from collections import namedtuple
import BigWorld
import ResMgr
from wg_async import wg_async, wg_await, await_callback, AsyncScope, AsyncSemaphore
from constants import DailyQuestDecorationMap, EVENT_TYPE
from debug_utils import LOG_WARNING
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.formatters import TOKEN_SIZES, DECORATION_SIZES, parseComplexToken
from gui.server_events.events_helpers import isMarathon, isDailyQuest, isPremium
from gui.shared.utils import mapTextureToTheMemory, getImageSize
from helpers import getClientLanguage, dependency
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
_DEFAULT_TOKENS_STYLES = [ title.split('/')[-1] for title in QUESTS.TOKEN_DEFAULT_ENUM ]
_DEFAULT_DECORATIONS = [ title.split('_')[-1].replace('.png', '') for title in RES_ICONS.MAPS_ICONS_MISSIONS_DECORATIONS_DECORATION_ENUM ]

def _getTokensFromAccountReqs(quest):
    return (parseComplexToken(t.getID()) for t in quest.accountReqs.getTokens())


def _getTokensFromBonuses(quest):
    return (parseComplexToken(t) for t in itertools.chain.from_iterable((b.getValue().keys() for b in quest.getBonuses('tokens'))))


class SubRequester(object):

    def __init__(self, eventsCache, semaphore):
        self._eventsCache = eventsCache
        self._semaphore = semaphore
        self._storage = {}

    def pickup(self, ticket):
        return self._storage.get(ticket)

    def ask(self, filecache, fileserver):
        tickets = self._tickets()
        for ticket in tickets:
            url = self._urlGetter(fileserver)(*ticket)
            headers = self._headers()
            if url and ticket not in self:
                filecache.get(url, headers=headers, callback=lambda name, content: None)

    def demand(self, filecache, fileserver):
        demanded = []
        tickets = self._tickets()
        for ticket in tickets:
            url = self._urlGetter(fileserver)(*ticket)
            headers = self._headers()
            if url and ticket not in self:
                demanded.append(url)
                self._run(url, headers, ticket, filecache)

        return demanded

    @wg_async
    def _run(self, url, headers, ticket, filecache):
        name, content = yield await_callback(filecache.get)(url, headers=headers)
        try:
            try:
                if content:
                    self._handler(ticket, content)
            except Exception:
                LOG_WARNING('Error during processing', name)

        finally:
            self._semaphore.release()

    def _handler(self, ticket, content):
        pass

    def _tickets(self):
        return []

    @staticmethod
    def _urlGetter(fileserver):
        raise NotImplementedError

    @staticmethod
    def _headers():
        return {}

    def __contains__(self, ticket):
        return ticket in self._storage


class TokenImagesSubRequester(SubRequester):

    def pickup(self, styleID, size):
        ticket = (styleID, size)
        content = self._storage.get(ticket)
        if styleID in _DEFAULT_TOKENS_STYLES:
            return RES_ICONS.getTokenImage(size, styleID)
        return 'img://{}'.format(mapTextureToTheMemory(content)) if content else RES_ICONS.getTokenUndefinedImage(size)

    def _handler(self, ticket, content):
        _, expectedSize = ticket
        actualSize = '{}x{}'.format(*getImageSize(content))
        if expectedSize != actualSize:
            raise SoftException('Downloaded image has invalid size')
        self._storage[ticket] = content

    def _tickets(self):
        tickets = []
        for quest in self._eventsCache.getQuests().itervalues():
            if quest.getType() not in (EVENT_TYPE.TOKEN_QUEST, EVENT_TYPE.BATTLE_QUEST, EVENT_TYPE.PERSONAL_QUEST):
                continue
            for token in itertools.chain(_getTokensFromAccountReqs(quest), _getTokensFromBonuses(quest)):
                styleID = token.styleID
                if token.isDisplayable and styleID not in _DEFAULT_TOKENS_STYLES and styleID not in tickets:
                    tickets.append(styleID)

        return itertools.product(tickets, TOKEN_SIZES.ALL())

    @staticmethod
    def _urlGetter(fileserver):
        return fileserver.getMissionsTokenImageUrl


_TokenInfoData = namedtuple('_TokenInfoData', ['title', 'description'])

class TokenInfoSubRequester(SubRequester):

    def pickup(self, styleID):
        ticket = (styleID,)
        storageData = self._storage.get(ticket, None)
        if storageData is not None:
            return storageData
        else:
            return _TokenInfoData(title=backport.text(R.strings.quests.token.default.dyn(styleID)()), description=None) if styleID in _DEFAULT_TOKENS_STYLES else _TokenInfoData(title=backport.text(R.strings.quests.token.undefined()), description=None)

    def _handler(self, ticket, content):
        section = ResMgr.DataSection()
        section.createSectionFromString(content)
        tokens = section['root/tokens']
        for item in tokens.values():
            tokenID = item['id'].asString
            string = item['title'].asString
            description = item.readString('description') if item.has_key('description') else None
            ticket = (tokenID,)
            self._storage[ticket] = _TokenInfoData(title=string, description=description)

        return

    def _tickets(self):
        for quest in self._eventsCache.getQuests().itervalues():
            if quest.getType() not in (EVENT_TYPE.TOKEN_QUEST, EVENT_TYPE.BATTLE_QUEST, EVENT_TYPE.PERSONAL_QUEST):
                continue
            for token in itertools.chain(_getTokensFromAccountReqs(quest), _getTokensFromBonuses(quest)):
                if token.isDisplayable:
                    return [(getClientLanguage(),)]

        return []

    @staticmethod
    def _urlGetter(fileserver):
        return fileserver.getMissionsTokenDescrsUrl

    def __contains__(self, _):
        return False


class DecorationRequester(SubRequester):

    def pickup(self, decorationID, size):
        ticket = (decorationID, size)
        if size == DECORATION_SIZES.BONUS:
            if str(decorationID) in _DEFAULT_DECORATIONS:
                return RES_ICONS.getQuestDecoration(decorationID)
            default = RES_ICONS.MAPS_ICONS_MISSIONS_DECORATIONS_UNDEFINED
        else:
            if size == DECORATION_SIZES.DAILY:
                return DailyQuestDecorationMap.get(decorationID, '')
            default = ''
        content = self._storage.get(ticket)
        return 'img://{}'.format(mapTextureToTheMemory(content)) if content else default

    def _handler(self, ticket, content):
        _, expectedSize = ticket
        actualSize = '{}x{}'.format(*getImageSize(content))
        if actualSize != expectedSize:
            raise SoftException('Downloaded image has invalid size')
        self._storage[ticket] = content

    def _tickets(self):
        decorations = []
        for quest in self._eventsCache.getGroups().itervalues():
            decorationID = quest.getIconID()
            if decorationID:
                decorations.append((decorationID, DECORATION_SIZES.MARATHON))

        for quest in self._eventsCache.getQuests().itervalues():
            decorationID = quest.getIconID()
            if not decorationID:
                continue
            if isDailyQuest(quest.getID()) or isPremium(quest.getID()):
                continue
            if isMarathon(quest.getID()):
                if str(decorationID) not in _DEFAULT_DECORATIONS:
                    decorations.append((decorationID, DECORATION_SIZES.BONUS))
            if quest.getType() not in EVENT_TYPE.SHARED_QUESTS:
                for size in (DECORATION_SIZES.CARDS, DECORATION_SIZES.DETAILS):
                    decorations.append((decorationID, size))

        for action in self._eventsCache.getActions().itervalues():
            for step in action.getActions().itervalues():
                for actionData in step:
                    decorationID = actionData.uiDecoration
                    if not decorationID:
                        continue
                    decorations.append((decorationID, DECORATION_SIZES.DISCOUNT))

        return decorations

    @staticmethod
    def _urlGetter(fileserver):
        return fileserver.getMissionsDecorationUrl


class TokenSaleSubRequester(SubRequester):

    def pickup(self, tokenWebID):
        ticket = (tokenWebID,)
        return self._storage.get(ticket, False)

    def _tickets(self):
        tokens = []
        for quest in self._eventsCache.getQuests().itervalues():
            if quest.getType() not in EVENT_TYPE.QUESTS_WITH_SHOP_BUTTON:
                continue
            if not quest.isTokensOnSaleDynamic():
                continue
            for token in quest.accountReqs.getTokens():
                if token.isDisplayable() and token not in tokens:
                    tokens.append(token)

        if tokens:
            return [[ token.getWebID() for token in tokens ]]
        return []

    def _handler(self, ticket, content):
        tokenWebIDs = ticket
        data = json.loads(content)
        for item in data.get('data', []):
            attributes = item.get('attributes', {})
            properties = attributes.get('custom_properties', {})
            for tokenWebID, isOnSale in properties.iteritems():
                if tokenWebID in tokenWebIDs:
                    ticket = (tokenWebID,)
                    self._storage[ticket] = bool(isOnSale)

    @staticmethod
    def _urlGetter(_):
        return lambda *tokenWebIDs: GUI_SETTINGS.lookup('tokenShopAvailabilityURL') % ','.join(tokenWebIDs)

    @staticmethod
    def _headers():
        apiKey = GUI_SETTINGS.lookup('tokenShopAPIKey')
        return {'Authorization': 'Bearer {}'.format(apiKey)}

    def __contains__(self, ticket):
        return all(((webID,) in self._storage for webID in ticket))


class Prefetcher(object):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, eventsCache):
        self._eventsCache = weakref.proxy(eventsCache)
        self._asyncScope = None
        self._semaphore = None
        self._requesters = {}
        return

    def getTokenImage(self, styleID, size):
        return self._requesters['tokenImage'].pickup(styleID, size)

    def getMissionDecoration(self, decorationID, size):
        return self._requesters['decoration'].pickup(decorationID, size)

    def getTokenInfo(self, styleID):
        return self._requesters['tokenInfo'].pickup(styleID).title

    def getTokenDetailedInfo(self, styleID):
        return self._requesters['tokenInfo'].pickup(styleID).description

    def isTokenOnSale(self, tokenWebID):
        return self._requesters['tokenSale'].pickup(tokenWebID)

    def init(self):
        self._asyncScope = AsyncScope()
        self._semaphore = AsyncSemaphore(0, self._asyncScope)
        self._requesters = {'tokenImage': TokenImagesSubRequester(self._eventsCache, self._semaphore),
         'tokenInfo': TokenInfoSubRequester(self._eventsCache, self._semaphore),
         'tokenSale': TokenSaleSubRequester(self._eventsCache, self._semaphore),
         'decoration': DecorationRequester(self._eventsCache, self._semaphore)}

    def fini(self):
        self._asyncScope.destroy()

    def ask(self):
        filecache = BigWorld.player().customFilesCache
        fileserver = self.lobbyContext.getServerSettings().fileServer
        for requester in self._requesters.itervalues():
            requester.ask(filecache, fileserver)

    @wg_async
    def demand(self):
        demanded = []
        filecache = BigWorld.player().customFilesCache
        fileserver = self.lobbyContext.getServerSettings().fileServer
        for requester in self._requesters.itervalues():
            demanded.extend(requester.demand(filecache, fileserver))

        while demanded:
            yield wg_await(self._semaphore.acquire())
            demanded.pop()
