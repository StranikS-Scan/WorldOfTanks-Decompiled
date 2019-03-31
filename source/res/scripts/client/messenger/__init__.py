# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/__init__.py
# Compiled at: 2011-11-16 16:19:41
from debug_utils import LOG_ERROR
import BigWorld
from constants import CHAT_MESSAGE_MAX_LENGTH
import types
MESSENGER_XML_FILE = 'messenger'
MESSENGER_I18N_FILE = 'messenger'
MESSENGER_XML_FILE_PATH = 'gui/%s.xml' % MESSENGER_XML_FILE
MESSENGER_OLDICT_FILE_PATH = 'text/messenger_oldictionary.xml'
MESSAGE_MAX_LENGTH = CHAT_MESSAGE_MAX_LENGTH
MESSAGE_FLOOD_COOLDOWN = 20
BREAKERS_MAX_LENGTH = 1
VISIBLE_MESSAGE_MAX_LENGTH = 50
INVITE_COMMENT_MAX_LENGTH = 400
MESSAGE_DATETIME_FORMAT_DICT = {0: lambda time: u'',
 1: lambda time: '({0:>s})'.format(BigWorld.wg_getShortDateFormat(time)).decode('utf-8', 'ignore'),
 2: lambda time: '({0:>s})'.format(BigWorld.wg_getLongTimeFormat(time)).decode('utf-8', 'ignore'),
 3: lambda time: '({0:>s} {1:>s})'.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getLongTimeFormat(time)).decode('utf-8', 'ignore')}
DEFAULT_MESSAGE_DATETIME_FORMAT_INDEX = 2
DEFAULT_MESSAGE_DATETIME_FORMAT = MESSAGE_DATETIME_FORMAT_DICT[DEFAULT_MESSAGE_DATETIME_FORMAT_INDEX]

def getLongDatetimeFormat(time):
    return BigWorld.wg_getLongDateFormat(time) + ' ' + BigWorld.wg_getLongTimeFormat(time)


LOBBY_MESSAGE_FORMAT = '<font color="#000000">%s</font>&nbsp;<font color="#000000">%s&nbsp;</font><font color="#000000">%s</font>'

class LAZY_CHANNELS(object):
    COMMON = (1, '#chat:channels/common', 1)
    COMPANIES = (2, '#chat:channels/company', 2)
    SPECIAL_BATTLES = (3, '#chat:channels/special_battles', 3)
    ALL = (COMMON, COMPANIES, SPECIAL_BATTLES)
    INDICES = tuple((x[1] for x in ALL))
    CLIENT_IDXS = tuple((x[0] for x in ALL))
    ORDERS = dict(((x[0], x[2]) for x in ALL))


BATTLE_MESSAGE_FORMAT = "<font color='#%s'>%s&nbsp;:&nbsp;</font><font color='#%s'>%s</font>"
BATTLE_DEFAULT_MESSAGE_LIFE_TIME = 5
SCH_MSGS_MAX_LENGTH = 250
SCH_DEFAULT_POP_UP_MSG_LIFE_TIME = 5.0
SCH_DEFAULT_POP_UP_MSG_STACK_LENGTH = 5
INVITES_I18N_FILE = 'invites'
from chat_shared import getOperationCooldownPeriod, isOperationInCooldown, CHAT_COMMANDS
import chat_shared
from helpers import i18n

def isBroadcatInCooldown():
    return isOperationInCooldown(chat_shared.g_chatCooldownData, CHAT_COMMANDS.broadcast, update=False)


BROADCAST_COOL_DOWN_MESSAGE = i18n.makeString('#%s:client/error/broadcastInCooldown' % MESSENGER_I18N_FILE, getOperationCooldownPeriod(CHAT_COMMANDS.broadcast))

def isOperationInCooldownEx(operationName):
    operation = CHAT_COMMANDS.lookup(operationName)
    result = False
    if operation is not None:
        result = isOperationInCooldown(chat_shared.g_chatCooldownData, operation, update=False)
    else:
        LOG_ERROR("Can't find operation = %s in chat_shared.CHAT_COMMANDS" % operationName)
    return result


def getOperationCooldownPeriodEx(operationName):
    command = CHAT_COMMANDS.lookup(operationName)
    result = -1
    if command is not None:
        result = getOperationCooldownPeriod(command)
    else:
        LOG_ERROR("Can't find operation = %s in chat_shared.CHAT_COMMANDS" % operationName)
    return result


_battleChatShortcuts = (CHAT_COMMANDS.HELPME.name(),
 CHAT_COMMANDS.FOLLOWME.name(),
 CHAT_COMMANDS.ATTACK.name(),
 CHAT_COMMANDS.BACKTOBASE.name(),
 CHAT_COMMANDS.POSITIVE.name(),
 CHAT_COMMANDS.NEGATIVE.name(),
 CHAT_COMMANDS.ATTENTIONTOCELL.name(),
 CHAT_COMMANDS.ATTACKENEMY.name())
_moderationChatCommands = (CHAT_COMMANDS.CHGCHNLNAME.name(),
 CHAT_COMMANDS.GREETING.name(),
 CHAT_COMMANDS.BAN.name(),
 CHAT_COMMANDS.UNBAN.name(),
 CHAT_COMMANDS.ADDMODERATOR.name(),
 CHAT_COMMANDS.DELMODERATOR.name())

def getOperationInCooldownMsg(operation, period):
    if operation in _battleChatShortcuts:
        command = CHAT_COMMANDS.lookup(operation)
        args = []
        for index in range(command.argsCnt):
            key = '#%s:command/%s/arg%d' % (MESSENGER_I18N_FILE, operation, index)
            args.append(i18n.makeString(key))

        operationName = i18n.makeString(command.msgText, *args)
    elif operation in _moderationChatCommands:
        operationName = operation
    else:
        operationKey = '#%s:command/%s' % (MESSENGER_I18N_FILE, operation)
        operationName = i18n.makeString(operationKey)
        if operationName.startswith('command'):
            operationName = operation
    if period > 0:
        message = i18n.makeString('#%s:client/error/commandInCooldown/limited' % MESSENGER_I18N_FILE, operationName, period)
    else:
        message = i18n.makeString('#%s:client/error/commandInCooldown/unlimited' % MESSENGER_I18N_FILE, operationName)
    return message


from messenger.MessengerSettings import MessengerSettings
g_settings = MessengerSettings(MESSENGER_XML_FILE_PATH)
g_settings.readXML()
from messenger.dictionaries import ObsceneLanguageDictionary
g_olDictionary = ObsceneLanguageDictionary.load(MESSENGER_OLDICT_FILE_PATH)

def passCensor(text):
    if text is None:
        return u''
    else:
        if type(text) is not types.UnicodeType:
            text = unicode(text, 'utf-8')
        if g_settings.userPreferences['enableOlFilter']:
            return g_olDictionary.searchAndReplace(text)
        return text


from chat_shared import SYS_MESSAGE_TYPE
sch_formatters = __import__('messenger.service_channel_formatters', globals={}, locals={}, fromlist=['ServerRebootFormatter',
 'ServerRebootCancelledFormatter',
 'BattleResultsFormatter',
 'GoldReceivedFormatter',
 'InvoiceReceivedFormatter',
 'AdminMessageFormatter',
 'AccountTypeChangedFormatter',
 'GiftReceivedFormatterClientSysMessageFormatter',
 'PremiumAccountExpiryFormatter',
 'AOGASNotifyFormatter',
 'WaresSoldFormatter',
 'WaresBoughtFormatter',
 'PremiumBoughtFormatter',
 'PremiumExtendedFormatterPremiumExpiredFormatter',
 'PrebattleArenaFinishFormatter',
 'PrebattleKickFormatter',
 'PrebattleDestructionFormatter',
 'VehCamouflageTimedOutFormatter',
 'VehicleTypeLockExpired'])
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
 SYS_MESSAGE_TYPE.vehTypeLockExpired.index(): sch_formatters.VehicleTypeLockExpired()}

class SCH_CLIENT_MSG_TYPE(object):
    SYS_MSG_TYPE, PREMIUM_ACCOUNT_EXPIRY_MSG, AOGAS_NOTIFY_TYPE = range(3)


SCH_CLIENT_FORMATTERS_DICT = {SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE: sch_formatters.ClientSysMessageFormatter(),
 SCH_CLIENT_MSG_TYPE.PREMIUM_ACCOUNT_EXPIRY_MSG: sch_formatters.PremiumAccountExpiryFormatter(),
 SCH_CLIENT_MSG_TYPE.AOGAS_NOTIFY_TYPE: sch_formatters.AOGASNotifyFormatter()}
