# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/notification.py
from gui.SystemMessages import SM_TYPE, pushI18nMessage, pushMessage
from web_client_api import WebCommandException, w2c, W2CSchema, Field

class _NotificationSchema(W2CSchema):
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


class NotificationWebApiMixin(object):

    @w2c(_NotificationSchema, 'notification')
    def notification(self, cmd):
        smType = SM_TYPE.lookup(cmd.type)
        if smType is None:
            raise WebCommandException("Unknown notification's type: %s!" % cmd.type)
        if cmd.hasMessage():
            pushMessage(cmd.message, type=smType, messageData=cmd.message_data)
        elif cmd.hasI18nKey():
            parameters = cmd.i18n_data
            params = {'type': smType,
             'key': cmd.i18n_key,
             'messageData': cmd.message_data}
            for key, value in parameters.iteritems():
                params[key] = value

            pushI18nMessage(**params)
        elif cmd.hasKey():
            custom_parameters = cmd.custom_parameters
            params = {'type': smType,
             'key': cmd.key,
             'messageData': cmd.message_data}
            for key, value in custom_parameters.iteritems():
                params[key] = value

            pushI18nMessage(**params)
        return
