# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/notification.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_NotificationCommand = namedtuple('_NotificationCommand', ('type', 'message', 'key', 'custom_parameters'))
_NotificationCommand.__new__.__defaults__ = (None,
 None,
 None,
 {})
_NotificationCommandScheme = {'required': (('type', basestring),),
 'unions': (('key', basestring), ('message', basestring))}

class NotificationCommand(_NotificationCommand, SchemeValidator):
    """
    Represents web command for showing notification.
    """

    def __init__(self, *args, **kwargs):
        super(NotificationCommand, self).__init__(_NotificationCommandScheme)

    def hasKey(self):
        return self.key is not None

    def hasMessage(self):
        return self.message is not None


def createNotificationHandler(handlerFunc):
    data = {'name': 'notification',
     'cls': NotificationCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
