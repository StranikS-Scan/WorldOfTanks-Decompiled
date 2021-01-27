# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/reactive_comm/service.py
import weakref
from collections import deque
import typing
import async
from gui.game_control.reactive_comm.constants import SubscriptionClientStatus
from gui.game_control.reactive_comm.channel import SubscriptionStatus, ChannelsEventsSender
from gui.game_control.reactive_comm.manager import ChannelsManager
from helpers import dependency
from skeletons.gui.game_control import IReactiveCommunicationService
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.game_control.reactive_comm.channel import Subscription
    from gui.game_control.reactive_comm.packer import ServiceMessage

class ReactiveCommunicationService(IReactiveCommunicationService, ChannelsEventsSender):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ReactiveCommunicationService, self).__init__()
        self.__manager = None
        return

    @property
    def isChannelSubscriptionAvailable(self):
        return self.__manager is not None

    @async.async
    def subscribeToChannel(self, subscription):
        if self.__manager is not None:
            result = yield async.await(self.__manager.subscribe(subscription))
        else:
            result = SubscriptionStatus(SubscriptionClientStatus.Disabled)
        raise async.AsyncReturn(result)
        return

    def unsubscribeFromChannel(self, subscription):
        return self.__manager.unsubscribe(subscription) if self.__manager is not None else False

    def getLastMessageFromChannel(self, subscription):
        return self.__manager.getLastMessage(subscription) if self.__manager is not None else False

    def getChannelHistory(self, name):
        return self.__manager.getChannelHistory(name) if self.__manager is not None else deque()

    def getChannelStatus(self, name):
        return self.__manager.getChannelStatus(name) if self.__manager is not None else SubscriptionStatus(SubscriptionClientStatus.Disabled)

    def fini(self):
        self.clear()
        super(ReactiveCommunicationService, self).fini()

    def onLobbyStarted(self, ctx):
        self.__update()
        self.__addListeners()

    def onDisconnected(self):
        self.__removeListeners()
        self.__clear()

    def onAvatarBecomePlayer(self):
        if self.__manager is not None:
            self.__manager.flush()
        self.__removeListeners()
        return

    def __clear(self):
        if self.__manager is not None:
            self.__manager.destroy()
            self.__manager = None
        return

    def __update(self):
        config = self.__lobbyContext.getServerSettings().getReactiveCommunicationConfig()
        if not config.isEnabled:
            self.__clear()
        elif self.__manager is None:
            self.__manager = ChannelsManager(config.url, weakref.proxy(self))
        elif self.__manager.url != config.url:
            self.__manager.migrate(config.url)
        return

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def __onServerSettingsChanged(self, _):
        self.__update()
