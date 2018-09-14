# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/notification.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_NotificationCommand = namedtuple('_NotificationCommand', ('type', 'message', 'message_data', 'i18n_key', 'i18n_data', 'key', 'custom_parameters'))
_NotificationCommand.__new__.__defaults__ = (None,
 None,
 {},
 None,
 {},
 None,
 {})
_NotificationCommandScheme = {'required': (('type', basestring),),
 'unions': (('message', basestring), ('i18n_key', basestring), ('key', basestring)),
 'optional': (('message_data', dict), ('i18n_data', dict)),
 'deprecated': (('key', 'prefer "i18n_key"'),)}

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

    def hasI18nKey(self):
        return self.i18n_key is not None


def createNotificationHandler(handlerFunc):
    data = {'name': 'notification',
     'cls': NotificationCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
