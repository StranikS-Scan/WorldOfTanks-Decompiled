# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/wot_plus.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getUserName
from helpers import time_utils
from items.vehicles import getVehicleType
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage

class SimpleFormatter(ServiceChannelFormatter):

    def __init__(self, templateName):
        self._template = templateName

    def format(self, message, *args):
        if message is None:
            return []
        else:
            formatted = g_settings.msgTemplates.format(self._template, ctx=self.getCtx(message, *args))
            return [MessageData(formatted, self._getGuiSettings(message, self._template))]

    def getCtx(self, message, *args):
        return None

    def getConvertedDateTime(self, time):
        return TimeFormatter.getShortDatetimeFormat(time_utils.makeLocalServerTime(time))


class IStandardMessageFormatter(SimpleFormatter):

    def getCtx(self, message, *args):
        ctx = {}
        title = self.getTitle(message, *args)
        text = self.getText(message, *args)
        if title:
            ctx['title'] = title
        if text:
            ctx['text'] = text
        return ctx

    def getTitle(self, message, *args):
        return None

    def getText(self, message, *args):
        return None


class WotPlusUnlockedFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(WotPlusUnlockedFormatter, self).__init__('WotPlusUnlockMessage')

    def getTitle(self, message, *args):
        startTime = message.data.get('startTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.unlockMessage.title(), startTime=self.getConvertedDateTime(startTime))

    def getText(self, message, *args):
        expiryTime = message.data.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal(), time=self.getConvertedDateTime(expiryTime))


class WotPlusRenewedFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(WotPlusRenewedFormatter, self).__init__('WotPlusRenewMessage')

    def getTitle(self, message, *args):
        renewTime = message.data.get('renewTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.renewMessage.title(), time=self.getConvertedDateTime(renewTime))

    def getText(self, message, *args):
        expiryTime = message.data.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal(), time=self.getConvertedDateTime(expiryTime))


class WotPlusExpiredFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(WotPlusExpiredFormatter, self).__init__('WotPlusExpireMessage')

    def getTitle(self, message, *args):
        timeOfExpiry = message.data.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.expireMessage.title(), time=self.getConvertedDateTime(timeOfExpiry))


class RentEnd(IStandardMessageFormatter):

    def __init__(self):
        super(RentEnd, self).__init__('WotPlusRentEndMessage')

    def getTitle(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.rental.end.title(), vehicleName=vehName)
