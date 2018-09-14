# Embedded file name: scripts/client/messenger/proto/shared_errors.py
import BigWorld
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from helpers import i18n
from messenger.m_constants import CLIENT_ERROR_NAMES, CLIENT_ACTION_NAMES, CLIENT_ERROR_ID
from messenger.proto.interfaces import IChatError

class I18nErrorID(object):
    __slots__ = ('errorID',)

    def __init__(self, errorID):
        super(I18nErrorID, self).__init__()
        self.errorID = errorID

    def __repr__(self):
        return '{0}'.format(self.getName())

    def getName(self):
        if self.errorID in CLIENT_ERROR_NAMES:
            errorName = CLIENT_ERROR_NAMES[self.errorID]
        else:
            errorName = 'CLIENT_ERROR_{0}'.format(self.errorID)
        return errorName

    def getI18nKey(self):
        return I18N_MESSENGER.client_error_shared(self.getName())


class I18nActionID(object):
    __slots__ = ('actionID',)

    def __init__(self, actionID):
        super(I18nActionID, self).__init__()
        self.actionID = actionID

    def __repr__(self):
        return '{0}'.format(self.getName())

    def getName(self):
        if self.actionID in CLIENT_ACTION_NAMES:
            actionName = CLIENT_ACTION_NAMES[self.actionID]
        else:
            actionName = 'CLIENT_ACTION_{0}'.format(self.actionID)
        return actionName

    def getI18nName(self):
        name = self.getName()
        key = I18N_MESSENGER.client_action(name)
        if key:
            name = i18n.makeString(key)
        return name


class ClientError(IChatError):
    __slots__ = ('_error', '_kwargs')

    def __init__(self, errorID, **kwargs):
        self._error = self.createError(errorID)
        self._kwargs = kwargs

    def __repr__(self):
        return '{0}(error={1})'.format(self.__class__.__name__, self._error)

    def createError(self, errorID):
        return I18nErrorID(errorID)

    def getErrorID(self):
        return self._error.errorID

    def getErrorName(self):
        return self._error.getName()

    def getMessage(self):
        key = self._error.getI18nKey()
        if key:
            result = i18n.makeString(key, **self._kwargs)
        else:
            result = self._error.getName()
            if self._kwargs:
                result = '{0}/{1}'.format(result, self._kwargs)
        return result


class ClientActionError(ClientError):
    __slots__ = ('_action',)

    def __init__(self, actionID, errorID = None, **kwargs):
        super(ClientActionError, self).__init__((errorID or CLIENT_ERROR_ID.GENERIC), **kwargs)
        self._action = self.createAction(actionID)

    def __repr__(self):
        return '{0}(action={1}, error={2})'.format(self.__class__.__name__, self._action, self._error)

    def createAction(self, actionID):
        return I18nActionID(actionID)

    def getActionID(self):
        return self._action.actionID

    def getMessage(self):
        if 'actionName' not in self._kwargs:
            self._kwargs['actionName'] = self._action.getI18nName()
        return super(ClientActionError, self).getMessage()


class ChatCoolDownError(ClientActionError):

    def __init__(self, actionID, coolDown = None):
        if coolDown:
            kwargs = {'floatArg1': coolDown}
        else:
            kwargs = {}
        super(ChatCoolDownError, self).__init__(actionID, CLIENT_ERROR_ID.COOLDOWN, **kwargs)

    def getMessage(self):
        actionName = self._action.getI18nName()
        if self._kwargs:
            msg = i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_ACTION_IN_COOLDOWN, actionName=actionName, **self._kwargs)
        else:
            msg = i18n.makeString(I18N_MESSENGER.CLIENT_ERROR_ACTION_IN_COOLDOWN_WO_PERIOD, actionName=actionName)
        return msg


class ChatBanError(IChatError):
    __slots__ = ('_endTime', '_reason')

    def __init__(self, endTime, reason):
        super(ChatBanError, self).__init__()
        self._endTime = endTime
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
