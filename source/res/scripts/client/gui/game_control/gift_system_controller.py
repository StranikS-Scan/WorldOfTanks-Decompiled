# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/gift_system_controller.py
import typing
from constants import Configs
from Event import Event, EventManager
from gifts.gifts_common import ClientReqStrategy
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.gift_system.hubs import createGiftEventHub
from gui.gift_system.hubs.base.hub_core import IGiftEventHub
from gui.gift_system.requesters.history_requester import GiftSystemHistoryRequester
from gui.gift_system.requesters.state_requester import GiftSystemWebStateRequester
from gui.gift_system.wrappers import skipNoHubsAction
from helpers import dependency
from helpers.server_settings import GiftSystemConfig
from skeletons.gui.game_control import IGiftSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsHistoryData, GiftsWebState
    from gui.shared import events
    from helpers.server_settings import ServerSettings, GiftEventConfig

class GiftSystemController(IGiftSystemController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__em = EventManager()
        self.onEventHubsCreated = Event(self.__em)
        self.onEventHubsDestroyed = Event(self.__em)
        self.__isLobbyInited = False
        self.__serverSettings = None
        self.__giftSystemSettings = None
        self.__eventHubs = {}
        self.__historyRequester = GiftSystemHistoryRequester(self.__onHistoryReceived)
        self.__webStateRequester = GiftSystemWebStateRequester(self.__onWebStateReceived)
        return

    def fini(self):
        self.__historyRequester.destroy()
        self.__webStateRequester.destroy()
        self.__em.clear()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onGiftSettingsChanged
        self.__destroyEventHubs(set(self.__eventHubs.keys()), onDisconnect=True)
        self.__serverSettings = self.__giftSystemSettings = None
        return

    def onLobbyInited(self, event=None):
        self.__updateLobbyState(isLobbyInited=True)
        self.__onWebStateReadyChanged(strategy=ClientReqStrategy.AUTO)
        self.__onHistoryReadyChanged(self.__itemsCache.items.giftSystem.isHistoryReady)
        self.__updateReadyListening()

    def getEventHub(self, eventID):
        return self.__eventHubs.get(eventID)

    def getSettings(self):
        return self.__giftSystemSettings

    def requestWebState(self, eventID):
        if eventID not in self.__eventHubs:
            return
        self.__onWebStateReadyChanged(strategy=ClientReqStrategy.DEMAND, eventIDs=[eventID])

    def __clear(self):
        self.__updateLobbyState(isLobbyInited=False)
        self.__webStateRequester.stop()
        self.__historyRequester.stop()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onGiftSettingsChanged(self, diff):
        if Configs.GIFTS_CONFIG.value in diff:
            self.__updateGiftSettings()

    def __onHistoryReadyChanged(self, isHistoryReady):
        if not isHistoryReady:
            return
        reqEventIDs = set((eID for eID, eHub in self.__eventHubs.iteritems() if eHub.isHistoryRequired()))
        self.__historyRequester.request(reqEventIDs)

    def __onHistoryReceived(self, history):
        for eventID, eventHub in ((eID, eHub) for eID, eHub in self.__eventHubs.iteritems() if eID in history):
            eventHub.processHistory(history[eventID])

        self.__onWebStateReadyChanged(strategy=ClientReqStrategy.AUTO)

    def __onWebStateReadyChanged(self, strategy, eventIDs=None):
        eventIDs = eventIDs or self.__eventHubs.keys()
        reqEventIDs = set((eID for eID in eventIDs if self.__eventHubs[eID].isWebStateRequired(strategy)))
        self.__webStateRequester.request(reqEventIDs)

    def __onWebStateReceived(self, webState):
        for eventID, eventHub in ((eID, eHub) for eID, eHub in self.__eventHubs.iteritems() if eID in webState):
            eventHub.processWebState(webState[eventID])

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onGiftSettingsChanged
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onGiftSettingsChanged
        self.__updateGiftSettings()
        return

    @skipNoHubsAction
    def __createEventHubs(self, hubsToCreate, eventsSettings):
        for eventID in hubsToCreate:
            self.__eventHubs[eventID] = createGiftEventHub(eventID, eventsSettings[eventID], self.__isLobbyInited)

        self.onEventHubsCreated(hubsToCreate)

    @skipNoHubsAction
    def __destroyEventHubs(self, hubsToDestroy, onDisconnect=False):
        if not onDisconnect:
            self.onEventHubsDestroyed(hubsToDestroy)
        for eventID in hubsToDestroy:
            self.__eventHubs[eventID].destroy()
            del self.__eventHubs[eventID]

    @skipNoHubsAction
    def __updateEventHubs(self, hubsToUpdate, eventsSettings):
        for eventID in hubsToUpdate:
            self.__eventHubs[eventID].updateSettings(eventsSettings[eventID])

    def __updateEventHubsSettings(self, prevSettings, newSettings):
        prevEvents, newEvents = prevSettings.events, newSettings.events
        prevEventsIDs, newEventsIDs = set(prevEvents.keys()), set(newEvents.keys())
        self.__destroyEventHubs(prevEventsIDs - newEventsIDs)
        self.__updateEventHubs(prevEventsIDs & newEventsIDs, newEvents)
        self.__createEventHubs(newEventsIDs - prevEventsIDs, newEvents)

    def __updateGiftSettings(self):
        prevSettings = self.__giftSystemSettings or GiftSystemConfig()
        self.__giftSystemSettings = self.__serverSettings.giftSystemConfig
        self.__updateEventHubsSettings(prevSettings, self.__giftSystemSettings)

    def __updateLobbyState(self, isLobbyInited=False):
        self.__isLobbyInited = isLobbyInited
        for eventHub in self.__eventHubs.itervalues():
            eventHub.getMessenger().setMessagesAllowed(isLobbyInited)

    def __updateReadyListening(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        if [ eventHub for eventHub in self.__eventHubs.itervalues() if eventHub.isHistoryRequired() ]:
            g_clientUpdateManager.addCallbacks({'cache.giftsData.isReady': self.__onHistoryReadyChanged})
