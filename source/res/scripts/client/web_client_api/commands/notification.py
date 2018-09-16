# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/notification.py
from command import W2CSchema, Field, createCommandHandler

class NotificationSchema(W2CSchema):
    __unions__ = ('message', 'i18n_key', 'key')
    type = Field(required=True, type=basestring)
    message = Field(type=basestring)
    message_data = Field(type=dict)
    i18n_key = Field(type=basestring)
    i18n_data = Field(type=dict)
    key = Field(type=basestring, deprecated='prefer "i18n_key"')

    def hasKey(self):
        return self.key is not None

    def hasMessage(self):
        return self.message is not None

    def hasI18nKey(self):
        return self.i18n_key is not None


def createNotificationHandler(handlerFunc):
    return createCommandHandler('notification', NotificationSchema, handlerFunc)
