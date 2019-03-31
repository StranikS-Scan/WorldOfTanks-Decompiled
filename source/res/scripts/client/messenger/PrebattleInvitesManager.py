# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/PrebattleInvitesManager.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from chat_shared import CHAT_RESPONSES
import constants
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_DEBUG, deprecated
from external_strings_utils import truncate_utf8
from ids_generators import SequenceIDGenerator
from messenger import g_settings, invite_formatters, INVITE_COMMENT_MAX_LENGTH
from messenger.common import MessengerGlobalStorage
from messenger.wrappers import PrbInviteWrapper
import Event

class PrebattleInvitesManager(object):

    def __init__(self, usersManager):
        self.__usersManager = usersManager
        self.formatter = invite_formatters.PrebattleInviteFormatter()
        self._IDGen = SequenceIDGenerator()
        self._IDMap = {'inviteIDs': {},
         'prbIDs': {}}
        self.__receivedInvites = {}
        self.__unreadInvitesCount = 0
        self._cp_playerDbID = MessengerGlobalStorage('_playerDbId', -1L)
        self.__eventManager = Event.EventManager()
        self.onReceivedInviteListInited = Event.Event(self.__eventManager)
        self.onReceivedInviteListModified = Event.Event(self.__eventManager)

    def init(self):
        self.__isUserRosterInited = False
        self.__usersManager.onUsersRosterReceived += self.__um_onUsersRosterReceived
        g_playerEvents.onPrebattleInvitesChanged += self.__pe_onPrebattleInvitesChanged

    def clear(self):
        self.__isUserRosterInited = False
        self.__usersManager.onUsersRosterReceived -= self.__um_onUsersRosterReceived
        g_playerEvents.onPrebattleInvitesChanged -= self.__pe_onPrebattleInvitesChanged
        self.__receivedInvites.clear()
        self.__unreadInvitesCount = 0
        self._IDMap = {'inviteIDs': {},
         'prbIDs': {}}
        self.__eventManager.clear()

    def sendInvites(self, accountsToInvite, comment):
        truncated = truncate_utf8(comment.strip(), INVITE_COMMENT_MAX_LENGTH)
        BigWorld.player().prb_sendInvites(accountsToInvite, truncated)

    def acceptInvite(self, inviteID):
        try:
            prebattleID, peripheryID = self._IDMap['inviteIDs'][inviteID]
        except KeyError:
            LOG_ERROR('Invite ID is invalid', inviteID, self._IDMap)
            return

        BigWorld.player().prb_acceptInvite(prebattleID, peripheryID)
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def declineInvite(self, inviteID):
        try:
            prebattleID, peripheryID = self._IDMap['inviteIDs'][inviteID]
        except KeyError:
            LOG_ERROR('Invite ID is invalid', inviteID, self._IDMap)
            return

        BigWorld.player().prb_declineInvite(prebattleID, peripheryID)
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def getInviteInfo(self, inviteID):
        try:
            prebattleID, peripheryID = self._IDMap['inviteIDs'][inviteID]
            return (prebattleID, peripheryID)
        except KeyError:
            return (0, 0)

    def __um_onUsersRosterReceived(self):
        if not self.__isUserRosterInited:
            invitesData = getattr(BigWorld.player(), 'prebattleInvites', {})
            LOG_DEBUG('Users roster received, list of invites is available', invitesData)
            self.__isUserRosterInited = True
            self._buildReceivedInviteList(invitesData)
            self.onReceivedInviteListInited()

    def __pe_onPrebattleInvitesChanged(self, diff):
        if not self.__isUserRosterInited:
            LOG_DEBUG('Received invites ignored. Manager waits for client will receive a roster list')
            return
        else:
            prbInvites = diff.get('prebattleInvites_r')
            if prbInvites is not None:
                self._buildReceivedInviteList(prbInvites)
            prbInvites = diff.get('prebattleInvites')
            if prbInvites is not None:
                self.__updatePrebattleInvites(prbInvites)
            return

    def __updatePrebattleInvites(self, prbInvites):
        receiver = BigWorld.player().name
        receiverDBID = self._cp_playerDbID.value()
        added = []
        changed = []
        deleted = []
        modified = False
        for (prebattleID, peripheryID), data in prbInvites.iteritems():
            inviteID = self._makeInviteID(prebattleID, peripheryID)
            if data is None:
                if self._delInvite(inviteID):
                    modified = True
                    deleted.append(inviteID)
                continue
            anotherPeriphery = connectionManager.peripheryID != peripheryID
            invite = PrbInviteWrapper(id=inviteID, receiver=receiver, receiverDBID=receiverDBID, peripheryID=peripheryID, anotherPeriphery=anotherPeriphery, **data)
            inList = inviteID in self.__receivedInvites
            if not inList:
                if self._addInvite(invite):
                    modified = True
                    added.append(inviteID)
            elif self._updateInvite(invite):
                modified = True
                changed.append(inviteID)

        if modified:
            self.onReceivedInviteListModified(added, changed, deleted)
        return

    def handleChatActionFailureEvent(self, actionResponse, chatAction):
        if actionResponse in [CHAT_RESPONSES.inviteCommandError, CHAT_RESPONSES.inviteCreateError, CHAT_RESPONSES.inviteCreationNotAllowed]:
            return True
        return False

    def _makeInviteID(self, prebattleID, peripheryID):
        inviteID = self._IDMap['prbIDs'].get((prebattleID, peripheryID))
        if inviteID is None:
            inviteID = self._IDGen.next()
            self._IDMap['inviteIDs'][inviteID] = (prebattleID, peripheryID)
            self._IDMap['prbIDs'][prebattleID, peripheryID] = inviteID
        return inviteID

    def _addInvite(self, invite):
        if g_settings.userPreferences['invitesFromFriendsOnly']:
            user = self.__usersManager.getUser(invite.creatorDBID, invite.creator)
            if not user.isFriend():
                LOG_DEBUG('Invite to be ignored:', invite)
                return False
        link = self.formatter.link(invite)
        if not len(link):
            if constants.IS_DEVELOPMENT:
                LOG_WARNING('Formatter not found. Invite data : ', invite)
            return False
        self.__receivedInvites[invite.id] = (invite, link)
        if invite.isActive():
            self.__unreadInvitesCount += 1
        return True

    def _updateInvite(self, other):
        inviteID = other.id
        invite, _ = self.__receivedInvites[inviteID]
        if other.isActive() and g_settings.userPreferences['invitesFromFriendsOnly']:
            user = self.__usersManager.getUser(invite.creatorDBID, invite.creator)
            if not user.isFriend():
                LOG_DEBUG('Invite to be ignored:', invite)
                return False
        prevCount = invite.count
        invite = invite._merge(other)
        link = self.formatter.link(invite)
        self.__receivedInvites[inviteID] = (invite, link)
        if invite.isActive() and prevCount < invite.count:
            self.__unreadInvitesCount += 1
        return True

    def _delInvite(self, inviteID):
        result = inviteID in self.__receivedInvites
        if result:
            self.__receivedInvites.pop(inviteID)
        return result

    def _buildReceivedInviteList(self, invitesData):
        self.__receivedInvites.clear()
        self.__unreadInvitesCount = 0
        receiver = BigWorld.player().name
        receiverDBID = self._cp_playerDbID.value()
        for (prebattleID, peripheryID), data in invitesData.iteritems():
            inviteID = self._makeInviteID(prebattleID, peripheryID)
            anotherPeriphery = connectionManager.peripheryID != peripheryID
            invite = PrbInviteWrapper(id=inviteID, receiver=receiver, receiverDBID=receiverDBID, peripheryID=peripheryID, anotherPeriphery=anotherPeriphery, **data)
            self._addInvite(invite)

    def getReceivedInviteCount(self):
        return len(self.__receivedInvites)

    def getReceivedInvite(self, inviteID):
        return self.__receivedInvites.get(inviteID)

    def getReceivedInvites(self, IDs=None):
        result = self.__receivedInvites.values()
        if IDs is not None:
            result = filter(lambda item: item[0].id in IDs, result)
        return result

    def getUnreadCount(self):
        return self.__unreadInvitesCount

    def resetUnreadCount(self):
        self.__unreadInvitesCount = 0
