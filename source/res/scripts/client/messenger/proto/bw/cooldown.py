# Embedded file name: scripts/client/messenger/proto/bw/cooldown.py
from chat_shared import isOperationInCooldown, CHAT_COMMANDS, getOperationCooldownPeriod
import chat_shared
from debug_utils import LOG_ERROR
from helpers import i18n
from messenger.m_constants import MESSENGER_I18N_FILE
BROADCAST_COOL_DOWN_MESSAGE = i18n.makeString('#%s:client/error/broadcastInCooldown' % MESSENGER_I18N_FILE, getOperationCooldownPeriod(CHAT_COMMANDS.broadcast))
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


def getOperationInCooldownMsg(operation, period, params = None):
    if operation in _battleChatShortcuts:
        command = CHAT_COMMANDS.lookup(operation)
        args = []
        for index in range(command.argsCnt):
            key = '#%s:command/%s/arg%d' % (MESSENGER_I18N_FILE, operation, index)
            args.append(i18n.makeString(key))

        operationName = i18n.makeString(command.msgText, *args)
    elif operation in _moderationChatCommands:
        operationName = operation
    elif operation in _reloadingChatCommandsWithParams:
        params = {}
        command = CHAT_COMMANDS.lookup(operation)
        for key in _reloadingChatCommandsWithParams[operation]:
            value = i18n.makeString('#%s:command/%s/%s' % (MESSENGER_I18N_FILE, operation, key))
            params.update({key: value})

        operationName = i18n.makeString(command.msgText, **params)
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
