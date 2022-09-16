# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/reactive_comm/manager.py
import itertools
import logging
from collections import deque
import typing
import BigWorld
import wg_async
import websocket
from gui.game_control.reactive_comm import packer
from gui.game_control.reactive_comm import channel as _ce
from gui.game_control.reactive_comm import constants
_logger = logging.getLogger(__name__)

class ChannelsManager(object):
    __slots__ = ('__url', '__eventsSender', '__client', '__channels', '__cids', '__pending', '__callbackIDs')

    def __init__(self, url, eventsSender=None):
        super(ChannelsManager, self).__init__()
        self.__url = url
        self.__eventsSender = eventsSender
        self.__client = None
        self.__channels = {}
        self.__cids = {}
        self.__pending = deque()
        self.__callbackIDs = {}
        return

    @property
    def url(self):
        return self.__url

    @property
    def client(self):
        return self.__client

    def destroy(self):
        self.flush()
        self.__eventsSender = None
        self.__tryToDestroyClient(reset=True)
        return

    def flush(self):
        while self.__pending:
            event, _ = self.__pending.popleft()
            event.set()
            event.destroy()

        for channel, callbackID in self.__callbackIDs.iteritems():
            BigWorld.cancelCallback(callbackID)
            if channel in self.__channels:
                self.__channels[channel].unsubscribe(self.__client)
            _logger.warning('Channel %s is not in channels', channel)

        self.__callbackIDs.clear()

    def migrate(self, url):
        if self.__url == url:
            return
        self.__tryToDestroyClient(reset=False)
        self.__tryToCreateClient()
        self.__url = url
        if not self.__client.open(self.__url):
            _logger.error('Can not connect to server by url %s', self.__url)
            self.__tryToDestroyClient(reset=True)

    @wg_async.wg_async
    def subscribe(self, subscription):
        if not self.__url:
            _logger.error('Url of subscription service is empty')
            raise wg_async.AsyncReturn(_ce.SubscriptionStatus(constants.SubscriptionClientStatus.Disabled))
        name = subscription.channel
        if not _ce.isChannelNameValid(name):
            _logger.error('Name of channel is invalid: %r', name.decode('utf-8') if isinstance(name, str) else name)
            raise wg_async.AsyncReturn(_ce.SubscriptionStatus(constants.SubscriptionClientStatus.NameNotAllowed))
        if name in self.__channels:
            self.__cancelUnsubscribeCallback(name)
            channel = self.__channels[name]
        else:
            channel = self.__channels[name] = _ce.Channel(name, self.__eventsSender)
        if not channel.addSubscription(subscription):
            raise wg_async.AsyncReturn(_ce.SubscriptionStatus(constants.SubscriptionClientStatus.InvalidObject))
        if channel.isSubscribed:
            raise wg_async.AsyncReturn(channel.status)
        elif self.__tryToCreateClient():
            if self.__client.open(self.__url, reconnect=True):
                event = wg_async.AsyncEvent()
                self.__pending.append((event, subscription))
                yield wg_async.wg_await(event.wait())
                raise wg_async.AsyncReturn(channel.status)
            else:
                _logger.error('Can not connect to server by url %s', self.__url)
                raise wg_async.AsyncReturn(False)
        else:
            if self.__client.status == websocket.ConnectionStatus.Opened:
                channel.subscribe(self.__client)
            else:
                _logger.warning('Connection is not opened, waiting for reconnect to subscribe to channel <%s>', channel.name)
            event = wg_async.AsyncEvent()
            self.__pending.append((event, subscription))
            yield wg_async.wg_await(event.wait())
            raise wg_async.AsyncReturn(channel.status)

    def unsubscribe(self, subscription):
        name = subscription.channel
        if name in self.__channels:
            channel = self.__channels[name]
            channel.removeSubscription(subscription)
            if channel.isSubscribed and not channel.hasSubscription:
                self.__setUnsubscribeCallback(name)

            def _criteria(item):
                return item[1] == subscription

            self.__tryToTriggerEvents(_criteria)
            return True
        _logger.warning('Channel %s is not found to unsubscribe', name)
        return False

    def getLastMessage(self, subscription):
        name = subscription.channel
        if name in self.__channels:
            channel = self.__channels[name]
            if channel.isSubscribed:
                channel.getLastMessage(self.__client)
            return True
        _logger.warning('Channel %s is not found to get_last', name)
        return False

    def getChannelHistory(self, name):
        return self.__channels[name].messages if name in self.__channels else deque()

    def getChannelStatus(self, name):
        return self.__channels[name].status if name in self.__channels else _ce.SubscriptionStatus(constants.SubscriptionClientStatus.NotExists)

    def __tryToCreateClient(self):
        if self.__client is None:
            self.__client = websocket.Client()
            listener = self.__client.listener
            listener.onOpened += self.__onWebsocketOpened
            listener.onClosed += self.__onWebsocketClosed
            listener.onMessage += self.__onWebsocketMessage
            return True
        else:
            return False

    def __tryToDestroyClient(self, reset=True):
        if self.__client is not None:
            self.__client.terminate()
            self.__client = None
        if reset:
            for channel in self.__channels.itervalues():
                channel.clear()

            self.__channels.clear()
        return

    def __tryToTriggerEvents(self, criteria):
        found = list(itertools.ifilter(criteria, self.__pending))
        for event, subscription in found:
            self.__pending.remove((event, subscription))
            event.set()
            event.destroy()

    def __tryToTriggerEventsByChannel(self, name):

        def _criteria(item):
            return item[1].channel == name

        self.__tryToTriggerEvents(_criteria)

    def __setUnsubscribeCallback(self, channel):
        if channel not in self.__callbackIDs:

            def _invoke():
                self.__callbackIDs.pop(channel, None)
                if channel in self.__channels:
                    self.__channels[channel].unsubscribe(self.__client)
                else:
                    _logger.warning('Channel %s is not in channels', channel)
                return

            self.__callbackIDs[channel] = BigWorld.callback(constants.CHANNEL_UNSUBSCRIPTION_DELAY, _invoke)
        else:
            _logger.error('Request to unsubscribe from channel is already added: %s', channel)

    def __cancelUnsubscribeCallback(self, channel):
        callbackID = self.__callbackIDs.pop(channel, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __handleStatusReceived(self, message):
        name = message.channel
        if name in self.__channels:
            channel = self.__channels[name]
            channel.setStatus(message.status)
            self.__tryToTriggerEventsByChannel(name)
            if channel.isSubscribed:
                self.__cids[message.cid] = name
            else:
                self.__channels.pop(name)
                self.__cids.pop(message.cid, None)
        return

    def __handleMessageReceived(self, message):
        cid = message.cid
        if cid in self.__cids:
            self.__channels[self.__cids[cid]].addMessage(message)
        else:
            _logger.debug('Channel is not created on the client: %r', message)

    def __onWebsocketOpened(self, server):
        _logger.debug('ChannelsManager is connected to subscription service: server = %s', server)
        for channel in self.__channels.itervalues():
            if not channel.isSubscribed:
                channel.subscribe(self.__client)

    def __onWebsocketClosed(self, server, code, reason):
        _logger.debug('ChannelsManager is disconnected from subscription service: server = %s, code = %r, reason = %s', server, code, reason)
        for channel in self.__channels.itervalues():
            channel.close()

    def __onWebsocketMessage(self, code, payload):
        if code == websocket.OpCode.Binary:
            message = packer.unpackMessage(payload)
            if message.isStatusReceived:
                self.__handleStatusReceived(message)
            if message.isMessageReceived:
                self.__handleMessageReceived(message)
            if not message.isValid:
                _logger.error('Unexpected format of message from subscription service: %r', message)
        else:
            _logger.error('Binary message is expected from subscription service: %r, %r', code, payload)
