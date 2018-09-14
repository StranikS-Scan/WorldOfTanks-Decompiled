# Embedded file name: scripts/client/gui/prb_control/invites.py
from collections import namedtuple, defaultdict
import BigWorld
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from account_helpers import isRoamingEnabled
from constants import PREBATTLE_INVITE_STATUS, PREBATTLE_INVITE_STATUS_NAMES, PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING
from gui import SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.settings import PRB_INVITE_STATE
from gui.battle_control import g_sessionProvider as g_battleCtrl
from gui.shared import g_itemsCache
from gui.shared.utils import getPlayerDatabaseID, getPlayerName
from gui.shared.actions import ActionsChain
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from ids_generators import SequenceIDGenerator
from helpers import time_utils
import Event
from messenger import g_settings
from messenger.m_constants import USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from messenger.ext import isNotFriendSenderIgnored
from predefined_hosts import g_preDefinedHosts

def isInviteSenderIgnoredInBattle(user, areFriendsOnly, isFromBattle):
    if isFromBattle:
        return isNotFriendSenderIgnored(user, False)
    return isNotFriendSenderIgnored(user, areFriendsOnly)


class _INVITE_VERSION(object):
    OLD = 1
    NEW = 2


_PrbInviteData = namedtuple('_PrbInviteData', ' '.join(['clientID',
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
 'prebattleID',
 'extraData',
 'alwaysAvailable',
 'ownerDBID',
 'expiryTime',
 'id']))

class PrbInviteWrapper(_PrbInviteData):

    @staticmethod
    def __new__(cls, clientID = -1L, createTime = None, type = 0, comment = str(), creator = str(), creatorDBID = -1L, creatorClanAbbrev = None, receiver = str(), receiverDBID = -1L, receiverClanAbbrev = None, state = None, count = 0, peripheryID = 0, prebattleID = 0, extraData = None, alwaysAvailable = None, ownerDBID = -1L, expiryTime = None, id = -1L, **kwargs):
        if ownerDBID < 0L:
            ownerDBID = creatorDBID
        result = _PrbInviteData.__new__(cls, clientID, createTime, type, comment, creator, creatorDBID, creatorClanAbbrev, receiver, receiverDBID, receiverClanAbbrev, state, count, peripheryID, prebattleID, extraData or {}, alwaysAvailable, ownerDBID, expiryTime, id)
        result.showAt = 0
        return result

    @property
    def senderFullName(self):
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
            if self.type in PREBATTLE_TYPE.UNIT_MGR_PREBATTLES and self._isCurrentPrebattle(unitFunctional):
                return True
            if self._isCurrentPrebattle(prbFunctional):
                return True
        return False

    def getCreateTime(self):
        if self.createTime is not None:
            return int(time_utils.makeLocalServerTime(self.createTime))
        else:
            return

    def getExpiryTime(self):
        if self.expiryTime is not None:
            return int(time_utils.makeLocalServerTime(self.expiryTime))
        else:
            return

    def getExtraData(self, key = None):
        if key is not None:
            return self.extraData.get(key)
        else:
            return self.extraData

    def isCreatedInBattle(self):
        return not self.isFromHangar()

    def isIncoming(self):
        return True

    def isActive(self):
        return self.getState() == PRB_INVITE_STATE.PENDING

    def isExpired(self):
        return False

    def getState(self):
        return PRB_INVITE_STATE.getFromOldState(self)

    def accept(self, callback = None):
        if connectionManager.peripheryID == self.peripheryID:
            BigWorld.player().prb_acceptInvite(self.prebattleID, self.peripheryID)
        else:
            LOG_ERROR('Invalid periphery', (self.prebattleID, self.peripheryID), connectionManager.peripheryID)

    def decline(self, callback = None):
        BigWorld.player().prb_declineInvite(self.prebattleID, self.peripheryID)

    def revoke(self, callback = None):
        LOG_WARNING('Old-style invite can not be revoked')

    @classmethod
    def getVersion(cls):
        return _INVITE_VERSION.OLD

    def isFromHangar(self):
        return True

    def isSameBattle(self, arenaUniqueID):
        return False

    def _isCurrentPrebattle(self, functional):
        return functional is not None and self.prebattleID == functional.getID()

    def _merge(self, other):
        data = {}
        if other.creator:
            data['creator'] = other.creator
        if other.creatorDBID > 0L:
            data['creatorDBID'] = other.creatorDBID
        if other.creatorClanAbbrev:
            data['creatorClanAbbrev'] = other.creatorClanAbbrev
        if other.createTime is not None:
            data['createTime'] = other.createTime
        if other.expiryTime:
            data['expiryTime'] = other.expiryTime
        if other.ownerDBID:
            data['ownerDBID'] = other.ownerDBID
        if other.id:
            data['id'] = other.id
        if other.extraData:
            data['extraData'] = other.extraData
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


class PrbInvitationWrapper(PrbInviteWrapper):

    @staticmethod
    def __new__(cls, clientID = -1L, id = -1L, type = 0, status = None, sentAt = None, expiresAt = None, ownerID = -1L, senderDBID = -1L, receiverDBID = -1L, info = None, sender = str(), senderClanAbbrev = None, receiver = str(), receiverClanAbbrev = None, **kwargs):
        info = info or {}
        peripheryID, prbID = cls.getPrbInfo(info)
        result = PrbInviteWrapper.__new__(cls, clientID, sentAt, type, info.get('comment', ''), sender, senderDBID, senderClanAbbrev, receiver, receiverDBID, receiverClanAbbrev, status, 1, peripheryID, prbID, info, False, ownerID, expiresAt, id, **kwargs)
        return result

    @classmethod
    def getPrbInfo(cls, inviteInfo):
        return (inviteInfo.get('peripheryID', 0), inviteInfo.get('unitMgrID', 0))

    @classmethod
    def getVersion(cls):
        return _INVITE_VERSION.NEW

    def isFromHangar(self):
        return self.extraData.get('arenaUniqueID') is None

    def isSameBattle(self, arenaUniqueID):
        invArenaUniqueID = self.extraData.get('arenaUniqueID')
        return invArenaUniqueID is not None and invArenaUniqueID == arenaUniqueID

    def isIncoming(self):
        return self.ownerDBID != getPlayerDatabaseID()

    def isExpired(self):
        expiryTime = self.getExpiryTime()
        return expiryTime is not None and expiryTime < time_utils.getCurrentTimestamp()

    def getState(self):
        return PRB_INVITE_STATE.getFromNewState(self)

    def accept(self, callback = None):
        if connectionManager.peripheryID == self.peripheryID:
            BigWorld.player().prebattleInvitations.acceptInvitation(self.id, self.creatorDBID, callback)
        else:
            LOG_ERROR('Invalid periphery', (self.prebattleID, self.peripheryID), connectionManager.peripheryID)

    def decline(self, callback = None):
        BigWorld.player().prebattleInvitations.declineInvitation(self.id, self.creatorDBID, callback)

    def revoke(self, callback = None):
        LOG_WARNING('Need to call valid Account method')


class _AcceptInvitesPostActions(ActionsChain):

    def __init__(self, invite, actions):
        self.invite = invite
        super(_AcceptInvitesPostActions, self).__init__(actions)


class PRB_INVITES_INIT_STEP(object):
    UNDEFINED = 0
    FRIEND_RECEIVED = 1
    IGNORED_RECEIVED = 2
    STARTED = 4
    DATA_BUILD = 8
    CONTACTS_RECEIVED = FRIEND_RECEIVED | IGNORED_RECEIVED
    INITED = CONTACTS_RECEIVED | DATA_BUILD | STARTED


def _getOldInvites():
    return getattr(BigWorld.player(), 'prebattleInvites', {})


def _getNewInvites():
    if hasattr(BigWorld.player(), 'prebattleInvitations'):
        return BigWorld.player().prebattleInvitations.getInvites()
    return {}


class InvitesManager(UsersInfoHelper):
    __clanInfo = None

    def __init__(self, loader):
        super(InvitesManager, self).__init__()
        self.__loader = loader
        self._IDGen = SequenceIDGenerator()
        self._IDMap = {}
        self.__invites = {}
        self.__unreadInvitesCount = 0
        self.__eventManager = Event.EventManager()
        self.__acceptChain = None
        self.onInvitesListInited = Event.Event(self.__eventManager)
        self.onReceivedInviteListModified = Event.Event(self.__eventManager)
        self.onSentInviteListModified = Event.Event(self.__eventManager)
        self.__isInBattle = False
        return

    def __del__(self):
        LOG_DEBUG('InvitesManager deleted')
        super(InvitesManager, self).__del__()

    def init(self):
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        g_messengerEvents.users.onUsersListReceived += self.__me_onUsersListReceived
        g_playerEvents.onPrebattleInvitesChanged += self.__pe_onPrebattleInvitesChanged
        g_playerEvents.onPrebattleInvitationsChanged += self.__pe_onPrebattleInvitationsChanged
        g_playerEvents.onPrebattleInvitesStatus += self.__pe_onPrebattleInvitesStatus

    def fini(self):
        self.__clearAcceptChain()
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        self.__loader = None
        g_messengerEvents.users.onUsersListReceived -= self.__me_onUsersListReceived
        g_playerEvents.onPrebattleInvitationsChanged -= self.__pe_onPrebattleInvitationsChanged
        g_playerEvents.onPrebattleInvitesChanged -= self.__pe_onPrebattleInvitesChanged
        g_playerEvents.onPrebattleInvitesStatus -= self.__pe_onPrebattleInvitesStatus
        self.clear()
        return

    def start(self):
        self.__isInBattle = False
        if self.__inited & PRB_INVITES_INIT_STEP.STARTED == 0:
            self.__inited |= PRB_INVITES_INIT_STEP.STARTED
            if self.__inited == PRB_INVITES_INIT_STEP.INITED:
                self.onInvitesListInited()

    def clear(self):
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        self.__clearInvites()
        self._IDMap = {}
        self.__eventManager.clear()

    def onAvatarBecomePlayer(self):
        self.__isInBattle = True
        self.__clearAcceptChain()

    @storage_getter('users')
    def users(self):
        return None

    def isInited(self):
        return self.__inited == PRB_INVITES_INIT_STEP.INITED

    def acceptInvite(self, inviteID, postActions = None):
        try:
            invite = self.__invites[inviteID]
        except KeyError:
            LOG_ERROR('Invite ID is invalid', inviteID, self._IDMap)
            return

        self.__clearAcceptChain()
        if not postActions:
            invite.accept()
        else:
            self.__acceptChain = _AcceptInvitesPostActions(invite, postActions)
            self.__acceptChain.onStopped += self.__accept_onPostActionsStopped
            self.__acceptChain.start()
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def declineInvite(self, inviteID):
        try:
            invite = self.__invites[inviteID]
        except KeyError:
            LOG_ERROR('Invite ID is invalid', inviteID, self._IDMap)
            return

        invite.decline()
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def revokeInvite(self, inviteID):
        try:
            invite = self.__invites[inviteID]
        except KeyError:
            LOG_ERROR('Invite ID is invalid', inviteID, self._IDMap)
            return

        invite.revoke()
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def canAcceptInvite(self, invite):
        result = False
        if invite.alwaysAvailable is True:
            result = True
        elif invite.clientID in self.__invites:
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
                    result = invite.clientID > 0 and invite.isActive()
            else:
                result = invite.clientID > 0 and invite.isActive()
        return result

    def canDeclineInvite(self, invite):
        result = False
        if invite.clientID in self.__invites:
            result = invite.clientID > 0 and invite.isActive()
        return result

    def canRevokeInvite(self, invite):
        result = False
        if invite.clientID in self.__invites:
            result = invite.clientID > 0 and invite.isActive() and invite.creatorDBID == getPlayerDatabaseID()
        return result

    def getInvites(self, incoming = None, version = None, onlyActive = None):
        result = self.__invites.values()
        if incoming is not None:
            result = filter(lambda item: item.isIncoming() is incoming, result)
        if version is not None:
            result = filter(lambda item: item.getVersion() == version, result)
        if onlyActive is not None:
            result = filter(lambda item: item.isActive() is onlyActive, result)
        return result

    def getInvite(self, inviteID):
        invite = None
        if inviteID in self.__invites:
            invite = self.__invites[inviteID]
        return invite

    def getReceivedInviteCount(self):
        return len(self.getReceivedInvites())

    def getReceivedInvites(self, IDs = None):
        result = self.getInvites(incoming=True)
        if IDs is not None:
            result = filter(lambda item: item.clientID in IDs, result)
        return result

    def getSentInvites(self, IDs = None):
        result = self.getInvites(incoming=False)
        if IDs is not None:
            result = filter(lambda item: item.clientID in IDs, result)
        return result

    def getSentInviteCount(self):
        return len(self.getSentInvites())

    def getUnreadCount(self):
        return self.__unreadInvitesCount

    def resetUnreadCount(self):
        self.__unreadInvitesCount = 0

    def onUserNamesReceived(self, names):
        updated = defaultdict(list)
        rosterGetter = self.users.getUser
        inviteMaker = self._getNewInviteMaker(rosterGetter)
        prebattleInvitations = _getNewInvites()
        for invite in self.getInvites(version=_INVITE_VERSION.NEW):
            if invite.creatorDBID in names or invite.receiverDBID in names:
                inviteData = prebattleInvitations.get(invite.id)
                inviteID, invite = inviteMaker(inviteData)
                if inviteData and self._updateInvite(invite, rosterGetter):
                    updated[invite.isIncoming()].append(inviteID)

        for isIncoming, event in ((True, self.onReceivedInviteListModified), (False, self.onSentInviteListModified)):
            if updated[isIncoming]:
                event([], updated[isIncoming], [])

    def _makeInviteID(self, prebattleID, peripheryID, senderDBID, receiverDBID):
        inviteKey = (prebattleID,
         peripheryID,
         senderDBID,
         receiverDBID)
        inviteID = self._IDMap.get(inviteKey)
        if inviteID is None:
            inviteID = self._IDGen.next()
            self._IDMap[inviteKey] = inviteID
        return inviteID

    def _addInvite(self, invite, userGetter):
        if self.__isInviteSenderIgnoredInBattle(invite, userGetter):
            return False
        self.__invites[invite.clientID] = invite
        if invite.isActive():
            self.__unreadInvitesCount += 1
        return True

    def _updateInvite(self, other, userGetter):
        inviteID = other.clientID
        invite = self.__invites[inviteID]
        if invite == other or self.__isInviteSenderIgnoredInBattle(invite, userGetter):
            return False
        prevCount = invite.count
        invite = invite._merge(other)
        self.__invites[inviteID] = invite
        if invite.isActive() and prevCount < invite.count:
            self.__unreadInvitesCount += 1
        return True

    def _delInvite(self, inviteID):
        result = inviteID in self.__invites
        if result:
            self.__invites.pop(inviteID)
        return result

    def _buildReceivedInvitesList(self, invitesLists):
        if self.__inited & PRB_INVITES_INIT_STEP.DATA_BUILD == 0:
            self.__inited |= PRB_INVITES_INIT_STEP.DATA_BUILD
        self.__clearInvites()
        userGetter = self.users.getUser
        for invitesData, maker in invitesLists:
            for item in invitesData:
                _, invite = maker(item)
                if invite:
                    self._addInvite(invite, userGetter)

        if not g_battleCtrl.isBattleUILoaded():
            self.syncUsersInfo()

    def _rebuildInvitesLists(self):
        rosterGetter = self.users.getUser
        self._buildReceivedInvitesList([(_getOldInvites().items(), self._getOldInviteMaker(rosterGetter)), (_getNewInvites().values(), self._getNewInviteMaker(rosterGetter))])

    def _getOldInviteMaker(self, rosterGetter):
        receiver = getPlayerName()
        receiverDBID = getPlayerDatabaseID()
        receiverClanAbbrev = g_lobbyContext.getClanAbbrev(self.__clanInfo)

        def _inviteMaker(item):
            (prebattleID, peripheryID), data = item
            inviteID = self._makeInviteID(prebattleID, peripheryID, data['creatorDBID'], receiverDBID)
            if data is not None:
                invite = PrbInviteWrapper(clientID=inviteID, receiver=receiver, receiverDBID=receiverDBID, receiverClanAbbrev=receiverClanAbbrev, peripheryID=peripheryID, prebattleID=prebattleID, **data)
            else:
                invite = None
            return (inviteID, invite)

        return _inviteMaker

    def _getNewInviteMaker(self, rosterGetter):

        def _getUserName(userDBID):
            name, abbrev = ('', None)
            if userDBID:
                if g_battleCtrl.isBattleUILoaded():
                    name, abbrev = g_battleCtrl.getCtx().getFullPlayerNameWithParts(accID=userDBID, showVehShortName=False)[1:3]
                if not name:
                    userName = self.getUserName(userDBID)
                    userClanAbbrev = self.getUserClanAbbrev(userDBID)
                    user = rosterGetter(userDBID)
                    if user and user.hasValidName():
                        name, abbrev = userName, userClanAbbrev
            return (name, abbrev)

        def _inviteMaker(item):
            peripheryID, prebattleID = PrbInvitationWrapper.getPrbInfo(item.get('info', {}))
            senderDBID = item.get('senderDBID', 0)
            receiverDBID = item.get('receiverDBID', 0)
            inviteID = self._makeInviteID(prebattleID, peripheryID, senderDBID, receiverDBID)
            senderName, senderClanAbbrev = _getUserName(senderDBID)
            receiverName, receiverClanAbbrev = _getUserName(receiverDBID)
            return (inviteID, PrbInvitationWrapper(inviteID, sender=senderName, senderClanAbbrev=senderClanAbbrev, receiver=receiverName, receiverClanAbbrev=receiverClanAbbrev, **item))

        return _inviteMaker

    def __initReceivedInvites(self):
        step = PRB_INVITES_INIT_STEP.CONTACTS_RECEIVED
        if self.__inited & step != step:
            return
        self._rebuildInvitesLists()
        if self.__inited == PRB_INVITES_INIT_STEP.INITED:
            self.onInvitesListInited()

    def __clearAcceptChain(self):
        if self.__acceptChain is not None:
            self.__acceptChain.onStopped -= self.__accept_onPostActionsStopped
            self.__acceptChain.stop()
            self.__acceptChain = None
        return

    def __me_onUsersListReceived(self, tags):
        doInit = False
        if USER_TAG.FRIEND in tags:
            doInit = True
            step = PRB_INVITES_INIT_STEP.FRIEND_RECEIVED
            if self.__inited & step == 0:
                self.__inited |= step
        if USER_TAG.IGNORED in tags:
            doInit = True
            step = PRB_INVITES_INIT_STEP.IGNORED_RECEIVED
            if self.__inited & step == 0:
                self.__inited |= step
        if doInit:
            self.__initReceivedInvites()

    def __pe_onPrebattleInvitesChanged(self, diff):
        step = PRB_INVITES_INIT_STEP.CONTACTS_RECEIVED
        if self.__inited & step != step:
            LOG_DEBUG('Received invites are ignored. Manager waits for client will receive contacts')
            return
        if ('prebattleInvites', '_r') in diff:
            self._rebuildInvitesLists()
        if 'prebattleInvites' in diff:
            self.__updateOldPrebattleInvites(_getOldInvites())

    def __pe_onPrebattleInvitationsChanged(self, invitations):
        step = PRB_INVITES_INIT_STEP.CONTACTS_RECEIVED
        if self.__inited & step != step:
            LOG_DEBUG('Received invites are ignored. Manager waits for client will receive contacts')
            return
        self.__updateNewPrebattleInvites(invitations)

    def __pe_onPrebattleInvitesStatus(self, dbID, name, status):
        if status != PREBATTLE_INVITE_STATUS.OK:
            statusName = PREBATTLE_INVITE_STATUS_NAMES[status]
            SystemMessages.pushI18nMessage('#system_messages:invite/status/%s' % statusName, name=name, type=SystemMessages.SM_TYPE.Warning)

    def __updateOldPrebattleInvites(self, prbInvites):
        added = []
        changed = []
        deleted = []
        modified = False
        rosterGetter = self.users.getUser
        inviteMaker = self._getOldInviteMaker(rosterGetter)
        for item in prbInvites.iteritems():
            inviteID, invite = inviteMaker(item)
            if invite is None:
                if self._delInvite(inviteID):
                    modified = True
                    deleted.append(inviteID)
                continue
            inList = inviteID in self.__invites
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

    def __updateNewPrebattleInvites(self, prbInvites):
        added = defaultdict(list)
        changed = defaultdict(list)
        deleted = defaultdict(list)
        modified = dict(((v, False) for v in (True, False)))
        rosterGetter = self.users.getUser
        inviteMaker = self._getNewInviteMaker(rosterGetter)
        newInvites = {}
        for data in prbInvites.itervalues():
            inviteID, invite = inviteMaker(data)
            if inviteID not in newInvites or invite.createTime > newInvites[inviteID].createTime:
                newInvites[inviteID] = invite

        for invite in self.getInvites(version=_INVITE_VERSION.NEW):
            inviteID = invite.clientID
            if inviteID not in newInvites and self._delInvite(inviteID):
                isIncoming = invite.isIncoming()
                modified[isIncoming] = True
                deleted[isIncoming].append(inviteID)
            else:
                continue

        for inviteID, invite in newInvites.iteritems():
            isIncoming = invite.isIncoming()
            if inviteID not in self.__invites:
                if self._addInvite(invite, rosterGetter):
                    modified[isIncoming] = True
                    added[isIncoming].append(inviteID)
            elif self._updateInvite(invite, rosterGetter):
                modified[isIncoming] = True
                changed[isIncoming].append(inviteID)

        for isIncoming, event in ((True, self.onReceivedInviteListModified), (False, self.onSentInviteListModified)):
            if modified[isIncoming]:
                event(added[isIncoming], changed[isIncoming], deleted[isIncoming])

        self.syncUsersInfo()

    def __accept_onPostActionsStopped(self, isCompleted):
        if not isCompleted:
            return
        invite = self.__acceptChain.invite
        invite.accept()
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def __clearInvites(self):
        self.__invites.clear()
        self.__unreadInvitesCount = 0

    def __isInviteSenderIgnoredInBattle(self, invite, userGetter):
        return isInviteSenderIgnoredInBattle(userGetter(invite.creatorDBID), g_settings.userPrefs.invitesFromFriendsOnly, invite.isCreatedInBattle())
