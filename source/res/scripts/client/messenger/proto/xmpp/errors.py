# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/errors.py
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from helpers import i18n, time_utils
from messenger.m_constants import CLIENT_ACTION_ID, CLIENT_ERROR_ID
from messenger.proto.interfaces import IChatError
from messenger.proto import shared_errors
from messenger.proto.shared_errors import ClientActionError
from messenger.proto.xmpp.extensions.error import StanzaErrorExtension, WgErrorExtension, DEF_STANZA_ERROR_CONDITION
from messenger.proto.xmpp.extensions.shared_handlers import IQHandler, ProxyHandler
from messenger.proto.xmpp import xmpp_constants

class _ContactErrorID(shared_errors.I18nErrorID):

    def getName(self):
        if self.errorID in xmpp_constants.CONTACT_ERROR_NAMES:
            errorName = xmpp_constants.CONTACT_ERROR_NAMES[self.errorID]
        else:
            errorName = 'CONTACT_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.client_error_contact(self.getName())


class _LimitErrorID(shared_errors.I18nErrorID):

    def getName(self):
        if self.errorID in xmpp_constants.LIMIT_ERROR_NAMES:
            errorName = xmpp_constants.LIMIT_ERROR_NAMES[self.errorID]
        else:
            errorName = 'LIMIT_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.client_error_limit(self.getName())


class _ChannelErrorID(shared_errors.I18nErrorID):

    def getName(self):
        if self.errorID in xmpp_constants.CHANNEL_ERROR_NAMES:
            errorName = xmpp_constants.CHANNEL_ERROR_NAMES[self.errorID]
        else:
            errorName = 'CONTACT_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.client_error_channel(self.getName())


class _UserRoomCreationErrorID(shared_errors.I18nErrorID):

    def getName(self):
        if self.errorID in xmpp_constants.MUC_CREATION_ERROR_NAMES:
            errorName = xmpp_constants.MUC_CREATION_ERROR_NAMES[self.errorID]
        else:
            errorName = 'MUC_CREATION_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.server_error_user_room_creation(self.getName())


class ClientContactError(shared_errors.ClientError):

    def __init__(self, errorID, name=None):
        kwargs = {}
        if name:
            kwargs['strArg1'] = name
        super(ClientContactError, self).__init__(errorID, **kwargs)

    def createError(self, errorID):
        return _ContactErrorID(errorID)


class ClientIntLimitError(shared_errors.ClientError):

    def __init__(self, errorID, maxLimit, minLimit=0):
        super(ClientIntLimitError, self).__init__(errorID, int32Arg1=minLimit, int32Arg2=maxLimit)

    def createError(self, errorID):
        return _LimitErrorID(errorID)


class ClientChannelError(shared_errors.ClientError):

    def __init__(self, errorID, name=None):
        kwargs = {}
        if name:
            kwargs['strArg1'] = name
        super(ClientChannelError, self).__init__(errorID, **kwargs)

    def createError(self, errorID):
        return _ChannelErrorID(errorID)


class StanzaConditionError(IChatError):
    __slots__ = ('_condition',)

    def __init__(self, errorType, condition):
        super(StanzaConditionError, self).__init__()
        self._errorType = errorType
        self._condition = condition

    def getErrorType(self):
        return self._errorType

    def getCondition(self):
        return self._condition

    def getMessage(self):
        return i18n.makeString(I18N_MESSENGER.XMPP_ERROR_SIMPLE, strArg1=self.getCondition())


class ServerActionError(StanzaConditionError):
    __slots__ = ('_action',)

    def __init__(self, actionID, errorType, condition):
        super(ServerActionError, self).__init__(errorType, condition)
        self._actionID = actionID

    def getActionID(self):
        return self._actionID

    def getMessage(self):
        return i18n.makeString(I18N_MESSENGER.XMPP_ERROR_ACTION, actionName=shared_errors.I18nActionID(self._actionID).getI18nName(), strArg1=self.getCondition())


class ServerUserRoomCreationError(IChatError):
    __slots__ = ('_error',)

    def __init__(self, errorID, roomName):
        super(ServerUserRoomCreationError, self).__init__()
        self._error = _UserRoomCreationErrorID(errorID)
        self._kwargs = {'strArg1': roomName}

    def getMessage(self):
        key = self._error.getI18nKey()
        if key:
            reason = i18n.makeString(key, **self._kwargs)
        else:
            reason = self._error.getName()
        return i18n.makeString(I18N_MESSENGER.XMPP_ERROR_USER_ROOM_CREATION, strArg1=reason)


def createServerIQError(pyGlooxTag):
    return StanzaConditionError(*IQHandler(StanzaErrorExtension()).handleTag(pyGlooxTag))


def createServerActionIQError(actionID, pyGlooxTag):
    return ServerActionError(actionID, *IQHandler(StanzaErrorExtension()).handleTag(pyGlooxTag))


def createServerUserRoomCreationIQError(pyGlooxTag, roomName):
    errorID = IQHandler(WgErrorExtension()).handleTag(pyGlooxTag)
    if errorID != xmpp_constants.MUC_CREATION_ERROR.UNDEFINED:
        error = ServerUserRoomCreationError(errorID, roomName)
    else:
        error = ServerActionError(CLIENT_ACTION_ID.CREATE_USER_ROOM, *IQHandler(StanzaErrorExtension()).handleTag(pyGlooxTag))
    return error


def createServerPresenceError(pyGlooxTag):
    return StanzaConditionError(*ProxyHandler(StanzaErrorExtension()).handleTag(pyGlooxTag))


def createServerActionPresenceError(actionID, pyGlooxTag):
    return ServerActionError(actionID, *ProxyHandler(StanzaErrorExtension()).handleTag(pyGlooxTag))


def createServerMessageError(pyGlooxTag):
    return StanzaConditionError(*ProxyHandler(StanzaErrorExtension()).handleTag(pyGlooxTag))


def createServerActionMessageError(actionID, pyGlooxTag):
    errorType, condition = ProxyHandler(StanzaErrorExtension()).handleTag(pyGlooxTag)
    return ServerActionError(actionID, errorType, condition) if condition != DEF_STANZA_ERROR_CONDITION else ClientActionError(actionID, CLIENT_ERROR_ID.GENERIC)


def createChatBanError(banInfo):
    error = None
    item = banInfo.getFirstActiveItem()
    if item:
        if item.expiresAt:
            expiresAt = time_utils.makeLocalServerTime(item.expiresAt)
        else:
            expiresAt = 0
        error = shared_errors.ChatBanError(expiresAt, item.reason)
    return error
