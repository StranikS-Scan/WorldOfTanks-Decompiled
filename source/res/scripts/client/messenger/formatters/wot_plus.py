# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/wot_plus.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getUserName
from items.vehicles import getVehicleType
from messenger.formatters.service_channel import SimpleFormatter
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
