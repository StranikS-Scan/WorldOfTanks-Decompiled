# Embedded file name: scripts/client/messenger/formatters/__init__.py
from collections import namedtuple
import BigWorld
import time
from time import gmtime
from constants import NC_CONTEXT_ITEM_TYPE
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers import time_utils, i18n
from messenger import g_settings

class TimeFormatter(object):
    _messageDateTimeFormat = {0: 'getMessageEmptyFormatU',
     1: 'getMessageShortDateFormat',
     2: 'getMessageLongTimeFormat',
     3: 'getMessageLongDatetimeFormat'}

    @classmethod
    def getMessageTimeFormat(cls, time):
        method = cls._messageDateTimeFormat[g_settings.userPrefs.datetimeIdx]
        return getattr(cls, method)(time)

    @classmethod
    def getShortDateFormat(cls, time):
        return '{0:>s}'.format(BigWorld.wg_getShortDateFormat(time))

    @classmethod
    def getLongTimeFormat(cls, time):
        return '{0:>s}'.format(BigWorld.wg_getLongTimeFormat(time))

    @classmethod
    def getShortTimeFormat(cls, time):
        return '{0:>s}'.format(BigWorld.wg_getShortTimeFormat(time))

    @classmethod
    def getLongDatetimeFormat(cls, time):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getLongTimeFormat(time))

    @classmethod
    def getShortDatetimeFormat(cls, time):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getShortTimeFormat(time))

    @classmethod
    def getActualMsgTimeStr(cls, timestamp):
        DAY_SECONDS = 86400
        currentTime = time.time()
        if currentTime - timestamp > DAY_SECONDS or gmtime().tm_mday != gmtime(timestamp).tm_mday:
            return TimeFormatter.getShortDatetimeFormat(timestamp)
        else:
            return TimeFormatter.getShortTimeFormat(timestamp)

    @classmethod
    def getMessageEmptyFormatU(cls, _):
        return u''

    @classmethod
    def getMessageShortDateFormat(cls, time):
        return '({0:>s}) '.format(BigWorld.wg_getShortDateFormat(time)).decode('utf-8', 'ignore')

    @classmethod
    def getMessageLongTimeFormat(cls, time):
        return '({0:>s}) '.format(BigWorld.wg_getLongTimeFormat(time)).decode('utf-8', 'ignore')

    @classmethod
    def getMessageLongDatetimeFormat(cls, time):
        return '({0:>s} {1:>s}) '.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getLongTimeFormat(time)).decode('utf-8', 'ignore')


class NCContextItemFormatter(object):
    _formats = {NC_CONTEXT_ITEM_TYPE.GOLD: 'getGoldFormat',
     NC_CONTEXT_ITEM_TYPE.INTEGRAL: 'getIntegralFormat',
     NC_CONTEXT_ITEM_TYPE.FRACTIONAL: 'getFractionalFormat',
     NC_CONTEXT_ITEM_TYPE.NICE_NUMBER: 'getNiceNumberFormat',
     NC_CONTEXT_ITEM_TYPE.SHORT_TIME: 'getShortTimeFormat',
     NC_CONTEXT_ITEM_TYPE.LONG_TIME: 'getLongTimeFormat',
     NC_CONTEXT_ITEM_TYPE.SHORT_DATE: 'getShortDateFormat',
     NC_CONTEXT_ITEM_TYPE.LONG_DATE: 'getLongDateFormat',
     NC_CONTEXT_ITEM_TYPE.DATETIME: 'getDateTimeFormat',
     NC_CONTEXT_ITEM_TYPE.STRING: 'getStringFormat'}

    @classmethod
    def getItemFormat(cls, itemType, itemValue):
        if itemType not in cls._formats:
            LOG_WARNING('Type of item is not found', itemType, itemValue)
            return str(itemValue)
        method = cls._formats[itemType]
        return getattr(cls, method)(itemValue)

    @classmethod
    def getGoldFormat(cls, value):
        return BigWorld.wg_getGoldFormat(value)

    @classmethod
    def getIntegralFormat(cls, value):
        return BigWorld.wg_getIntegralFormat(value)

    @classmethod
    def getFractionalFormat(cls, value):
        return BigWorld.wg_getFractionalFormat(value)

    @classmethod
    def getNiceNumberFormat(cls, value):
        return BigWorld.wg_getNiceNumberFormat(value)

    @classmethod
    def getShortTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getShortTimeFormat)

    @classmethod
    def getLongTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getLongTimeFormat)

    @classmethod
    def getShortDateFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getShortDateFormat)

    @classmethod
    def getLongDateFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getLongDateFormat)

    @classmethod
    def getDateTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, lambda localTime: '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(value), BigWorld.wg_getLongTimeFormat(value)))

    @classmethod
    def getStringFormat(cls, value):
        return i18n.encodeUtf8(value)

    @classmethod
    def _makeLocalTimeString(cls, value, formatter):
        result = time_utils.makeLocalServerTime(value)
        if result:
            result = formatter(value)
        else:
            LOG_WARNING('Timestamp is not defined', value)
            result = ''
        return result


SysMsgExtraData = namedtuple('SysMsgExtraData', 'type data')
from chat_shared import SYS_MESSAGE_TYPE
from messenger.formatters import service_channel as sch_formatters
SCH_SERVER_FORMATTERS_DICT = {SYS_MESSAGE_TYPE.serverReboot.index(): sch_formatters.ServerRebootFormatter(),
 SYS_MESSAGE_TYPE.serverRebootCancelled.index(): sch_formatters.ServerRebootCancelledFormatter(),
 SYS_MESSAGE_TYPE.battleResults.index(): sch_formatters.BattleResultsFormatter(),
 SYS_MESSAGE_TYPE.goldReceived.index(): sch_formatters.GoldReceivedFormatter(),
 SYS_MESSAGE_TYPE.invoiceReceived.index(): sch_formatters.InvoiceReceivedFormatter(),
 SYS_MESSAGE_TYPE.adminTextMessage.index(): sch_formatters.AdminMessageFormatter(),
 SYS_MESSAGE_TYPE.accountTypeChanged.index(): sch_formatters.AccountTypeChangedFormatter(),
 SYS_MESSAGE_TYPE.giftReceived.index(): sch_formatters.GiftReceivedFormatter(),
 SYS_MESSAGE_TYPE.autoMaintenance.index(): sch_formatters.AutoMaintenanceFormatter(),
 SYS_MESSAGE_TYPE.waresSold.index(): sch_formatters.WaresSoldFormatter(),
 SYS_MESSAGE_TYPE.waresBought.index(): sch_formatters.WaresBoughtFormatter(),
 SYS_MESSAGE_TYPE.premiumBought.index(): sch_formatters.PremiumBoughtFormatter(),
 SYS_MESSAGE_TYPE.premiumExtended.index(): sch_formatters.PremiumExtendedFormatter(),
 SYS_MESSAGE_TYPE.premiumExpired.index(): sch_formatters.PremiumExpiredFormatter(),
 SYS_MESSAGE_TYPE.prbArenaFinish.index(): sch_formatters.PrebattleArenaFinishFormatter(),
 SYS_MESSAGE_TYPE.prbKick.index(): sch_formatters.PrebattleKickFormatter(),
 SYS_MESSAGE_TYPE.prbDestruction.index(): sch_formatters.PrebattleDestructionFormatter(),
 SYS_MESSAGE_TYPE.vehicleCamouflageTimedOut.index(): sch_formatters.VehCamouflageTimedOutFormatter(),
 SYS_MESSAGE_TYPE.vehiclePlayerEmblemTimedOut.index(): sch_formatters.VehEmblemTimedOutFormatter(),
 SYS_MESSAGE_TYPE.vehiclePlayerInscriptionTimedOut.index(): sch_formatters.VehInscriptionTimedOutFormatter(),
 SYS_MESSAGE_TYPE.vehTypeLockExpired.index(): sch_formatters.VehicleTypeLockExpired(),
 SYS_MESSAGE_TYPE.serverDowntimeCompensation.index(): sch_formatters.ServerDowntimeCompensation(),
 SYS_MESSAGE_TYPE.achievementReceived.index(): sch_formatters.AchievementFormatter(),
 SYS_MESSAGE_TYPE.converter.index(): sch_formatters.ConverterFormatter(),
 SYS_MESSAGE_TYPE.tokenQuests.index(): sch_formatters.TokenQuestsFormatter(),
 SYS_MESSAGE_TYPE.historicalCostsReserved.index(): sch_formatters.HistoricalCostsReservedFormatter(),
 SYS_MESSAGE_TYPE.notificationsCenter.index(): sch_formatters.NCMessageFormatter(),
 SYS_MESSAGE_TYPE.clanEvent.index(): sch_formatters.ClanMessageFormatter(),
 SYS_MESSAGE_TYPE.fortEvent.index(): sch_formatters.FortMessageFormatter(),
 SYS_MESSAGE_TYPE.fortBattleEnd.index(): sch_formatters.FortBattleResultsFormatter(),
 SYS_MESSAGE_TYPE.fortBattleRoundEnd.index(): sch_formatters.FortBattleRoundEndFormatter(),
 SYS_MESSAGE_TYPE.fortBattleInvite.index(): sch_formatters.FortBattleInviteFormatter(),
 SYS_MESSAGE_TYPE.vehicleRented.index(): sch_formatters.VehicleRentedFormatter(),
 SYS_MESSAGE_TYPE.rentalsExpired.index(): sch_formatters.RentalsExpiredFormatter(),
 SYS_MESSAGE_TYPE.refSystemQuests.index(): sch_formatters.RefSystemQuestsFormatter(),
 SYS_MESSAGE_TYPE.refSystemReferralBoughtVehicle.index(): sch_formatters.RefSystemReferralBoughtVehicleFormatter(),
 SYS_MESSAGE_TYPE.refSystemReferralContributedXP.index(): sch_formatters.RefSystemReferralContributedXPFormatter(),
 SYS_MESSAGE_TYPE.potapovQuestBonus.index(): sch_formatters.PotapovQuestsFormatter()}

class SCH_CLIENT_MSG_TYPE(object):
    SYS_MSG_TYPE, PREMIUM_ACCOUNT_EXPIRY_MSG, AOGAS_NOTIFY_TYPE, ACTION_NOTIFY_TYPE, BATTLE_TUTORIAL_RESULTS_TYPE = range(5)


SCH_CLIENT_FORMATTERS_DICT = {SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE: sch_formatters.ClientSysMessageFormatter(),
 SCH_CLIENT_MSG_TYPE.PREMIUM_ACCOUNT_EXPIRY_MSG: sch_formatters.PremiumAccountExpiryFormatter(),
 SCH_CLIENT_MSG_TYPE.AOGAS_NOTIFY_TYPE: sch_formatters.AOGASNotifyFormatter(),
 SCH_CLIENT_MSG_TYPE.ACTION_NOTIFY_TYPE: sch_formatters.ActionNotificationFormatter(),
 SCH_CLIENT_MSG_TYPE.BATTLE_TUTORIAL_RESULTS_TYPE: sch_formatters.BattleTutorialResultsFormatter()}
