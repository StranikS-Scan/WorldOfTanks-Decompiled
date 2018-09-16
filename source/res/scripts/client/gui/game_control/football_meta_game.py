# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/football_meta_game.py
from collections import namedtuple
import itertools
import Event
import constants
from gui import SystemMessages
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events.formatters import parseComplexToken
from gui.shared.gui_items.processors.football import PacketsOpener, BuffonRecruiter
from gui.shared.utils.decorators import process
from helpers import dependency, i18n
from items.football_config import DECK_TYPES, DECK_TOKENS, MILESTONE, calculateProgress, calculateMilestone, BUFFON_TOKEN, PACKET_TOKENS, CARDS_BY_TOKEN
from skeletons.gui.game_control import IFootballMetaGame
from skeletons.gui.server_events import IEventsCache
from gui.ClientUpdateManager import g_clientUpdateManager
Deck = namedtuple('Deck', 'type, count, diff')
Packet = namedtuple('Packet', 'random, striker, midfielder, defender')
DECKS_GUI_ORDER = list(reversed(list(itertools.chain.from_iterable(DECK_TOKENS))))
_PACKET_TOKEN_POSTFIX_TEMPLATE = '_{}'

def _formatPacketTokenPostfix(tokenID):
    complexToken = parseComplexToken(tokenID)
    return _PACKET_TOKEN_POSTFIX_TEMPLATE.format(complexToken.webID)


_PACKET_TOKEN_POSTFIX = {tokenID:_formatPacketTokenPostfix(tokenID) for tokenID in PACKET_TOKENS}

class _GuiDataStorage(object):

    def __init__(self):
        super(_GuiDataStorage, self).__init__()
        self.__isPlayerPacketsNotified = False

    def isPlayerPacketsNotified(self):
        return self.__isPlayerPacketsNotified

    def setPlayerPacketsNotified(self, value):
        self.__isPlayerPacketsNotified = value


class FootballMetaGame(IFootballMetaGame):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__eventsManager = Event.EventManager()
        self.onPacketsOpened = Event.Event(self.__eventsManager)
        self.onMilestoneReached = Event.Event(self.__eventsManager)
        self.onPacketsUpdated = Event.Event(self.__eventsManager)
        self.onBuffonRecruited = Event.Event(self.__eventsManager)
        self.__decks = []
        self.__milestone = MILESTONE.NONE
        self.__guiDataStorage = None
        return

    def init(self):
        g_clientUpdateManager.addCallback(diffpath='tokens', handler=self.__updateState)

    def fini(self):
        g_clientUpdateManager.removeCallback(diffpath='tokens', handler=self.__updateState)
        self.__eventsManager.clear()
        self.__clear()

    def onLobbyStarted(self, _):
        self.__updateState({})
        self.__guiDataStorage = _GuiDataStorage()

    def onDisconnected(self):
        self.__clear()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def getGuiDataStorage(self):
        return self.__guiDataStorage

    def getTokenInfo(self, tokenID):
        if tokenID in PACKET_TOKENS:
            styleID = QUESTS.TOKEN_DEFAULT_CARD.split('/')[-1]
            tooltipID = styleID + _PACKET_TOKEN_POSTFIX[tokenID]
        elif tokenID == BUFFON_TOKEN:
            styleID = QUESTS.TOKEN_DEFAULT_BUFFON.split('/')[-1]
            tooltipID = styleID
        else:
            return (None, None, None)
        tooltipHeader = i18n.makeString(FOOTBALL2018.getAwardTooltipPart(tooltipID, 'header'))
        tooltipBody = i18n.makeString(FOOTBALL2018.getAwardTooltipPart(tooltipID, 'body'))
        return (styleID, tooltipHeader, tooltipBody)

    def getDecks(self):
        decks = []
        cardsCount = self.__getCardsCount()
        for deckName in DECKS_GUI_ORDER:
            count = cardsCount.get(deckName)
            decks.append(Deck(type=DECK_TYPES.get(deckName), count=count, diff=0))

        return decks

    def getPackets(self):
        packets = []
        packetsCount = self.__getPacketsCount()
        for packetName, count in packetsCount.iteritems():
            for _ in range(count):
                packets.append(Packet(*CARDS_BY_TOKEN.get(packetName)))

        return packets

    def getProgress(self):
        return calculateProgress(self.__getCardsCount())

    def hasPackets(self):
        return bool(self.getPackets())

    def isBuffonAvailable(self):
        progress = self.eventsCache.questsProgress
        return bool(progress.getTokenCount(BUFFON_TOKEN))

    def isBuffonRecruited(self):
        progress = self.eventsCache.questsProgress
        return bool(self.getMilestone() == MILESTONE.THIRD and not progress.getTokenCount(BUFFON_TOKEN))

    def getMilestone(self):
        return calculateMilestone(self.getProgress())

    @process('updating')
    def openPackets(self):
        result = yield PacketsOpener().request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @process('recruting')
    def recruitBuffon(self, vehicleIntCD):
        result = yield BuffonRecruiter(vehicleIntCD).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        self.onBuffonRecruited(result.success)

    def __getCardsCount(self):
        progress = self.eventsCache.questsProgress
        decks = {}
        for deckName in DECKS_GUI_ORDER:
            decks.update({deckName: progress.getTokenCount(deckName)})

        return decks

    def __getPacketsCount(self):
        progress = self.eventsCache.questsProgress
        packets = {}
        for packetName in PACKET_TOKENS:
            count = progress.getTokenCount(packetName)
            if count:
                packets.update({packetName: count})

        return packets

    def __updateState(self, diff):
        tokens = [ token for token in diff.iterkeys() if 'fb18' in token ]
        milestone = self.getMilestone()
        isPacketsUp = any((token in CARDS_BY_TOKEN for token in tokens))
        isDeckUp = any((token in CARDS_BY_TOKEN and diff[token] is None for token in tokens))
        if self.__milestone != milestone:
            self.onMilestoneReached()
        if isPacketsUp:
            self.__guiDataStorage.setPlayerPacketsNotified(False)
            self.onPacketsUpdated()
        if isDeckUp:
            decks = []
            for od, nd in zip(self.__decks, self.getDecks()):
                diff = nd.count - od.count
                decks.append(Deck(nd.type, nd.count, diff))

            self.onPacketsOpened(decks)
        self.__milestone = milestone
        self.__decks = self.getDecks()

    if constants.IS_DEVELOPMENT:

        def getState(self):
            progress = self.eventsCache.questsProgress
            tokens = {}
            for token, data in progress.getCacheValue('tokens', {}).iteritems():
                if 'fb18' in token:
                    tokens.update({token: data})

            return tokens

    def __clear(self):
        self.__guiDataStorage = None
        return
