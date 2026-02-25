# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/wot_plus.py
import typing
from constants import IS_CHINA
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_model import WotPlusPeriodicityEnum
from gui.shared.formatters.date_time import getRegionalDateTime
from gui.shared.gui_items.Vehicle import getUserName
from helpers import dependency
from items.vehicles import getVehicleType
from messenger import g_settings
from messenger.formatters.service_channel import GeneralFormatter
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from renewable_subscription_common.settings_constants import WotPlusTier, PRO_THRESHOLD_DAYS
from skeletons.gui.game_control import IWotPlusController
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from typing import Dict, Tuple

def getVehicleNameFromVehicleCD(message, messageDataKey):
    vehTypeCD = message.data.get(messageDataKey)
    return '' if not vehTypeCD else getUserName(getVehicleType(vehTypeCD))


class WotPlusUnlockedAwardFormatter(GeneralFormatter):

    def __init__(self):
        super(WotPlusUnlockedAwardFormatter, self).__init__('')

    def format(self, message, *args):
        return []


class _WotPlusDateTimeFormatter(GeneralFormatter):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def _getConvertedDateTime(self, dTime):
        return getRegionalDateTime(dTime or 0, DateTimeFormatsEnum.SHORTDATETIME)


class _WotPlusPeriodicityTimeFormatter(_WotPlusDateTimeFormatter):

    def _getPeriodicityMessageText(self, message):
        return R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewalProYearly() if message.get('billingDays', 0) > PRO_THRESHOLD_DAYS else R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewalPro()

    def getText(self, message, *args):
        expiryTime = message.get('expiryTime', 0)
        return backport.text(self._getPeriodicityMessageText(message), time=self._getConvertedDateTime(expiryTime))


class WotPlusUnlockedFormatter(_WotPlusPeriodicityTimeFormatter):

    def __init__(self):
        super(WotPlusUnlockedFormatter, self).__init__('WotPlusUnlockMessage')

    def _getPeriodicityMessageText(self, _):
        return R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal()


class WotPlusCoreUnlockedFormatter(_WotPlusPeriodicityTimeFormatter):

    def __init__(self):
        super(WotPlusCoreUnlockedFormatter, self).__init__('WotPlusCoreUnlockMessage')

    def _getPeriodicityMessageText(self, _):
        return R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal()


class WotPlusProUnlockedFormatter(_WotPlusPeriodicityTimeFormatter):

    def __init__(self):
        super(WotPlusProUnlockedFormatter, self).__init__('WotPlusProUnlockMessage')

    def _getPeriodicityMessageText(self, message):
        return R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfUnlockProYearly() if message.get('periodicity', WotPlusPeriodicityEnum.P6MONTHS) == WotPlusPeriodicityEnum.P12MONTHS else R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfUnlockPro()


class WotPlusRenewedFormatter(_WotPlusPeriodicityTimeFormatter):

    def __init__(self):
        super(WotPlusRenewedFormatter, self).__init__('WotPlusRenewMessage')

    def getTitle(self, message, *args):
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.renewMessage.title())

    def getText(self, message, *args):
        return super(WotPlusRenewedFormatter, self).getText(message.data)

    def _getPeriodicityMessageText(self, _):
        return R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewalChange()


class WotPlusUpgradeFormatter(_WotPlusPeriodicityTimeFormatter):

    def __init__(self):
        super(WotPlusUpgradeFormatter, self).__init__('WotPlusUpgradeMessage')

    def getTitle(self, message, *args):
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.upgradeMessage.title())

    def getText(self, message, *args):
        return super(WotPlusUpgradeFormatter, self).getText(message.data)


class WotPlusExpiredFormatter(_WotPlusDateTimeFormatter):

    def __init__(self):
        super(WotPlusExpiredFormatter, self).__init__('WotPlusExpireMessage')

    def getTitle(self, message, *args):
        previousTier = message.data.get('previousTier', 0)
        timeOfExpiry = message.data.get('expiryTime', 0)
        if not IS_CHINA:
            if previousTier == WotPlusTier.PRO:
                messageTitle = R.strings.messenger.serviceChannelMessages.wotPlus.expireProMessage.title()
            else:
                messageTitle = R.strings.messenger.serviceChannelMessages.wotPlus.expireCoreMessage.title()
        else:
            messageTitle = R.strings.messenger.serviceChannelMessages.wotPlus.expireMessage.title()
        return backport.text(messageTitle, time=self._getConvertedDateTime(timeOfExpiry))


class PassiveXpActivatedFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXpActivatedFormatter, self).__init__('PassiveXPStatusMessage')

    def getText(self, message, *args):
        vehName = getVehicleNameFromVehicleCD(message, 'vehTypeCD')
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isActivated.text(), vehicleName=vehName)


class PassiveXpDeactivatedFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXpDeactivatedFormatter, self).__init__('PassiveXPStatusMessage')

    def getText(self, message, *args):
        vehName = getVehicleNameFromVehicleCD(message, 'vehTypeCD')
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isDeactivated.text(), vehicleName=vehName)


class PassiveXpSwitchedFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXpSwitchedFormatter, self).__init__('PassiveXPSwitchedMessage')

    def getValues(self, message, *args):
        oldVehTypeCD = message.data.get('oldVehTypeCD')
        newVehTypeCD = message.data.get('newVehTypeCD')
        oldVehName = getUserName(getVehicleType(oldVehTypeCD))
        newVehName = getUserName(getVehicleType(newVehTypeCD))
        return {'oldVehName': oldVehName,
         'newVehName': newVehName}


class PassiveXpIncompatibleCrewFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXpIncompatibleCrewFormatter, self).__init__('PassiveXPIncompatibleCrewMessage')

    def getValues(self, message, *args):
        vehName = getVehicleNameFromVehicleCD(message, 'vehTypeCD')
        return {'vehicleName': vehName}


class PassiveXPDeactivateDueToPostProgressionFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXPDeactivateDueToPostProgressionFormatter, self).__init__('PassiveXPDeactivateDueToPostProgression')

    def getValues(self, message, *args):
        vehName = getVehicleNameFromVehicleCD(message, 'vehTypeCD')
        return {'vehicleName': vehName}


class ProBoostActivatedFormatter(GeneralFormatter):

    def __init__(self):
        super(ProBoostActivatedFormatter, self).__init__('WotPlusProBoostActivatedMessage')

    def getValues(self, message, *args):
        return {'vehicleName': getVehicleNameFromVehicleCD(message, 'vehTypeCD'),
         'cooldown': message.data.get('cooldown', 0)}


class ProBoostDeactivatedFormatter(GeneralFormatter):

    def __init__(self):
        super(ProBoostDeactivatedFormatter, self).__init__('WotPlusProBoostDeactivatedMessage')

    def getValues(self, message, *args):
        return {'vehicleName': getVehicleNameFromVehicleCD(message, 'vehTypeCD')}


class ProBoostSwitchFormatter(GeneralFormatter):

    def __init__(self):
        super(ProBoostSwitchFormatter, self).__init__('WotPlusProBoostSwitchMessage')

    def getValues(self, message, *args):
        return {'vehicleNameTo': getVehicleNameFromVehicleCD(message, 'vehTypeCDTo'),
         'vehicleNameFrom': getVehicleNameFromVehicleCD(message, 'vehTypeCDFrom'),
         'cooldown': message.data.get('cooldown', 0)}


class WotPlusSwitchFormatter(ServiceChannelFormatter):

    def format(self, template, *args):
        if template:
            formatted = g_settings.msgTemplates.format(template)
            return [MessageData(formatted, self._getGuiSettings(None, template))]
        else:
            return []
