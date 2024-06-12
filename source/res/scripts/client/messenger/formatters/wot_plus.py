# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/wot_plus.py
import datetime
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getUserName
from items.vehicles import getVehicleType
from messenger.formatters.service_channel import SimpleFormatter, ServiceChannelFormatter
from skeletons.gui.game_control import IWotPlusController
from helpers import dependency, time_utils
from messenger import g_settings
from adisp import adisp_async, adisp_process
from messenger.formatters import TimeFormatter
from renewable_subscription_common.settings_constants import WotPlusState
from messenger.formatters.service_channel_helpers import MessageData
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from typing import Dict, Tuple

class IStandardMessageFormatter(SimpleFormatter):

    def getCtx(self, message, *args):
        ctx = {}
        title = self.getTitle(message, *args)
        text = self.getText(message, *args)
        values = self.getValues(message, *args) or {}
        if title:
            ctx['title'] = title
        if text:
            ctx['text'] = text
        ctx.update(values)
        return ctx

    def getTitle(self, message, *args):
        return None

    def getText(self, message, *args):
        return None

    def getValues(self, message, *args):
        return None


class PremiumSubsAsyncFormatter(ServiceChannelFormatter):
    subscriptionCtrl = dependency.descriptor(IWotPlusController)

    def isAsync(self):
        return True

    def getConvertedDateTime(self, dTime):
        return TimeFormatter.getShortDatetimeFormat(time_utils.makeLocalServerTime(dTime))

    @adisp_async
    @adisp_process
    def format(self, message, callback, *args):
        yield self.subscriptionCtrl.synchronize()
        callback(self._format(message))

    def _format(self, message):
        return []


class WotPlusUnlockedFormatter(PremiumSubsAsyncFormatter):
    subscriptionCtrl = dependency.descriptor(IWotPlusController)

    def isAsync(self):
        return True

    def getConvertedDateTime(self, dTime):
        return TimeFormatter.getShortDatetimeFormat(time_utils.makeLocalServerTime(dTime))

    def _format(self, message):
        expiryTime = message.data.get('expiryTime', 0)
        title = backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.unlockMessage.title())
        text = backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal(), time=self.getConvertedDateTime(expiryTime))
        if self.subscriptionCtrl.getState() == WotPlusState.TRIAL:
            title = backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.unlockTrialMessage.title())
            text = backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.unlockTrialMessage.text(), time=self.getConvertedDateTime(expiryTime))
        formatted = g_settings.msgTemplates.format('WotPlusUnlockMessage', ctx={'title': title,
         'text': text})
        return [MessageData(formatted, self._getGuiSettings(message, 'WotPlusUnlockMessage'))]


class PremiumSubsUpdatedFormatter(PremiumSubsAsyncFormatter):
    _MSG_TEMPLATE = 'InformationHeaderSysMessage'

    def _format(self, message):
        expiryTime = message.data.get('expiryTime', 0)
        oldExpiryTime = message.data.get('oldExpiryTime', 0)
        if self.subscriptionCtrl.getState() == WotPlusState.TRIAL:
            days = datetime.timedelta(seconds=max(expiryTime - oldExpiryTime, 0)).days
            title = backport.text(R.strings.messenger.serviceChannelMessages.premiumSubs.premiumSubsTrialUpdated.title(), days=days)
            text = backport.text(R.strings.messenger.serviceChannelMessages.premiumSubs.premiumSubsTrialUpdated.body(), days=days)
            formatted = g_settings.msgTemplates.format(self._MSG_TEMPLATE, ctx={'header': title,
             'text': text})
            return [MessageData(formatted, self._getGuiSettings(message, self._MSG_TEMPLATE))]
        return []


class PremiumSubsReceivedFromInvoiceFormatter(ServiceChannelFormatter):
    _MSG_TEMPLATE = 'InformationHeaderSysMessage'
    __subscriptionCtrl = dependency.descriptor(IWotPlusController)

    def format(self, message, *args):
        days = message.data.get('savedData', {}).get('premium_subs_days', 0)
        if self.__subscriptionCtrl.getState() in (WotPlusState.ACTIVE, WotPlusState.CANCELLED):
            title = backport.text(R.strings.messenger.serviceChannelMessages.premiumSubs.premiumSubsInvoiceReceived.title(), days=days)
            text = backport.text(R.strings.messenger.serviceChannelMessages.premiumSubs.premiumSubsInvoiceReceived.body(), days=days)
            formatted = g_settings.msgTemplates.format(self._MSG_TEMPLATE, ctx={'header': title,
             'text': text})
            return [MessageData(formatted, self._getGuiSettings(message, self._MSG_TEMPLATE))]
        return []


class WotPlusExpiredFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(WotPlusExpiredFormatter, self).__init__('WotPlusExpireMessage')

    def getTitle(self, message, *args):
        timeOfExpiry = message.data.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.expireMessage.title(), time=self.getConvertedDateTime(timeOfExpiry))


class PassiveXpActivatedFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(PassiveXpActivatedFormatter, self).__init__('PassiveXPStatusMessage')

    def getText(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isActivated.text(), vehicleName=vehName)


class PassiveXpDeactivatedFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(PassiveXpDeactivatedFormatter, self).__init__('PassiveXPStatusMessage')

    def getText(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isDeactivated.text(), vehicleName=vehName)


class PassiveXpSwitchedFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(PassiveXpSwitchedFormatter, self).__init__('PassiveXPSwitchedMessage')

    def getValues(self, message, *args):
        oldVehTypeCD = message.data.get('oldVehTypeCD')
        newVehTypeCD = message.data.get('newVehTypeCD')
        oldVehName = getUserName(getVehicleType(oldVehTypeCD))
        newVehName = getUserName(getVehicleType(newVehTypeCD))
        return {'oldVehName': oldVehName,
         'newVehName': newVehName}


class PassiveXpIncompatibleCrewFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(PassiveXpIncompatibleCrewFormatter, self).__init__('PassiveXPIncompatibleCrewMessage')

    def getValues(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return {'vehicleName': vehName}


class PassiveXpInvalidCrewFormatter(IStandardMessageFormatter):

    def __init__(self):
        super(PassiveXpInvalidCrewFormatter, self).__init__('PassiveXpInvalidCrewMessage')

    def getValues(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return {'vehicleName': vehName}
