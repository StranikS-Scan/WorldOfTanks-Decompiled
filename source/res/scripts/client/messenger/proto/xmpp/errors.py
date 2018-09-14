# Embedded file name: scripts/client/messenger/proto/xmpp/errors.py
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from helpers import i18n
from messenger.proto.interfaces import IChatError
from messenger.proto.shared_errors import ClientError, I18nActionID, I18nErrorID, ChatBanError
from messenger.proto.xmpp.extensions.error import StanzaErrorExtension
from messenger.proto.xmpp.extensions.shared_handlers import IQHandler
from messenger.proto.xmpp.xmpp_constants import CONTACT_ERROR_NAMES, LIMIT_ERROR_NAMES

class _ContactErrorID(I18nErrorID):

    def getName(self):
        if self.errorID in CONTACT_ERROR_NAMES:
            errorName = CONTACT_ERROR_NAMES[self.errorID]
        else:
            errorName = 'CONTACT_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.client_error_contact(self.getName())


class _LimitErrorID(I18nErrorID):

    def getName(self):
        if self.errorID in LIMIT_ERROR_NAMES:
            errorName = LIMIT_ERROR_NAMES[self.errorID]
        else:
            errorName = 'LIMIT_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.client_error_limit(self.getName())


class ClientContactError(ClientError):

    def __init__(self, errorID, name = None):
        kwargs = {}
        if name:
            kwargs['strArg1'] = name
        super(ClientContactError, self).__init__(errorID, **kwargs)

    def createError(self, errorID):
        return _ContactErrorID(errorID)


class ClientIntLimitError(ClientError):

    def __init__(self, errorID, maxLimit, minLimit = 0):
        super(ClientIntLimitError, self).__init__(errorID, int32Arg1=minLimit, int32Arg2=maxLimit)

    def createError(self, errorID):
        return _LimitErrorID(errorID)


class StanzaConditionError(IChatError):
    __slots__ = ('_condition',)

    def __init__(self, condition):
        super(StanzaConditionError, self).__init__()
        self._condition = condition

    def getCondition(self):
        return self._condition

    def getMessage(self):
        return i18n.makeString('#messenger:xmpp_error/simple', strArg1=self.getCondition())


class ServerActionError(StanzaConditionError):
    __slots__ = ('_action',)

    def __init__(self, actionID, condition):
        super(ServerActionError, self).__init__(condition)
        self._action = I18nActionID(actionID)

    def getMessage(self):
        return i18n.makeString('#messenger:xmpp_error/action', actionName=self._action.getI18nName(), strArg1=self.getCondition())


def createServerError(pyGlooxTag):
    return StanzaConditionError(IQHandler(StanzaErrorExtension()).handleTag(pyGlooxTag)[1])


def createServerActionError(actionID, pyGlooxTag):
    return ServerActionError(actionID, IQHandler(StanzaErrorExtension()).handleTag(pyGlooxTag)[1])


def createChatBanError(banInfo):
    error = None
    item = banInfo.getFirstActiveItem()
    if item:
        error = ChatBanError(item.expiresAt, item.reason)
    return error
