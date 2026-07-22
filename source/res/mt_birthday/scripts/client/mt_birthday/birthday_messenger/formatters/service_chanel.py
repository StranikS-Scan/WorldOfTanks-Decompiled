# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_messenger/formatters/service_chanel.py
from copy import copy
from messenger import g_settings
from messenger.formatters.service_channel import ClientSysMessageFormatter
from messenger.formatters.service_channel_helpers import MessageData
from mt_birthday.birthday_constants import GFNotificationTemplates

class BirthdayGiftSMFormatter(ClientSysMessageFormatter):
    _TEMPLATE = GFNotificationTemplates.CUSTOM_BIRTHDAY_GIFT_NOTIFICATION

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self._TEMPLATE, data={'linkageData': copy(message)})
        guiSettings = self._getGuiSettings(message, self._TEMPLATE)
        return [MessageData(formatted, guiSettings)]
