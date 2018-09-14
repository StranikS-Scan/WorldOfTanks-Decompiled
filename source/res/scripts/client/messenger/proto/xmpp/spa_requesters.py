# Embedded file name: scripts/client/messenger/proto/xmpp/spa_requesters.py
from adisp import async
from messenger.m_constants import CLIENT_ERROR_ID
from messenger.proto.entities import SharedUserEntity
from messenger.proto.shared_errors import ClientError
from messenger.proto.xmpp.errors import createServerError
from messenger.proto.xmpp.extensions import spa_resolver
from messenger.proto.xmpp.gloox_constants import GLOOX_EVENT as _EVENT, IQ_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA
from messenger.storage import storage_getter

class NicknameResolver(ClientEventsHandler):

    def __init__(self):
        super(NicknameResolver, self).__init__()
        self.__cached = {}
        self.__callback = None
        self.__iqID = ''
        self.__isRegistered = False
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    def clear(self):
        self.__cached.clear()
        self.__callback = None
        self.__iqID = ''
        return

    def registerHandlers(self):
        client = self.client()
        if not client:
            return
        register = client.registerHandler
        register(_EVENT.IQ, self.__handleIQ)
        register(_EVENT.DISCONNECTED, self.__handleDisconnected)
        self.__isRegistered = True

    def unregisterHandlers(self):
        self.__isRegistered = False
        client = self.client()
        if not client:
            return
        unregister = client.unregisterHandler
        unregister(_EVENT.IQ, self.__handleIQ)
        unregister(_EVENT.DISCONNECTED, self.__handleDisconnected)

    def resolve(self, dbIDs, callback = None):
        self.__callback = callback
        if not self.__isRegistered:
            self.__doCallback(error=ClientError(CLIENT_ERROR_ID.GENERIC))
            return False
        if self.__iqID:
            self.__doCallback(error=ClientError(CLIENT_ERROR_ID.LOCKED))
            return False
        getter = self.usersStorage.getUser
        result, required = {}, []
        for dbID in dbIDs:
            user = getter(dbID)
            if user and user.hasValidName():
                result[dbID] = user.getName()
            else:
                required.append(dbID)

        if not required:
            self.__doCallback(result=result)
            return False
        client = self.client()
        if not client or not client.isConnected():
            self.__doCallback(error=ClientError(CLIENT_ERROR_ID.NOT_CONNECTED))
            return False
        self.__cached = result
        self.__callback = callback
        self.__iqID = client.sendIQ(spa_resolver.SpaResolverByIDsQuery(required))
        return True

    def __doCallback(self, result = None, error = None):
        if self.__callback:
            self.__callback(result or {}, error)
            self.__callback = None
        return

    def __handleIQ(self, iqID, iqType, pyGlooxTag):
        if iqID != self.__iqID:
            return
        else:
            result, error = self.__cached.copy(), None
            self.__cached.clear()
            self.__iqID = ''
            if iqType == IQ_TYPE.RESULT:
                handler = spa_resolver.SpaResolverHandler()
                getter = self.usersStorage.getUser
                setter = self.usersStorage.addUser
                errorOutput = g_logOutput.error
                for dbID, name, error in handler.handleTag(pyGlooxTag):
                    if error:
                        errorOutput(CLIENT_LOG_AREA.PY_WRAPPER, 'Item is invalid', dbID, name, error)
                        continue
                    user = getter(dbID)
                    if not user:
                        user = SharedUserEntity(dbID, name)
                        setter(user)
                    else:
                        user.update(name=name)
                    result[dbID] = name

            elif iqType == IQ_TYPE.ERROR:
                error = createServerError(pyGlooxTag)
            self.__doCallback(result=result, error=error)
            return

    def __handleDisconnected(self, reason, description):
        self.__doCallback(result=self.__cached.copy())
        self.clear()


class AsyncNicknameResolver(NicknameResolver):

    @async
    def resolve(self, dbIDs, callback = None):
        super(AsyncNicknameResolver, self).resolve(dbIDs, callback)
