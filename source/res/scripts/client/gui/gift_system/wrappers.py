# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/wrappers.py
from collections import namedtuple
from functools import wraps
GiftsHistoryData = namedtuple('GiftsHistoryData', ('aggregated', 'detailed'))
GiftsWebState = namedtuple('GiftsWebState', ('sendLimit', 'expireTime', 'expireDelta', 'executionTime', 'state'))
IncomeSysMessage = namedtuple('IncomeSysMessage', ('eventID', 'senderID', 'giftItemID', 'meta', 'executionTime'))
SendGiftResponse = namedtuple('SendGiftResponse', ('state', 'receiverID', 'outCount', 'entitlementCode', 'meta', 'executionTime'))

def ifMessagesEnabled(method):

    @wraps(method)
    def wrapper(messenger, *args, **kwargs):
        if messenger.isMessagesEnabled():
            method(messenger, *args, **kwargs)

    return wrapper


def ifMessagesAllowed(msgType, useQueue=True):

    def decorator(method):

        @wraps(method)
        def wrapper(messenger, *args, **kwargs):
            if not messenger.isMessagesSuspended(*args, **kwargs):
                method(messenger, *args, **kwargs)
            elif useQueue:
                messenger.addToQueue(msgType, *args, **kwargs)

        return wrapper

    return decorator


def skipNoHubsAction(method):

    @wraps(method)
    def wrapper(controller, hubsToAction, *args, **kwargs):
        if hubsToAction:
            method(controller, hubsToAction, *args, **kwargs)

    return wrapper
