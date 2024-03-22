# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/personal_reserves.py
from gui.impl import backport
from gui.impl.gen import R
from helpers import html
from messenger import g_settings
from messenger.formatters.service_channel import GeneralFormatter

class IPersonalReservesFormatter(GeneralFormatter):

    def __init__(self):
        super(IPersonalReservesFormatter, self).__init__('PersonalReservesMessage')


class IPersonalReservesExpirableFormatter(GeneralFormatter):

    def __init__(self):
        super(IPersonalReservesExpirableFormatter, self).__init__('PersonalReservesExpirableMessage')


class ReleaseFormatter(IPersonalReservesFormatter):

    def getTitle(self, message, *args):
        return backport.text(R.strings.messenger.serviceChannelMessages.personalReservesRelease.title())

    def getText(self, message, *args):
        return g_settings.htmlTemplates.format('personalReservesRelease', ctx={'boosterCount': html.escape(message.get('values', ''))})


class PersonalReservesSoonExpirationFormatter(IPersonalReservesExpirableFormatter):

    def getTitle(self, message, *args):
        return backport.text(R.strings.messenger.serviceChannelMessages.personalReservesSoonExpire.title())

    def getText(self, message, *args):
        return g_settings.htmlTemplates.format('personalReservesSoonExpire', ctx={'boosterCount': html.escape(message.get('values', ''))})
