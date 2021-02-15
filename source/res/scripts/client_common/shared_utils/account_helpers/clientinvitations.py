# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/account_helpers/ClientInvitations.py
from collections import namedtuple
from functools import partial
import BigWorld
import AccountCommands
from constants import INVITATION_STATUS
from helpers.time_utils import getCurrentTimestamp, getServerUTCTime
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
UniqueId = namedtuple('UniqueId', ['id', 'senderID'])

class InvitationScope(object):
    AVATAR = 0
    ACCOUNT = 1


class ClientInvitations(object):

    def __init__(self, playerEvents):
        self.__proxy = None
        self.__expCbID = None
        self.__invitations = {}
        self.__playerEvents = playerEvents
        return

    def clear(self):
        self._clearExpiryCallback()

    def getInvites(self):
        return self.__invitations

    def setProxy(self, proxy):
        self.__proxy = proxy

    def onProxyBecomePlayer(self):
        pass

    def onProxyBecomeNonPlayer(self):
        pass

    def processInvitations(self, invitations, scope):
        LOG_DEBUG('ClientInvitations::processInvitations', invitations)
        for inv in invitations:
            senderID = inv.get('senderDBID', 0)
            senderVehID = inv.get('senderVehID', 0)
            if scope == InvitationScope.ACCOUNT:
                if senderVehID:
                    uniqueId = UniqueId(inv['id'], senderVehID)
                    if uniqueId in self.__invitations:
                        del self.__invitations[uniqueId]
            if (scope == InvitationScope.AVATAR or not senderID) and senderVehID:
                senderID = senderVehID
            if senderID:
                uniqueId = UniqueId(inv['id'], senderID)
                self.__invitations[uniqueId] = inv

        self._loadExpiryCallback()
        self.__playerEvents.onPrebattleInvitationsChanged(self.__invitations)

    def sendInvitation(self, accountsToInvite, comment='', callback=None):
        if self.__playerEvents.isPlayerEntityChanging:
            return
        self.__proxy._doCmdIntArrStrArr(AccountCommands.CMD_INVITATION_SEND, accountsToInvite, [comment], callback)

    def acceptInvitation(self, invitationID, senderID, callback=None):
        if self.__playerEvents.isPlayerEntityChanging:
            return
        proxy = partial(self._onInvitationResponseReceived, INVITATION_STATUS.ACCEPTED, invitationID, senderID, callback)
        self.__proxy._doCmdInt3(AccountCommands.CMD_INVITATION_ACCEPT, invitationID, senderID, 0, proxy)
        self.__playerEvents.onPrebattleInvitationAccepted(invitationID, senderID)

    def declineInvitation(self, invitationID, senderID, callback=None):
        if self.__playerEvents.isPlayerEntityChanging:
            return
        proxy = partial(self._onInvitationResponseReceived, INVITATION_STATUS.DECLINED, invitationID, senderID, callback)
        self.__proxy._doCmdInt3(AccountCommands.CMD_INVITATION_DECLINE, invitationID, senderID, 0, proxy)

    def _onInvitationResponseReceived(self, newStatus, invitationId, senderID, callback, _, code, errStr):
        if AccountCommands.isCodeValid(code):
            uniqueId = UniqueId(invitationId, senderID)
            try:
                self.__invitations[uniqueId]['status'] = newStatus
                self.__playerEvents.onPrebattleInvitationsChanged(self.__invitations)
            except KeyError:
                LOG_ERROR('Unknown invitation', uniqueId, self.__invitations, callback, code, errStr)

        else:
            self.__playerEvents.onPrebattleInvitationsError(invitationId, code, errStr)
        if callback is not None:
            callback(code, errStr)
        return

    def _cancelInvitations(self, predicate):
        for inv in self.__invitations.itervalues():
            if predicate(inv):
                inv['status'] = INVITATION_STATUS.ERROR

    def _loadExpiryCallback(self):
        self._clearExpiryCallback()
        if self.__invitations:
            inviteId = min(self.__invitations, key=lambda k: self.__invitations[k]['expiresAt'])
            invite = self.__invitations[inviteId]
            expTime = max(invite['expiresAt'] - getServerUTCTime(), 0.0)
            self.__expCbID = BigWorld.callback(expTime, partial(self.__onInviteExpired, inviteId))
            LOG_DEBUG('Invite expiration callback has been loaded', inviteId, expTime)

    def _clearExpiryCallback(self):
        if self.__expCbID is not None:
            BigWorld.cancelCallback(self.__expCbID)
            self.__expCbID = None
        return

    def __onInviteExpired(self, inviteId):
        try:
            del self.__invitations[inviteId]
            self.__playerEvents.onPrebattleInvitationsChanged(self.__invitations)
        except KeyError:
            LOG_ERROR('There is error while removing expired invite')
            LOG_CURRENT_EXCEPTION()

        self._loadExpiryCallback()


class ReplayClientInvitations(ClientInvitations):

    def processInvitations(self, invitations, scope):
        for inv in invitations:
            inv['expiresAt'] = getCurrentTimestamp() + 86400

        super(ReplayClientInvitations, self).processInvitations(invitations, scope)
