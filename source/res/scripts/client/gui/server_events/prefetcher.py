# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/prefetcher.py
import json
import itertools
import weakref
import BigWorld
import ResMgr
from async import async, await, await_callback, AsyncScope, AsyncSemaphore
from constants import EVENT_TYPE
from debug_utils import LOG_WARNING
from gui import GUI_SETTINGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.formatters import isMarathon, TOKEN_SIZES, DECORATION_SIZES
from gui.shared.utils import mapTextureToTheMemory, getImageSize
from helpers import getClientLanguage, dependency
from helpers.i18n import makeString as ms
from skeletons.gui.lobby_context import ILobbyContext
_DEFAULT_TOKENS_STYLES = [ title.split('/')[-1] for title in QUESTS.TOKEN_DEFAULT_ENUM ]
_DEFAULT_DECORATIONS = [ title.split('_')[-1].replace('.png', '') for title in RES_ICONS.MAPS_ICONS_MISSIONS_DECORATIONS_DECORATION_ENUM ]

class SubRequester(object):
    """ Base class for all requesters.
    """

    def __init__(self, eventsCache, semaphore):
        self._eventsCache = eventsCache
        self._semaphore = semaphore
        self._storage = {}

    def pickup(self, ticket):
        """ Get requested data from storage.
        """
        return self._storage.get(ticket)

    def ask(self, filecache, fileserver):
        """ Request data beforehand for future usage, i.e. don't wait for result.
        """
        tickets = self._tickets()
        for ticket in tickets:
            url = self._urlGetter(fileserver)(*ticket)
            headers = self._headers()
            if url and ticket not in self:
                filecache.get(url, headers=headers, callback=lambda name, content: None)

    def demand(self, filecache, fileserver):
        """ Request data for current usage right now, i.e. wait for result.
        """
        demanded = []
        tickets = self._tickets()
        for ticket in tickets:
            url = self._urlGetter(fileserver)(*ticket)
            headers = self._headers()
            if url and ticket not in self:
                demanded.append(url)
                self._run(url, headers, ticket, filecache)

        return demanded

    @async
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
        """ Async handler that actually waits for the demanded data.
        """
        pass

    def _tickets(self):
        """ Grab tickets that needs to be requested from events cache.
        """
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
    """ Requester for token images (of two sizes: 60x60 and 80x80)
    """

    def pickup(self, styleID, size):
        ticket = (styleID, size)
        if styleID in _DEFAULT_TOKENS_STYLES:
            return RES_ICONS.getTokenImage(size, styleID)
        else:
            content = self._storage.get(ticket)
            if content:
                return 'img://{}'.format(mapTextureToTheMemory(content))
            return RES_ICONS.getTokenUndefinedImage(size)

    def _handler(self, ticket, content):
        _, expectedSize = ticket
        actualSize = '{}x{}'.format(*getImageSize(content))
        if expectedSize != actualSize:
            raise ValueError('Downloaded image has invalid size')
        self._storage[ticket] = content

    def _tickets(self):
        tickets = []
        for quest in self._eventsCache.getQuests().itervalues():
            if quest.getType() not in (EVENT_TYPE.TOKEN_QUEST, EVENT_TYPE.BATTLE_QUEST):
                continue
            for token in quest.accountReqs.getTokens():
                styleID = token.getStyleID()
                if token.isDisplayable() and styleID not in _DEFAULT_TOKENS_STYLES and styleID not in tickets:
                    tickets.append(styleID)

        return itertools.product(tickets, TOKEN_SIZES.ALL())

    @staticmethod
    def _urlGetter(fileserver):
        return fileserver.getMissionsTokenImageUrl


class TokenInfoSubRequester(SubRequester):
    """ Requester for tokens titles.
    """

    def pickup(self, styleID):
        ticket = (styleID,)
        if styleID in _DEFAULT_TOKENS_STYLES:
            return QUESTS.getTokenTitle(styleID)
        else:
            return self._storage.get(ticket) or QUESTS.TOKEN_UNDEFINED

    def _handler(self, ticket, content):
        section = ResMgr.DataSection()
        section.createSectionFromString(content)
        tokens = section['root/tokens']
        for item in tokens.values():
            tokenID = item['id'].asString
            title = item['title'].asString
            ticket = (tokenID,)
            self._storage[ticket] = ms(MENU.QUOTE, string=title)

    def _tickets(self):
        return [(getClientLanguage(),)]

    @staticmethod
    def _urlGetter(fileserver):
        return fileserver.getMissionsTokenDescrsUrl

    def __contains__(self, _):
        return False


class DecorationRequester(SubRequester):
    """ Requester for quest's decorations.
    
    Depending on type of quests, decoration means different things.
    - uiDecoration of regular quest means custom background of its preview card;
    - uiDecoration of main token quest means custom bonus image;
    - uiDecoration of group means custom group background;
    - uiDecoration of discound means custom discount image.
    """

    def pickup(self, decorationID, size):
        ticket = (decorationID, size)
        if size == DECORATION_SIZES.BONUS:
            if str(decorationID) in _DEFAULT_DECORATIONS:
                return RES_ICONS.getQuestDecoration(decorationID)
            default = RES_ICONS.MAPS_ICONS_MISSIONS_DECORATIONS_UNDEFINED
        else:
            default = ''
        content = self._storage.get(ticket)
        if content:
            return 'img://{}'.format(mapTextureToTheMemory(content))
        else:
            return default

    def _handler(self, ticket, content):
        _, expectedSize = ticket
        actualSize = '{}x{}'.format(*getImageSize(content))
        if actualSize != expectedSize:
            raise ValueError('Downloaded image has invalid size')
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
            if isMarathon(quest.getID()):
                if str(decorationID) not in _DEFAULT_DECORATIONS:
                    decorations.append((decorationID, DECORATION_SIZES.BONUS))
            if quest.getType() not in EVENT_TYPE.SHARED_QUESTS:
                decorations.append((decorationID, DECORATION_SIZES.CARDS))

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
    """ Requester for tokens sale availability (i.e. whether they can be purchased or not).
    
    We need to ask PremShop about token availability. They put a special property
    to the packages that contain token, so we're creating request to the PremShop's
    items API to fetch the packages with tokens:
    
        .../shop/api/v2/items?filter[custom_properties]=TokenWebId_1,TokenWebId_2
    
    We also ask to include 'custom_properties' field in the response, so we have
    the ability to know which package sells what tokens:
    
        ...&fields[items]=custom_properties
    
    Complete url is in gui_settings.xml.
    
    Response has the following structure:
    {
        "data": [
            {
                "attributes": {
                    "custom_properties": {
                        "TokenWebId_1": "1",
                        "TokenWebId_2": "1",
                        "TokenWebId_3": "1"
                    }
                },
                "id": "1593",
                "type": "items"
            }
        ],
        "meta": {
            "author": "Payment System Team",
            "license": "Wargaming.net"
        }
    }
    """

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
        else:
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
    """ This class is responsible for requesting quests-related data from web services.
    """
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
        return self._requesters['tokenInfo'].pickup(styleID)

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

    @async
    def demand(self):
        demanded = []
        filecache = BigWorld.player().customFilesCache
        fileserver = self.lobbyContext.getServerSettings().fileServer
        for requester in self._requesters.itervalues():
            demanded.extend(requester.demand(filecache, fileserver))

        while demanded:
            yield await(self._semaphore.acquire())
            demanded.pop()
