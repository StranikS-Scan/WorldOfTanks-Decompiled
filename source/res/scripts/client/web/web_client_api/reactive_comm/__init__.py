# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/reactive_comm/__init__.py
import adisp
import async
from gui.game_control.reactive_comm import Subscription, SubscriptionClientStatus, SubscriptionServerStatus
from helpers import dependency
from skeletons.gui.game_control import IReactiveCommunicationService
from web.web_client_api import w2c, w2capi, Field, W2CSchema

class _SubscriptionSchema(W2CSchema):
    channel_name = Field(required=True, type=basestring)


@w2capi(name='reactive_communication_service', key='action', finiHandlerName='_finiSubscriptionsHandler')
class ReactiveCommunicationWebApi(object):
    __service = dependency.descriptor(IReactiveCommunicationService)

    def __init__(self):
        super(ReactiveCommunicationWebApi, self).__init__()
        self.__subscriptions = {}

    @w2c(W2CSchema, name='is_channel_subscription_available')
    def isSubscriptionAvailable(self, _):
        return self.__service.isChannelSubscriptionAvailable

    @w2c(_SubscriptionSchema, 'subscribe_to_channel')
    def subscribe(self, cmd):
        name = cmd.channel_name.encode('utf-8')
        if name not in self.__subscriptions:
            self.__subscriptions[name] = subscription = Subscription(name)
            self.__service.onSubscriptionClosed += self.__onSubscriptionClosed
            status = yield self.__doSubscribe(subscription)
            if not status:
                self.__subscriptions.pop(name, None)
            yield {'channel_name': name,
             'subscription_id': id(subscription),
             'status': {'client': status.client.value,
                        'server': status.server.value}}
        else:
            yield {'channel_name': name,
             'status': {'client': SubscriptionClientStatus.AlreadySubscribed.value,
                        'server': SubscriptionServerStatus.Subscribed.value}}
        return

    @w2c(_SubscriptionSchema, 'unsubscribe_from_channel')
    def unsubscribe(self, cmd):
        name = cmd.channel_name.encode('utf-8')
        success = False
        subscriptionID = 0
        if name in self.__subscriptions:
            subscription = self.__subscriptions.pop(name)
            subscriptionID = id(subscription)
            success = self.__service.unsubscribeFromChannel(subscription)
        return {'channel_name': name,
         'subscription_id': subscriptionID,
         'success': success}

    def _finiSubscriptionsHandler(self):
        self.__service.onSubscriptionClosed -= self.__onSubscriptionClosed
        for subscription in self.__subscriptions.values():
            self.__service.unsubscribeFromChannel(subscription)

        self.__subscriptions.clear()

    @adisp.async
    @async.async
    def __doSubscribe(self, subscription, callback):
        status = yield async.await(self.__service.subscribeToChannel(subscription))
        callback(status)

    def __onSubscriptionClosed(self, subscription, _):
        self.__subscriptions.pop(subscription, None)
        return
