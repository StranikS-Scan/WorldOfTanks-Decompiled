# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw/cooldown.py
from chat_shared import isOperationInCooldown, CHAT_COMMANDS, getOperationCooldownPeriod
import chat_shared
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from debug_utils import LOG_ERROR
from helpers import i18n, html
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.m_constants import MESSENGER_I18N_FILE

def getBroadcastCoolDownMessage():
    return getBroadcastIsInCoolDownMessage(getOperationCooldownPeriod(CHAT_COMMANDS.broadcast))


_battleChatShortcuts = (BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_UNAVAILABLE,
 BATTLE_CHAT_COMMAND_NAMES.REPLY,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTIONTOOBJECTIVE_ATK,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTIONTOOBJECTIVE_DEF,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
 BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_SAVE_TANKS_ATK,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_SAVE_TANKS_DEF,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_TIME_ATK,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_TIME_DEF,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_HQ_ATK,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_HQ_DEF,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_WEST,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_CENTER,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_EAST)
_reloadingChatCommandsWithParams = {BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN: ('rTime',),
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_CASSETE: ('rTime', 'ammoQuantityLeft'),
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY_CASSETE: ('ammoInCassete',)}
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


def getOperationInCooldownMsg(operation, period, params=None):
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
