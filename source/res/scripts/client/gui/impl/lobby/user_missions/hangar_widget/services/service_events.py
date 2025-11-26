# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/service_events.py
from PlayerEvents import g_playerEvents
from gui.shared import g_eventBus, events

class ServiceEvents(object):

    def stopListening(self):
        raise NotImplementedError()

    def startListening(self):
        raise NotImplementedError()

    def startServiceEvents(self):
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer

    def stopServiceEvents(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer

    def __onLobbyInited(self, *_):
        self.startListening()

    def __onAccountBecomeNonPlayer(self):
        self.stopListening()
