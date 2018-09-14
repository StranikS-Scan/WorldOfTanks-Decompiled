# Embedded file name: scripts/client/messenger/proto/bw_chat2/errors.py
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from helpers import i18n, html
from helpers.time_utils import makeLocalServerTime
from messenger.proto.interfaces import IChatError
from messenger.proto.shared_errors import ChatCoolDownError, ClientActionError, I18nActionID, I18nErrorID, ChatBanError
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from messenger_common_chat2 import MESSENGER_ERRORS as _ERRORS
from messenger_common_chat2 import MESSENGER_LIMITS as _LIMITS

def getChatActionName(actionID):
    actionName = _ACTIONS.getActionName(actionID)
    i18nKey = I18N_MESSENGER.chat_action(actionName)
    if i18nKey is not None:
        i18nName = i18n.makeString(i18nKey)
    else:
        i18nName = actionName
    return i18nName


def getBattleCommandExample(msgText):
    i18nKey = I18N_INGAME_GUI.chat_example(msgText)
    if i18nKey is not None:
        i18nName = html.escape(i18n.makeString(i18nKey))
    else:
        i18nName = msgText
    return i18nName


def getChatErrorMessage(errorID, kwargs):
    errorName = _ERRORS.getErrorName(errorID)
    i18nKey = I18N_MESSENGER.chat_error(errorName)
    if i18nKey is not None:
        msg = i18n.makeString(i18nKey, **kwargs)
    else:
        msg = '{0}\\{1}'.format(errorName, kwargs)
    return msg


class _BWChat2I18nError(I18nErrorID):

    def getName(self):
        return _ERRORS.getErrorName(self.errorID)

    def getI18nKey(self):
        return I18N_MESSENGER.chat_error(self.getName())


class _BWChat2I18nAction(I18nActionID):

    def getName(self):
        return _ACTIONS.getActionName(self.actionID)

    def getI18nName(self):
        return getChatActionName(self.actionID)


class _ActionCoolDownError(ChatCoolDownError):

    def createAction(self, actionID):
        return _BWChat2I18nAction(actionID)


class _BattleCommandError(IChatError):
    __slots__ = ('_example', '_coolDown')

    def __init__(self, command):
        super(_BattleCommandError, self).__init__()
        self._example = getBattleCommandExample(command.msgText)
        self._coolDown = command.cooldownPeriod


class _BattleCommandCoolDownError(_BattleCommandError):

    def __init__(self, command):
        super(_BattleCommandCoolDownError, self).__init__(command)
        self._coolDown = command.cooldownPeriod

    def getMessage(self):
        return i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_COMMANDINCOOLDOWN_LIMITED, self._example, self._coolDown)


class _BattleCommandGenericError(_BattleCommandError):

    def getMessage(self):
        return i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_COMMAND_GENERIC_ERROR, strArg1=self._example)


class _SimpleActionError(ClientActionError):

    def createError(self, errorID):
        return _BWChat2I18nError(errorID)

    def createAction(self, actionID):
        return _BWChat2I18nAction(actionID)


class _AdminCommandError(IChatError):
    __slots__ = ('_error',)

    def __init__(self, error):
        super(_AdminCommandError, self).__init__()
        self._error = error

    def getMessage(self):
        return i18n.makeString(I18N_MESSENGER.SERVER_ERRORS_CHATCOMMANDERROR_MESSAGE, error=self._error)


class _SimpleAdminCommandError(_AdminCommandError):

    def __init__(self, errorID, kwargs = None):
        super(_SimpleAdminCommandError, self).__init__(getChatErrorMessage(errorID, kwargs or {'actionName': i18n.makeString(I18N_MESSENGER.CUSTOM_CLIENT_ACTION_ADMIN_CHAT_COMMAND)}))


class _AdminCommandI18nError(_AdminCommandError):

    def __init__(self, keys, kwargs):
        super(_AdminCommandI18nError, self).__init__(i18n.makeString(keys, **kwargs))


class _AdminCommandCoolDownError(_AdminCommandError):

    def __init__(self):
        super(_AdminCommandCoolDownError, self).__init__(i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_COMMAND_IN_COOLDOWN_WO_NAME, floatArg1=_LIMITS.ADMIN_COMMANDS_FROM_CLIENT_COOLDOWN_SEC))


def createCoolDownError(actionID):
    command = _ACTIONS.adminChatCommandFromActionID(actionID)
    if command:
        return _AdminCommandCoolDownError()
    else:
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command:
            return _BattleCommandCoolDownError(command)
        if _ACTIONS.isRateLimitedBroadcastFromClient(actionID):
            coolDown = _LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC
        elif actionID == _ACTIONS.FIND_USERS_BY_NAME:
            coolDown = _LIMITS.FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC
        elif actionID == _ACTIONS.GET_VOIP_CREDENTIALS:
            coolDown = _LIMITS.VOIP_CREDENTIALS_REQUEST_COOLDOWN_SEC
        else:
            coolDown = None
        return _ActionCoolDownError(actionID, coolDown)


def createBroadcastError(args, broadcastID):
    errorID = args['int32Arg1']
    if not _ACTIONS.isRateLimitedBroadcastFromClient(broadcastID):
        raise AssertionError
        error = errorID == _ERRORS.IN_CHAT_BAN and ChatBanError(makeLocalServerTime(args['floatArg1']), args['strArg1'])
    elif errorID == _ERRORS.IN_COOLDOWN:
        error = _ActionCoolDownError(broadcastID, _LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC)
    else:
        error = _SimpleActionError(broadcastID, errorID)
    return error


def createAdminCommandError(args):
    errorID = args['int32Arg1']
    if errorID == _ERRORS.IN_COOLDOWN:
        error = _AdminCommandCoolDownError()
    else:
        error = _SimpleAdminCommandError(errorID)
    return error


def createBattleCommandError(args, command):
    errorID = args['int32Arg1']
    error = None
    if errorID == _ERRORS.IN_COOLDOWN:
        error = _BattleCommandCoolDownError(command)
    elif errorID == _ERRORS.GENERIC_ERROR:
        error = _BattleCommandGenericError(command)
    return error


def createVOIPError(args, actionID):
    errorID = args['int32Arg1']
    error, logOnly = None, False
    if actionID == _ACTIONS.GET_VOIP_CREDENTIALS:
        if errorID == _ERRORS.IN_COOLDOWN:
            error = _ActionCoolDownError(_ACTIONS.GET_VOIP_CREDENTIALS, _LIMITS.VOIP_CREDENTIALS_REQUEST_COOLDOWN_SEC)
        elif errorID == _ERRORS.GENERIC_ERROR:
            logOnly = True
            error = 'The player has received the error to the request for getting of voip credential. Perhaps voip connection to the server is lost, the server is reconnecting to voip.'
    return (error, logOnly)


def createSearchUserError(args):
    errorID = args['int32Arg1']
    error = None
    if errorID == _ERRORS.IN_COOLDOWN:
        error = _ActionCoolDownError(_ACTIONS.FIND_USERS_BY_NAME, _LIMITS.FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC)
    elif errorID in (_ERRORS.IS_BUSY, _ERRORS.WRONG_ARGS):
        error = _SimpleActionError(_ACTIONS.FIND_USERS_BY_NAME, errorID)
    return error
