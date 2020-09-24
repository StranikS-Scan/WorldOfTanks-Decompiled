# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/reactive_comm/channel.py
import logging
import re
from collections import deque
import typing
import Event
import websocket
from gui.game_control.reactive_comm import constants
from gui.game_control.reactive_comm import packer
_logger = logging.getLogger(__name__)
_channelRegExp = re.compile('^[a-zA-Z0-9_-]{2,36}$')

def isChannelNameValid(name):
    return _channelRegExp.match(name) is not None if isinstance(name, str) else False


class ChannelsEventsSender(object):

    def __init__(self):
        super(ChannelsEventsSender, self).__init__()
        self.__em = Event.EventManager()
        self.onChannelMessage = Event.Event(self.__em)
        self.onChannelClosed = Event.Event(self.__em)
        self.onSubscriptionClosed = Event.Event(self.__em)

    def clear(self):
        self.__em.clear()


class Channel(object):
    __slots__ = ('__weakref__', '__name', '__clientStatus', '__serverStatus', '__messages', '__subscriptions', '__eventsSender')

    def __init__(self, name, eventsSender=None):
        super(Channel, self).__init__()
        self.__name = name
        self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed
        self.__serverStatus = constants.SubscriptionServerStatus.Unsubscribed
        self.__messages = deque(maxlen=constants.MAX_CHANNEL_HISTORY)
        self.__subscriptions = []
        self.__eventsSender = eventsSender

    @property
    def name(self):
        return self.__name

    @property
    def status(self):
        return SubscriptionStatus(self.__clientStatus, self.__serverStatus)

    @property
    def isSubscribed(self):
        return self.__clientStatus == constants.SubscriptionClientStatus.Subscribed

    @property
    def hasSubscription(self):
        return len(self.__subscriptions) > 0

    @property
    def messages(self):
        return deque(self.__messages)

    def clear(self):
        self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed
        self.__clearSubscriptions(reason=constants.SubscriptionCloseReason.Cancel)
        self.__eventsSender = None
        return

    def close(self):
        self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed

    def subscribe(self, client):
        if self.__clientStatus == constants.SubscriptionClientStatus.Subscribed:
            _logger.warning('Client is already subscribed to channel <%s>', self.__name)
            return
        if client.status == websocket.ConnectionStatus.Opened:
            if self.__clientStatus != constants.SubscriptionClientStatus.Subscribing:
                _logger.debug('Request to subscribe to channel <%s> is sending', self.__name)
                self.__clientStatus = constants.SubscriptionClientStatus.Subscribing
                client.sendBinary(packer.packCommand(self.__name, constants.SubscriptionCommand.Subscribe))
        else:
            _logger.error('Request to subscribe to channel <%s> can not be invoked, connection is not opened', self.__name)

    def unsubscribe(self, client):
        if self.__clientStatus == constants.SubscriptionClientStatus.Unsubscribed:
            _logger.warning('Client is already unsubscribed from channel <%s>', self.__name)
            return
        if client.status == websocket.ConnectionStatus.Opened:
            if self.__clientStatus != constants.SubscriptionClientStatus.Unsubscribing:
                _logger.debug('Request to unsubscribe from channel <%s> is sending', self.__name)
                self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribing
                client.sendBinary(packer.packCommand(self.__name, constants.SubscriptionCommand.Unsubscribe))
        else:
            self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed

    def addSubscription(self, subscription):
        if isinstance(subscription, Subscription) and subscription not in self.__subscriptions and subscription.channel == self.__name:
            self.__subscriptions.append(subscription)
            return True
        return False

    def removeSubscription(self, subscription):
        if subscription in self.__subscriptions:
            self.__subscriptions.remove(subscription)
            reason = constants.SubscriptionCloseReason.Request
            if self.__eventsSender is not None:
                self.__eventsSender.onSubscriptionClosed(subscription, reason)
            subscription.onClosed(reason)
            subscription.clear()
            return True
        else:
            return False

    def setStatus(self, status):
        if status == constants.SubscriptionServerStatus.ChannelDeleted:
            _logger.debug('Channel <%s> is deleted in subscriptions service', self.__name)
            self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed
            self.__messages.clear()
            self.__clearSubscriptions(reason=constants.SubscriptionCloseReason.Deleted)
        elif self.__clientStatus == constants.SubscriptionClientStatus.Subscribing:
            if status == constants.SubscriptionServerStatus.Subscribed:
                _logger.debug('Request to subscribe to channel <%s> is success', self.__name)
                self.__clientStatus = constants.SubscriptionClientStatus.Subscribed
            else:
                _logger.error('Request to subscribe to channel <%s> is failed: %r', self.__name, status)
                self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed
        elif self.__clientStatus == constants.SubscriptionClientStatus.Unsubscribing:
            if status == constants.SubscriptionServerStatus.Unsubscribed:
                _logger.debug('Request to unsubscribe from channel <%s> is success', self.__name)
                self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed
                self.__messages.clear()
            else:
                _logger.error('Request to unsubscribe from channel <%s> is failed: %r', self.__name, status)
                self.__clientStatus = constants.SubscriptionClientStatus.Unsubscribed
                self.__messages.clear()
            self.__clearSubscriptions(reason=constants.SubscriptionCloseReason.Request)
        else:
            _logger.warning('Channel response <%s> is not handled: %r, %r', self.__name, self.__clientStatus, status)
        self.__serverStatus = status

    def addMessage(self, message):
        if self.__clientStatus == constants.SubscriptionClientStatus.Subscribed:
            self.__messages.append(message)
            for subscription in self.__subscriptions:
                subscription.onMessage(message)

            if self.__eventsSender is not None:
                self.__eventsSender.onChannelMessage(self.__name, message)
            return True
        else:
            return False

    def __clearSubscriptions(self, reason=constants.SubscriptionCloseReason.Cancel):
        for subscription in self.__subscriptions:
            if self.__eventsSender is not None:
                self.__eventsSender.onSubscriptionClosed(subscription, reason)
            subscription.onClosed(reason)
            subscription.clear()

        if self.__eventsSender is not None:
            self.__eventsSender.onChannelClosed(self.__name, reason)
        del self.__subscriptions[:]
        return


class Subscription(object):
    __slots__ = ('__channel', '__em', 'onMessage', 'onClosed')

    def __init__(self, channel):
        super(Subscription, self).__init__()
        self.__channel = channel
        self.__em = Event.EventManager()
        self.onMessage = Event.Event(self.__em)
        self.onClosed = Event.Event(self.__em)

    @property
    def channel(self):
        return self.__channel

    def clear(self):
        self.__channel = ''
        self.__em.clear()


class SubscriptionStatus(object):
    __slots__ = ('__clientStatus', '__serverStatus')

    def __init__(self, clientStatus=constants.SubscriptionClientStatus.Unsubscribed, serverStatus=constants.SubscriptionServerStatus.Unsubscribed):
        super(SubscriptionStatus, self).__init__()
        self.__clientStatus = clientStatus
        self.__serverStatus = serverStatus

    def __repr__(self):
        return '{}(client={}, server={})'.format(self.__class__.__name__, self.__clientStatus, self.__serverStatus)

    def __nonzero__(self):
        return self.isSubscribed

    @property
    def isSubscribed(self):
        return self.__clientStatus == constants.SubscriptionClientStatus.Subscribed

    @property
    def client(self):
        return self.__clientStatus

    @property
    def server(self):
        return self.__serverStatus
