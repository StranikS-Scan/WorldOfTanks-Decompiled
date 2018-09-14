# Embedded file name: scripts/client/messenger/proto/bw_chat2/admin_chat_cmd.py
from debug_utils import LOG_WARNING
from external_strings_utils import isAccountNameValid, normalizedAccountName
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from gui.shared.utils.decorators import ReprInjector
from helpers import i18n
from messenger.m_constants import PROTO_TYPE, MESSENGER_COMMAND_TYPE
from messenger.proto.bw_chat2.errors import _SimpleAdminCommandError, _AdminCommandI18nError
from messenger.proto.entities import _ChatCommand
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from messenger_common_chat2 import ADMIN_CHAT_COMMANDS_BY_NAMES as _COMMANDS_BY_NAMES
from messenger_common_chat2 import messageArgs
from messenger_common_chat2 import MESSENGER_ERRORS as _ERRORS
from messenger.storage import storage_getter
import types

@ReprInjector.simple('id', 'args', 'tail')

class _ParsingResult(object):
    __slots__ = ('id', 'args', 'tail')

    def __init__(self, args = None, tail = None):
        super(_ParsingResult, self).__init__()
        self.id = 0
        self.args = args or messageArgs()
        self.tail = tail or []

    def hasError(self):
        return False

    def getError(self):
        raise RuntimeError, 'That routine can not be invoked in this class'

    def _next(self):
        return self.tail.pop(0)


class _ParsingError(_ParsingResult):
    __slots__ = ('i18nKey',)

    def __init__(self, errorID, args = None, i18nKey = None):
        super(_ParsingError, self).__init__(args)
        self.id = errorID
        self.i18nKey = i18nKey

    def hasError(self):
        return True

    def getError(self):
        if self.i18nKey:
            error = _AdminCommandI18nError(self.i18nKey, self.args)
        else:
            error = _SimpleAdminCommandError(self.id, self.args)
        return error


class _ArgsParser(object):

    def __init__(self, nargs):
        super(_ArgsParser, self).__init__()
        self.nargs = nargs

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def parse_args(self, argsLine):
        args = argsLine.split(None, self.nargs - 1)
        if len(args) != self.nargs:
            if self.nargs > len(args):
                i18nKey = '#chat:errors/toosmallargs'
            else:
                i18nKey = '#chat:errors/toomanyargs'
            return _ParsingError(_ERRORS.GENERIC_ERROR, i18nKey=i18nKey)
        else:
            return _ParsingResult(tail=args)


class _UserBanUnBanArgsParser(_ArgsParser):

    def parse_args(self, argsLine):
        ctx = self.playerCtx
        isGameAdmin = ctx.isGameAdmin()
        isChatAdmin = ctx.isChatAdmin()
        if not isGameAdmin and not isChatAdmin:
            return _ParsingError(_ERRORS.NOT_ALLOWED)
        result = super(_UserBanUnBanArgsParser, self).parse_args(argsLine)
        if result.hasError():
            return result
        banType = result._next()
        if banType == 'game':
            if not isGameAdmin:
                return _ParsingError(_ERRORS.NOT_ALLOWED)
            result.args['int32Arg1'] = 1
        elif banType == 'chat':
            if not isChatAdmin:
                return _ParsingError(_ERRORS.NOT_ALLOWED)
            result.args['int32Arg1'] = 2
        else:
            return _ParsingError(_ERRORS.WRONG_ARGS, {'int32Arg1': banType}, I18N_MESSENGER.CLIENT_ERROR_COMMAND_WRONG_BAN_TYPE)
        name = result._next()
        if name:
            if isAccountNameValid(name):
                result.args['strArg1'] = normalizedAccountName(name)
            else:
                return _ParsingError(_ERRORS.WRONG_ARGS, {'strArg1': name}, I18N_MESSENGER.CLIENT_ERROR_COMMAND_WRONG_PLAYER_NAME)
        else:
            result = _ParsingError(_ERRORS.WRONG_ARGS)
        return result


_MAX_BAN_TIME = 5256000
_TIME_LETTER_TO_MULTIPLIER = {'h': 60,
 'd': 1440,
 'w': 10080,
 'm': 43200,
 'y': 525600}

class _UserBanArgsParser(_UserBanUnBanArgsParser):

    def __init__(self):
        super(_UserBanUnBanArgsParser, self).__init__(4)

    def parse_args(self, argsLine):
        result = super(_UserBanArgsParser, self).parse_args(argsLine)
        if result.hasError():
            return result
        else:
            banPeriod = result._next()
            if banPeriod and type(banPeriod) in types.StringTypes:
                amount, multiplier, litter = (None, 1, None)
                if banPeriod.isdigit():
                    amount = long(banPeriod)
                else:
                    amountStr = banPeriod[:-1]
                    litter = banPeriod[-1]
                    if amountStr.isdigit():
                        amount = long(amountStr)
                if amount is None:
                    return _ParsingError(_ERRORS.WRONG_ARGS, {'int64Arg1': banPeriod}, I18N_MESSENGER.CLIENT_ERROR_COMMAND_WRONG_BAN_PERIOD)
                if litter is not None:
                    if litter in _TIME_LETTER_TO_MULTIPLIER:
                        multiplier = _TIME_LETTER_TO_MULTIPLIER[litter]
                    else:
                        return _ParsingError(_ERRORS.WRONG_ARGS, {'int64Arg1': banPeriod}, I18N_MESSENGER.CLIENT_ERROR_COMMAND_WRONG_BAN_PERIOD)
                result.args['int64Arg1'] = min(amount * multiplier, _MAX_BAN_TIME)
            else:
                return _ParsingError(_ERRORS.WRONG_ARGS)
            reason = result._next()
            if reason:
                result.args['strArg2'] = reason
            else:
                return _ParsingError(_ERRORS.WRONG_ARGS)
            return result


class _UserUnBanArgsParser(_UserBanUnBanArgsParser):

    def __init__(self):
        super(_UserBanUnBanArgsParser, self).__init__(2)


_AVAILABLE_PARSERS = {'USERBAN': _UserBanArgsParser,
 'USERUNBAN': _UserUnBanArgsParser}

def getCommandFromLine(text):
    cmdName, argsLine = ('', '')
    if text and text[0] == '/':
        cmdLine = text[1:].split(None, 1)
        if cmdLine:
            cmdName = cmdLine.pop(0)
            if cmdName not in _COMMANDS_BY_NAMES:
                cmdName, argsLine = ('', '')
        if cmdLine:
            argsLine = cmdLine.pop(0)
    return (cmdName, argsLine)


def parseCommandLine(text):
    cmdName, argsLine = getCommandFromLine(text)
    if cmdName:
        if cmdName in _AVAILABLE_PARSERS:
            result = _AVAILABLE_PARSERS[cmdName]().parse_args(argsLine)
            if not result.hasError():
                result.id = _COMMANDS_BY_NAMES[cmdName].id
        else:
            result = _ParsingError(_ERRORS.GENERIC_ERROR, {'strArg1': cmdName}, I18N_MESSENGER.CLIENT_ERROR_COMMAND_NOT_SUPPORTED)
    else:
        result = None
    return result


class _AdminChatCommandDecorator(_ChatCommand):
    __slots__ = ('_actionID',)

    def __init__(self, actionID, protoData, clientID = 0):
        super(_AdminChatCommandDecorator, self).__init__(protoData, clientID)
        self._actionID = actionID

    def getID(self):
        return self._actionID

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def getCommandType(self):
        return MESSENGER_COMMAND_TYPE.ADMIN

    def getCommandText(self):
        cmd = _ACTIONS.adminChatCommandFromActionID(self._actionID)
        if not cmd:
            LOG_WARNING('Command is not found', self._actionID)
            return str(self._actionID)
        key = I18N_MESSENGER.command_success(cmd.name)
        if key:
            msg = i18n.makeString(key, **self._protoData)
        else:
            msg = cmd.name
        return msg


def makeDecorator(result, clientID):
    return _AdminChatCommandDecorator(result.id, result.args, clientID)
