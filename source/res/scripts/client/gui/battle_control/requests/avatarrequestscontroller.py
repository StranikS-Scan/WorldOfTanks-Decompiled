# Embedded file name: scripts/client/gui/battle_control/requests/AvatarRequestsController.py
from collections import namedtuple
import BigWorld
import AccountCommands
from debug_utils import LOG_DEBUG, LOG_WARNING
from ids_generators import Int32IDGenerator
from helpers import i18n
from messenger import MessengerEntry, g_settings
from gui.shared.utils.requesters.abstract import RequestsByIDProcessor
from gui.shared.utils.requesters.RequestsController import RequestsController
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
from gui.battle_control.requests.settings import AVATAR_REQUEST_TYPE, DEFAULT_COOLDOWN

class _AvatarCooldownManager(RequestCooldownManager):

    def __init__(self):
        super(_AvatarCooldownManager, self).__init__(REQUEST_SCOPE.CLUB)

    def lookupName(self, rqTypeID):
        rqName = AVATAR_REQUEST_TYPE.getKeyByValue(rqTypeID)
        return i18n.makeString('#system_messages:battle/request/%s' % str(rqName))

    def getDefaultCoolDown(self):
        return DEFAULT_COOLDOWN

    def _showSysMessage(self, msg):
        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': msg}))


class _AvatarRequester(RequestsByIDProcessor):

    class _Response(namedtuple('_Response', ['code', 'errStr', 'data'])):

        def isSuccess(self):
            return AccountCommands.isCodeValid(self.code)

    def __init__(self):
        super(_AvatarRequester, self).__init__(Int32IDGenerator())

    def getSender(self):
        return BigWorld.player().prebattleInvitations

    def _doCall(self, method, *args, **kwargs):
        requestID = self._idsGenerator.next()

        def _callback(code, errStr, data):
            ctx = self._requests.get(requestID)
            self._onResponseReceived(requestID, self._makeResponse(code, errStr, data, ctx))

        method(callback=_callback, *args, **kwargs)
        return requestID

    def _makeResponse(self, code = 0, errMsg = '', data = None, ctx = None):
        response = self._Response(code, errMsg, data)
        if not response.isSuccess():
            LOG_WARNING('Avatar request error', ctx, response)
        return response


class AvatarRequestsController(RequestsController):

    def __init__(self):
        super(AvatarRequestsController, self).__init__(_AvatarRequester(), _AvatarCooldownManager())
        self.__handlers = {AVATAR_REQUEST_TYPE.SEND_INVITES: self.sendInvites}

    def fini(self):
        self.__handlers.clear()
        super(AvatarRequestsController, self).fini()

    def sendInvites(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'sendInvitation', ctx.getDatabaseIDs())

    def _getHandlerByRequestType(self, requestTypeID):
        return self.__handlers.get(requestTypeID)

    def _getRequestTimeOut(self):
        return 30.0
