# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/wot_plus.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum
from gui.shared.formatters.date_time import getRegionalDateTime
from gui.shared.gui_items.Vehicle import getUserName
from items.vehicles import getVehicleType
from messenger.formatters.service_channel import GeneralFormatter
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from typing import Dict, Tuple

class WotPlusUnlockedAwardFormatter(GeneralFormatter):

    def __init__(self):
        super(WotPlusUnlockedAwardFormatter, self).__init__('')

    def format(self, message, *args):
        return []


class _WotPlusDateTimeFormatter(GeneralFormatter):

    def _getConvertedDateTime(self, dTime):
        return getRegionalDateTime(dTime or 0, DateTimeFormatsEnum.SHORTDATE)


class WotPlusUnlockedFormatter(_WotPlusDateTimeFormatter):

    def __init__(self):
        super(WotPlusUnlockedFormatter, self).__init__('WotPlusUnlockMessage')

    def getText(self, message, *args):
        expiryTime = message.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal(), time=self._getConvertedDateTime(expiryTime))


class WotPlusRenewedFormatter(_WotPlusDateTimeFormatter):

    def __init__(self):
        super(WotPlusRenewedFormatter, self).__init__('WotPlusRenewMessage')

    def getTitle(self, message, *args):
        renewTime = message.data.get('renewTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.renewMessage.title(), time=self._getConvertedDateTime(renewTime))

    def getText(self, message, *args):
        expiryTime = message.data.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.nextDateOfRenewal(), time=self._getConvertedDateTime(expiryTime))


class WotPlusExpiredFormatter(_WotPlusDateTimeFormatter):

    def __init__(self):
        super(WotPlusExpiredFormatter, self).__init__('WotPlusExpireMessage')

    def getTitle(self, message, *args):
        timeOfExpiry = message.data.get('expiryTime', 0)
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.expireMessage.title(), time=self._getConvertedDateTime(timeOfExpiry))


class PassiveXpActivatedFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXpActivatedFormatter, self).__init__('PassiveXPStatusMessage')

    def getText(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isActivated.text(), vehicleName=vehName)


class PassiveXpDeactivatedFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXpDeactivatedFormatter, self).__init__('PassiveXPStatusMessage')

    def getText(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
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
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return {'vehicleName': vehName}


class PassiveXPDeactivateDueToPostProgressionFormatter(GeneralFormatter):

    def __init__(self):
        super(PassiveXPDeactivateDueToPostProgressionFormatter, self).__init__('PassiveXPDeactivateDueToPostProgression')

    def getValues(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD')
        vehName = getUserName(getVehicleType(vehTypeCD))
        return {'vehicleName': vehName}


class WotPlusSwitchFormatter(ServiceChannelFormatter):

    def format(self, template, *args):
        if template:
            formatted = g_settings.msgTemplates.format(template)
            return [MessageData(formatted, self._getGuiSettings(None, template))]
        else:
            return []
