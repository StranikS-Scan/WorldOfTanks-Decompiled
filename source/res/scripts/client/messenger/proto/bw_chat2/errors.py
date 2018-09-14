# Embedded file name: scripts/client/messenger/proto/bw_chat2/errors.py
import BigWorld
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from helpers import i18n, html
from helpers.time_utils import makeLocalServerTime
from messenger.proto.interfaces import IServerError
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


class _ActionCoolDownError(IServerError):
    __slots__ = ('_actionID', '_coolDown')

    def __init__(self, actionID, coolDown = None):
        super(_ActionCoolDownError, self).__init__()
        self._actionID = actionID
        self._coolDown = coolDown

    def getMessage(self):
        name = getChatActionName(self._actionID)
        if self._coolDown:
            msg = i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_ACTION_IN_COOLDOWN, strArg1=name, floatArg1=self._coolDown)
        else:
            msg = i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_ACTION_IN_COOLDOWN_WO_PERIOD, strArg1=name)
        return msg


class _BattleCommandError(IServerError):
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


class _SimpleActionError(IServerError):
    __slots__ = ('_actionID', '_errorID')

    def __init__(self, actionID, errorID):
        self._actionID = actionID
        self._errorID = errorID

    def getMessage(self):
        return getChatErrorMessage(self._errorID, {'strArg1': getChatActionName(self._actionID)})


class _AdminCommandError(IServerError):
    __slots__ = ('_error',)

    def __init__(self, error):
        super(_AdminCommandError, self).__init__()
        self._error = error

    def getMessage(self):
        return i18n.makeString(I18N_MESSENGER.SERVER_ERRORS_CHATCOMMANDERROR_MESSAGE, error=self._error)


class _SimpleAdminCommandError(_AdminCommandError):

    def __init__(self, errorID, kwargs = None):
        super(_SimpleAdminCommandError, self).__init__(getChatErrorMessage(errorID, kwargs or {}))


class _AdminCommandI18nError(_AdminCommandError):

    def __init__(self, keys, kwargs):
        super(_AdminCommandI18nError, self).__init__(i18n.makeString(keys, **kwargs))


class _AdminCommandCoolDownError(_AdminCommandError):

    def __init__(self):
        super(_AdminCommandCoolDownError, self).__init__(i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_COMMAND_IN_COOLDOWN_WO_NAME, floatArg1=_LIMITS.ADMIN_COMMANDS_FROM_CLIENT_COOLDOWN_SEC))


class _ChatBanError(IServerError):
    __slots__ = ('_endTime', '_reason')

    def __init__(self, endTime, reason):
        super(_ChatBanError, self).__init__()
        self._endTime = makeLocalServerTime(endTime)
        self._reason = reason

    def getTitle(self):
        return i18n.makeString(I18N_MESSENGER.SERVER_ERRORS_CHATBANNED_TITLE)

    def getMessage(self):
        if self._endTime:
            banEndTime = BigWorld.wg_getLongDateFormat(self._endTime) + ' ' + BigWorld.wg_getShortTimeFormat(self._endTime)
            msg = i18n.makeString('#chat:errors/chatbanned', banEndTime=banEndTime, banReason=self._reason)
        else:
            msg = i18n.makeString('#chat:errors/chatbannedpermanent', banReason=self._reason)
        return msg

    def isModal(self):
        return True


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
        error = errorID == _ERRORS.IN_CHAT_BAN and _ChatBanError(args['floatArg1'], args['strArg1'])
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


def createVOIPError(args):
    errorID = args['int32Arg1']
    error = None
    if errorID == _ERRORS.IN_COOLDOWN:
        error = _ActionCoolDownError(_ACTIONS.GET_VOIP_CREDENTIALS, _LIMITS.VOIP_CREDENTIALS_REQUEST_COOLDOWN_SEC)
    return error


def createSearchUserError(args):
    errorID = args['int32Arg1']
    error = None
    if errorID == _ERRORS.IN_COOLDOWN:
        error = _ActionCoolDownError(_ACTIONS.FIND_USERS_BY_NAME, _LIMITS.FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC)
    elif errorID in (_ERRORS.IS_BUSY, _ERRORS.WRONG_ARGS):
        error = _SimpleActionError(_ACTIONS.FIND_USERS_BY_NAME, errorID)
    return error
