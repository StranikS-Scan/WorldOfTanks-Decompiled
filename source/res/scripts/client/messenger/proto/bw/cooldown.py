# Embedded file name: scripts/client/messenger/proto/bw/cooldown.py
from chat_shared import isOperationInCooldown, CHAT_COMMANDS, getOperationCooldownPeriod
import chat_shared
from debug_utils import LOG_ERROR
from helpers import i18n, html
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.m_constants import MESSENGER_I18N_FILE
BROADCAST_COOL_DOWN_MESSAGE = getBroadcastIsInCoolDownMessage(getOperationCooldownPeriod(CHAT_COMMANDS.broadcast))
_battleChatShortcuts = (CHAT_COMMANDS.HELPME.name(),
 CHAT_COMMANDS.FOLLOWME.name(),
 CHAT_COMMANDS.ATTACK.name(),
 CHAT_COMMANDS.BACKTOBASE.name(),
 CHAT_COMMANDS.POSITIVE.name(),
 CHAT_COMMANDS.NEGATIVE.name(),
 CHAT_COMMANDS.ATTENTIONTOCELL.name(),
 CHAT_COMMANDS.ATTACKENEMY.name(),
 CHAT_COMMANDS.TURNBACK.name(),
 CHAT_COMMANDS.HELPMEEX.name(),
 CHAT_COMMANDS.SUPPORTMEWITHFIRE.name(),
 CHAT_COMMANDS.RELOADING_READY.name(),
 CHAT_COMMANDS.RELOADING_UNAVAILABLE.name(),
 CHAT_COMMANDS.STOP.name())
_reloadingChatCommandsWithParams = {CHAT_COMMANDS.RELOADINGGUN.name(): ('rTime',),
 CHAT_COMMANDS.RELOADING_CASSETE.name(): ('rTime', 'ammoQuantityLeft'),
 CHAT_COMMANDS.RELOADING_READY_CASSETE.name(): ('ammoInCassete',)}
_moderationChatCommands = (CHAT_COMMANDS.CHGCHNLNAME.name(),
 CHAT_COMMANDS.GREETING.name(),
 CHAT_COMMANDS.BAN.name(),
 CHAT_COMMANDS.UNBAN.name(),
 CHAT_COMMANDS.ADDMODERATOR.name(),
 CHAT_COMMANDS.DELMODERATOR.name())

def isBroadcatInCooldown():
    return isOperationInCooldown(chat_shared.g_chatCooldownData, CHAT_COMMANDS.broadcast, update=False)


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


def getBattleCommandExample(msgText):
    result = msgText.split('/', 1)
    if len(result) > 1:
        i18nKey = I18N_INGAME_GUI.chat_example(result[1])
        if i18nKey is not None:
            i18nName = html.escape(i18n.makeString(i18nKey))
        else:
            i18nName = msgText
    else:
        i18nName = i18n.makeString(msgText)
    return i18nName


def getOperationInCooldownMsg(operation, period, params = None):
    if operation in _battleChatShortcuts:
        command = CHAT_COMMANDS.lookup(operation)
        operationName = getBattleCommandExample(command.msgText)
    elif operation in _moderationChatCommands:
        operationName = operation
    elif operation in _reloadingChatCommandsWithParams:
        command = CHAT_COMMANDS.lookup(operation)
        operationName = getBattleCommandExample(command.msgText)
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
