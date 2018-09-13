# Embedded file name: scripts/client/gui/prb_control/invites.py
from collections import namedtuple
import BigWorld
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from account_helpers import getPlayerDatabaseID, isRoamingEnabled
import constants
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.shared import g_itemsCache
from gui.shared.actions import ActionsChain
from ids_generators import SequenceIDGenerator
from helpers import time_utils
from messenger import g_settings
import Event
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from predefined_hosts import g_preDefinedHosts
_PrbInviteData = namedtuple('_PrbInviteData', ' '.join(['id',
 'createTime',
 'type',
 'comment',
 'creator',
 'creatorDBID',
 'creatorClanAbbrev',
 'receiver',
 'receiverDBID',
 'receiverClanAbbrev',
 'state',
 'count',
 'peripheryID',
 'prebattleID']))

class PrbInviteWrapper(_PrbInviteData):

    @staticmethod
    def __new__(cls, id = -1L, createTime = None, type = 0, comment = str(), creator = str(), creatorDBID = -1L, creatorClanAbbrev = None, receiver = str(), receiverDBID = -1L, receiverClanAbbrev = None, state = None, count = 0, peripheryID = 0, prebattleID = 0, **kwargs):
        if createTime is not None:
            createTime = time_utils.makeLocalServerTime(createTime)
        result = _PrbInviteData.__new__(cls, id, createTime, type, comment, creator, creatorDBID, creatorClanAbbrev, receiver, receiverDBID, receiverClanAbbrev, state, count, peripheryID, prebattleID)
        result.showAt = 0
        return result

    @property
    def creatorFullName(self):
        return g_lobbyContext.getPlayerFullName(self.creator, clanAbbrev=self.creatorClanAbbrev, pDBID=self.creatorDBID, regionCode=g_lobbyContext.getRegionCode(self.creatorDBID))

    @property
    def receiverFullName(self):
        return g_lobbyContext.getPlayerFullName(self.receiver, clanAbbrev=self.receiverClanAbbrev, pDBID=self.receiverDBID, regionCode=g_lobbyContext.getRegionCode(self.receiverDBID))

    @property
    def anotherPeriphery(self):
        return connectionManager.peripheryID != self.peripheryID

    @property
    def alreadyJoined(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher:
            prbFunctional = dispatcher.getPrbFunctional()
            unitFunctional = dispatcher.getUnitFunctional()
            if self.type in (constants.PREBATTLE_TYPE.UNIT, constants.PREBATTLE_TYPE.SORTIE, constants.PREBATTLE_TYPE.FORT_BATTLE) and self._isCurrentPrebattle(unitFunctional):
                return True
            if self._isCurrentPrebattle(prbFunctional):
                return True
        return False

    def _isCurrentPrebattle(self, functional):
        return functional is not None and self.prebattleID == functional.getID()

    def _merge(self, other):
        data = {}
        if other.createTime is not None:
            data['createTime'] = time_utils.makeLocalServerTime(other.createTime)
        if other.state > 0:
            data['state'] = other.state
        if other.count > 0:
            data['count'] = other.count
        if len(other.comment) or other.isActive():
            data['comment'] = other.comment
        return self._replaceEx(**data)

    def _replaceEx(self, **kwargs):
        result = self._replace(**kwargs)
        result.showAt = self.showAt
        return result

    def isPlayerSender(self):
        return False

    def isActive(self):
        return self.state == constants.PREBATTLE_INVITE_STATE.ACTIVE


class _AcceptInvitesPostActions(ActionsChain):

    def __init__(self, peripheryID, prebattleID, actions):
        self.peripheryID = peripheryID
        self.prebattleID = prebattleID
        super(_AcceptInvitesPostActions, self).__init__(actions)


class PRB_INVITES_INIT_STEP(object):
    UNDEFINED = 0
    RECEIVED_ROSTERS = 1
    STARTED = 2
    DATA_BUILD = 4
    INITED = RECEIVED_ROSTERS | DATA_BUILD | STARTED


class InvitesManager(object):
    __clanInfo = None

    def __init__(self, loader):
        self.__loader = loader
        self._IDGen = SequenceIDGenerator()
        self._IDMap = {'inviteIDs': {},
         'prbIDs': {}}
        self.__receivedInvites = {}
        self.__unreadInvitesCount = 0
        self.__eventManager = Event.EventManager()
        self.__acceptChain = None
        self.onReceivedInviteListInited = Event.Event(self.__eventManager)
        self.onReceivedInviteListModified = Event.Event(self.__eventManager)
        return

    def __del__(self):
        LOG_DEBUG('InvitesManager deleted')

    def init(self):
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        g_messengerEvents.users.onUsersRosterReceived += self.__me_onUsersRosterReceived
        g_playerEvents.onPrebattleInvitesChanged += self.__pe_onPrebattleInvitesChanged
        g_playerEvents.onPrebattleInvitesStatus += self.__pe_onPrebattleInvitesStatus

    def fini(self):
        self.__clearAcceptChain()
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        self.__loader = None
        g_messengerEvents.users.onUsersRosterReceived -= self.__me_onUsersRosterReceived
        g_playerEvents.onPrebattleInvitesChanged -= self.__pe_onPrebattleInvitesChanged
        g_playerEvents.onPrebattleInvitesStatus -= self.__pe_onPrebattleInvitesStatus
        self.clear()
        return

    def start(self):
        if self.__inited & PRB_INVITES_INIT_STEP.STARTED == 0:
            self.__inited |= PRB_INVITES_INIT_STEP.STARTED
            if self.__inited == PRB_INVITES_INIT_STEP.INITED:
                self.onReceivedInviteListInited()

    def clear(self):
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        self.__receivedInvites.clear()
        self.__unreadInvitesCount = 0
        self._IDMap = {'inviteIDs': {},
         'prbIDs': {}}
        self.__eventManager.clear()

    def onAvatarBecomePlayer(self):
        if self.__inited & PRB_INVITES_INIT_STEP.STARTED > 0:
            self.__inited ^= PRB_INVITES_INIT_STEP.STARTED
        self.__clearAcceptChain()

    @storage_getter('users')
    def users(self):
        return None

    def isInited(self):
        return self.__inited == PRB_INVITES_INIT_STEP.INITED

    def acceptInvite(self, inviteID, postActions = None):
        try:
            prebattleID, peripheryID = self._IDMap['inviteIDs'][inviteID]
        except KeyError:
            LOG_ERROR('Invite ID is invalid', inviteID, self._IDMap)
            return

        self.__clearAcceptChain()
        if not postActions:
            self._doAccept(prebattleID, peripheryID)
        else:
            self.__acceptChain = _AcceptInvitesPostActions(peripheryID, prebattleID, postActions)
            self.__acceptChain.onStopped += self.__accept_onPostActionsStopped
            self.__acceptChain.start()
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

    def canAcceptInvite(self, invite):
        result = False
        if invite.id in self.__receivedInvites:
            dispatcher = self.__loader.getDispatcher()
            if dispatcher:
                prbFunctional = dispatcher.getPrbFunctional()
                unitFunctional = dispatcher.getUnitFunctional()
                preQueueFunctional = dispatcher.getPreQueueFunctional()
                if invite.alreadyJoined:
                    return False
                if prbFunctional and prbFunctional.hasLockedState() or unitFunctional and unitFunctional.hasLockedState() or preQueueFunctional and preQueueFunctional.hasLockedState():
                    return False
            another = invite.anotherPeriphery
            if another:
                if g_preDefinedHosts.periphery(invite.peripheryID) is None:
                    LOG_ERROR('Periphery not found')
                    result = False
                elif g_lobbyContext.getCredentials() is None:
                    LOG_ERROR('Login info not found')
                    result = False
                elif g_preDefinedHosts.isRoamingPeriphery(invite.peripheryID) and not isRoamingEnabled(g_itemsCache.items.stats.attributes):
                    LOG_ERROR('Roaming is not supported')
                    result = False
                else:
                    result = invite.id > 0 and invite.isActive()
            else:
                result = invite.id > 0 and invite.isActive()
        return result

    def canDeclineInvite(self, invite):
        result = False
        if invite.id in self.__receivedInvites:
            result = invite.id > 0 and invite.isActive()
        return result

    def getInviteInfo(self, inviteID):
        try:
            prebattleID, peripheryID = self._IDMap['inviteIDs'][inviteID]
            return (prebattleID, peripheryID)
        except KeyError:
            return (0, 0)

    def getReceivedInviteCount(self):
        return len(self.__receivedInvites)

    def getReceivedInvite(self, inviteID):
        invite = None
        if inviteID in self.__receivedInvites:
            invite = self.__receivedInvites[inviteID]
        return invite

    def getReceivedInvites(self, IDs = None):
        result = self.__receivedInvites.values()
        if IDs is not None:
            result = filter(lambda item: item.id in IDs, result)
        return result

    def getUnreadCount(self):
        return self.__unreadInvitesCount

    def resetUnreadCount(self):
        self.__unreadInvitesCount = 0

    def _doAccept(self, prebattleID, peripheryID):
        if connectionManager.peripheryID == peripheryID:
            BigWorld.player().prb_acceptInvite(prebattleID, peripheryID)
        else:
            LOG_ERROR('Invalid periphery', (prebattleID, peripheryID), connectionManager.peripheryID)

    def _makeInviteID(self, prebattleID, peripheryID):
        inviteID = self._IDMap['prbIDs'].get((prebattleID, peripheryID))
        if inviteID is None:
            inviteID = self._IDGen.next()
            self._IDMap['inviteIDs'][inviteID] = (prebattleID, peripheryID)
            self._IDMap['prbIDs'][prebattleID, peripheryID] = inviteID
        return inviteID

    def _addInvite(self, invite, userGetter):
        if g_settings.userPrefs.invitesFromFriendsOnly:
            user = userGetter(invite.creatorDBID)
            if user is None or not user.isFriend():
                LOG_DEBUG('Invite to be ignored:', invite)
                return False
        self.__receivedInvites[invite.id] = invite
        if invite.isActive():
            self.__unreadInvitesCount += 1
        return True

    def _updateInvite(self, other, userGetter):
        inviteID = other.id
        invite = self.__receivedInvites[inviteID]
        if other.isActive() and g_settings.userPrefs.invitesFromFriendsOnly:
            user = userGetter(invite.creatorDBID)
            if user is None or not user.isFriend():
                LOG_DEBUG('Invite to be ignored:', invite)
                return False
        prevCount = invite.count
        invite = invite._merge(other)
        self.__receivedInvites[inviteID] = invite
        if invite.isActive() and prevCount < invite.count:
            self.__unreadInvitesCount += 1
        return True

    def _delInvite(self, inviteID):
        result = inviteID in self.__receivedInvites
        if result:
            self.__receivedInvites.pop(inviteID)
        return result

    def _buildReceivedInvitesList(self, invitesData):
        if self.__inited & PRB_INVITES_INIT_STEP.DATA_BUILD == 0:
            self.__inited |= PRB_INVITES_INIT_STEP.DATA_BUILD
        self.__receivedInvites.clear()
        self.__unreadInvitesCount = 0
        receiver = BigWorld.player().name
        receiverDBID = getPlayerDatabaseID()
        receiverClanAbbrev = g_lobbyContext.getClanAbbrev(self.__clanInfo)
        userGetter = self.users.getUser
        for (prebattleID, peripheryID), data in invitesData.iteritems():
            inviteID = self._makeInviteID(prebattleID, peripheryID)
            invite = PrbInviteWrapper(id=inviteID, receiver=receiver, receiverDBID=receiverDBID, receiverClanAbbrev=receiverClanAbbrev, peripheryID=peripheryID, prebattleID=prebattleID, **data)
            self._addInvite(invite, userGetter)

    def __clearAcceptChain(self):
        if self.__acceptChain is not None:
            self.__acceptChain.onStopped -= self.__accept_onPostActionsStopped
            self.__acceptChain.stop()
            self.__acceptChain = None
        return

    def __me_onUsersRosterReceived(self):
        if self.__inited & PRB_INVITES_INIT_STEP.RECEIVED_ROSTERS == 0:
            invitesData = getattr(BigWorld.player(), 'prebattleInvites', {})
            LOG_DEBUG('Users roster received, list of invites is available', invitesData)
            self.__inited |= PRB_INVITES_INIT_STEP.RECEIVED_ROSTERS
            self._buildReceivedInvitesList(invitesData)
            if self.__inited == PRB_INVITES_INIT_STEP.INITED:
                self.onReceivedInviteListInited()

    def __pe_onPrebattleInvitesChanged(self, diff):
        if self.__inited & PRB_INVITES_INIT_STEP.RECEIVED_ROSTERS == 0:
            LOG_DEBUG('Received invites ignored. Manager waits for client will receive a roster list')
            return
        else:
            prbInvites = diff.get(('prebattleInvites', '_r'))
            if prbInvites is not None:
                self._buildReceivedInvitesList(prbInvites)
            prbInvites = diff.get('prebattleInvites')
            if prbInvites is not None:
                self.__updatePrebattleInvites(prbInvites)
            return

    def __pe_onPrebattleInvitesStatus(self, dbID, name, status):
        if status != constants.PREBATTLE_INVITE_STATUS.OK:
            statusName = constants.PREBATTLE_INVITE_STATUS_NAMES[status]
            SystemMessages.g_instance.pushI18nMessage('#system_messages:invite/status/%s' % statusName, type=SystemMessages.SM_TYPE.Warning)

    def __updatePrebattleInvites(self, prbInvites):
        receiver = BigWorld.player().name
        receiverDBID = getPlayerDatabaseID()
        receiverClanAbbrev = g_lobbyContext.getClanAbbrev(self.__clanInfo)
        added = []
        changed = []
        deleted = []
        modified = False
        rosterGetter = self.users.getUser
        for (prebattleID, peripheryID), data in prbInvites.iteritems():
            inviteID = self._makeInviteID(prebattleID, peripheryID)
            if data is None:
                if self._delInvite(inviteID):
                    modified = True
                    deleted.append(inviteID)
                continue
            invite = PrbInviteWrapper(id=inviteID, receiver=receiver, receiverDBID=receiverDBID, receiverClanAbbrev=receiverClanAbbrev, peripheryID=peripheryID, prebattleID=prebattleID, **data)
            inList = inviteID in self.__receivedInvites
            if not inList:
                if self._addInvite(invite, rosterGetter):
                    modified = True
                    added.append(inviteID)
            elif self._updateInvite(invite, rosterGetter):
                modified = True
                changed.append(inviteID)

        if modified:
            self.onReceivedInviteListModified(added, changed, deleted)
        return

    def __accept_onPostActionsStopped(self, isCompleted):
        if not isCompleted:
            return
        prebattleID = self.__acceptChain.prebattleID
        peripheryID = self.__acceptChain.peripheryID
        if (prebattleID, peripheryID) in self._IDMap['prbIDs']:
            self._doAccept(prebattleID, peripheryID)
            if self.__unreadInvitesCount > 0:
                self.__unreadInvitesCount -= 1
        else:
            LOG_ERROR('Prebattle invite not found', prebattleID, peripheryID)
