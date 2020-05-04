# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/chat_controller.py
import logging
import gui.shared
from constants import QUEUE_TYPE
from helpers import dependency
from skeletons.se20 import ICustomizableObjectsManager
from messenger.ext import channel_num_gen
from messenger.m_constants import LAZY_CHANNEL
from gui.prb_control.events_dispatcher import _defCarouselItemCtx
from gui.Scaleform.framework.managers.containers import VIEW_SEARCH_CRITERIA
from messenger.gui.events_dispatcher import showLazyChannelWindow
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from soft_exception import SoftException
from skeletons.gui.server_events import IEventsCache
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SECRET_EVENT_CHAT_FIRST_SEEN
_logger = logging.getLogger(__name__)

class ChatConntroller(object):
    customizableObjectsManager = dependency.descriptor(ICustomizableObjectsManager)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__clientID = channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.SECRET_EVENT)
        if not self.__clientID:
            SoftException('Client ID not found. Secret event channel does not work')
        self.__isChatEnabled = False
        self.__isShown = False
        self.__currentQueueType = None
        return

    def start(self):
        gui.shared.g_eventBus.addListener(gui.shared.events.GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)
        self.eventsCache.onSyncCompleted += self._onSyncCompleted

    def stop(self):
        gui.shared.g_eventBus.removeListener(gui.shared.events.GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)
        self.customizableObjectsManager.onPrbEntityChanged -= self._onPrbEntityChanged
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted

    def removeSecretEventChannelFromCarousel(self):
        if self.__isShown:
            gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(self.__clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_REMOVE), gui.shared.EVENT_BUS_SCOPE.LOBBY)
            self.__isShown = False

    def addSecretEventChannelToCarousel(self):
        if not self.__isShown:
            currCarouselItemCtx = _defCarouselItemCtx._replace(label=LAZY_CHANNEL.SECRET_EVENT, order=channel_num_gen.getOrder4LazyChannel(LAZY_CHANNEL.SECRET_EVENT), isNotified=not self.__chatFirstSeen, criteria={VIEW_SEARCH_CRITERIA.VIEW_UNIQUE_NAME: gui.shared.utils.functions.getViewName(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, self.__clientID)}, openHandler=lambda : showLazyChannelWindow(self.__clientID))
            gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(self.__clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_ADD, currCarouselItemCtx._asdict()), gui.shared.EVENT_BUS_SCOPE.LOBBY)
            self.__isShown = True
            self.__setChatFirstSeen()

    def _onLobbyInited(self, _):
        self.customizableObjectsManager.onPrbEntityChanged += self._onPrbEntityChanged
        self._getParams()

    def _onPrbEntityChanged(self, queueType):
        self.__currentQueueType = queueType
        self._update()

    def _update(self):
        if self.__isChatEnabled and self.__currentQueueType == QUEUE_TYPE.EVENT_BATTLES:
            self.addSecretEventChannelToCarousel()
        else:
            self.removeSecretEventChannelFromCarousel()

    def _getParams(self):
        self.__isChatEnabled = self.eventsCache.getGameEventData().get('isChatEnabled', False)

    def _onSyncCompleted(self):
        self._getParams()
        self._update()

    def __setChatFirstSeen(self):
        AccountSettings.setCounters(SECRET_EVENT_CHAT_FIRST_SEEN, True)

    @property
    def __chatFirstSeen(self):
        return AccountSettings.getCounters(SECRET_EVENT_CHAT_FIRST_SEEN)
