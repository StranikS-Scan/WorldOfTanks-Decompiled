# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/invites.py
import logging
from collections import namedtuple, defaultdict
import BigWorld
import Event
from PlayerEvents import g_playerEvents
from account_helpers import isRoamingEnabled
from constants import PREBATTLE_INVITE_STATUS, PREBATTLE_INVITE_STATUS_NAMES
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.prb_helpers import BadgesHelper
from gui.prb_control import prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import prb_seqs
from gui.prb_control.settings import PRB_INVITE_STATE
from gui.shared.actions import ActionsChain
from gui.shared.utils import getPlayerDatabaseID, getPlayerName, showInvitationInWindowsBar
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from helpers import dependency
from helpers import time_utils
from ids_generators import SequenceIDGenerator
from messenger import g_settings
from messenger.ext import isNotFriendSenderIgnored
from messenger.m_constants import USER_ACTION_ID, USER_TAG, UserEntityScope
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from messenger.ext.player_helpers import isCurrentPlayer
from predefined_hosts import g_preDefinedHosts
from shared_utils import CONST_CONTAINER
from shared_utils.account_helpers.ClientInvitations import UniqueId
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.game_control import IAnonymizerController
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class _InviteVersion(CONST_CONTAINER):
    OLD = 1
    NEW = 2


class _WarningType(object):
    ANONYMIZED = 'anonymized'


_PrbInviteData = namedtuple('_PrbInviteData', ('clientID',
 'createTime',
 'type',
 'comment',
 'creator',
 'creatorID',
 'creatorVehID',
 'creatorClanAbbrev',
 'creatorBadges',
 'receiver',
 'receiverID',
 'receiverClanAbbrev',
 'state',
 'count',
 'peripheryID',
 'prebattleID',
 'extraData',
 'alwaysAvailable',
 'ownerID',
 'expiryTime',
 'id'))

def isInviteSenderIgnored(user, areFriendsOnly, isFromBattle):
    return isNotFriendSenderIgnored(user, False) if isFromBattle else isNotFriendSenderIgnored(user, areFriendsOnly)


class PrbInviteWrapper(_PrbInviteData):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    __anonymizerController = dependency.descriptor(IAnonymizerController)

    @staticmethod
    def __new__(cls, clientID=-1, createTime=None, type=0, comment=str(), creator=str(), creatorID=None, creatorVehID=None, creatorClanAbbrev=None, creatorBadges=None, receiver=str(), receiverID=None, receiverClanAbbrev=None, state=None, count=0, peripheryID=0, prebattleID=0, extraData=None, alwaysAvailable=None, ownerID=None, expiryTime=None, id=-1, **kwargs):
        if ownerID is None:
            ownerID = creatorID
        badgesHelper = BadgesHelper(creatorBadges)
        result = _PrbInviteData.__new__(cls, clientID, createTime, type, comment, creator, creatorID, creatorVehID, creatorClanAbbrev, badgesHelper, receiver, receiverID, receiverClanAbbrev, state, count, peripheryID, prebattleID, extraData or {}, alwaysAvailable, ownerID, expiryTime, id)
        result.showAt = 0
        return result

    def __eq__(self, other):
        if isinstance(other, PrbInviteWrapper) and self.clientID == other.clientID and self.createTime == other.createTime and self.type == other.type and self.creatorID == other.creatorID and self.receiverID == other.receiverID and self.state == other.state and self.count == other.count and self.peripheryID == other.peripheryID and self.prebattleID == other.prebattleID:
            if self.id == other.id:
                return True
        return False

    @property
    def senderFullName(self):
        fullName = self.lobbyContext.getPlayerFullName(self.creator, clanAbbrev=self.creatorClanAbbrev)
        if fullName != '':
            fullName = '{}{}'.format(self.getCreatorBadgeImgStr(), fullName)
        return fullName

    @property
    def receiverFullName(self):
        return self.lobbyContext.getPlayerFullName(self.receiver, clanAbbrev=self.receiverClanAbbrev)

    @property
    def anotherPeriphery(self):
        return self.connectionMgr.peripheryID != self.peripheryID

    @property
    def alreadyJoined(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher:
            if self._isCurrentPrebattle(dispatcher.getEntity()):
                return True
        return False

    @property
    def warning(self):
        return _WarningType.ANONYMIZED if self.__anonymizerController.isAnonymized else ''

    def getCreatorBadgeID(self):
        return self.creatorBadges.getBadgeID()

    def getCreatorBadgeImgStr(self, size=24, vspace=-6):
        return self.creatorBadges.getBadgeImgStr(size, vspace)

    def getCreateTime(self):
        return int(time_utils.makeLocalServerTime(self.createTime)) if self.createTime is not None else None

    def getExpiryTime(self):
        return int(time_utils.makeLocalServerTime(self.expiryTime)) if self.expiryTime is not None else None

    def getExtraData(self, key=None):
        return self.extraData.get(key) if key is not None else self.extraData

    def isCreatedInBattle(self):
        return not self.isFromHangar()

    def isIncoming(self):
        return True

    def isActive(self):
        return self.getState() in (PRB_INVITE_STATE.PENDING, PRB_INVITE_STATE.POSTPONED)

    def isExpired(self):
        return False

    def getState(self):
        return PRB_INVITE_STATE.getFromOldState(self)

    def accept(self, callback=None):
        if self.connectionMgr.peripheryID == self.peripheryID:
            BigWorld.player().prb_acceptInvite(self.prebattleID, self.peripheryID)
        else:
            _logger.error('Invalid periphery. %s', ((self.prebattleID, self.peripheryID), self.connectionMgr.peripheryID))

    def decline(self, callback=None):
        BigWorld.player().prb_declineInvite(self.prebattleID, self.peripheryID)

    def revoke(self, callback=None):
        _logger.warning('Old-style invite can not be revoked')

    @classmethod
    def getVersion(cls):
        return _InviteVersion.OLD

    def isFromHangar(self):
        return True

    def isSameBattle(self, arenaUniqueID):
        return False

    def merge(self, other):
        return self._merge(other)

    def _isCurrentPrebattle(self, entity):
        return entity is not None and self.prebattleID == entity.getID()

    def _merge(self, other):
        data = {}
        if other.creator:
            data['creator'] = other.creator
        if other.creatorID is not None:
            data['creatorID'] = other.creatorID
        if other.creatorClanAbbrev:
            data['creatorClanAbbrev'] = other.creatorClanAbbrev
        if other.createTime is not None:
            data['createTime'] = other.createTime
        if other.expiryTime:
            data['expiryTime'] = other.expiryTime
        if other.ownerID:
            data['ownerID'] = other.ownerID
        if other.id:
            data['id'] = other.id
        if other.extraData:
            data['extraData'] = other.extraData
        data['state'] = other.state
        if other.count:
            data['count'] = other.count
        if other.comment or other.isActive():
            data['comment'] = other.comment
        return self._replaceEx(**data)

    def _replaceEx(self, **kwargs):
        result = self._replace(**kwargs)
        result.showAt = self.showAt
        return result


class PrbInvitationWrapper(PrbInviteWrapper):

    @staticmethod
    def __new__(cls, clientID=-1, id=-1, type=0, status=None, sentAt=None, expiresAt=None, ownerID=None, creatorID=None, senderVehID=None, receiverID=None, receiverSID=None, info=None, sender=str(), senderBadges=None, senderClanAbbrev=None, receiver=str(), receiverClanAbbrev=None, **kwargs):
        info = info or {}
        peripheryID, prbID = cls.getPrbInfo(info)
        result = PrbInviteWrapper.__new__(cls, clientID, sentAt, type, info.get('comment', ''), sender, creatorID, senderVehID, senderClanAbbrev, senderBadges, receiver, receiverID, receiverClanAbbrev, status, 1, peripheryID, prbID, info, False, ownerID, expiresAt, id, **kwargs)
        return result

    @classmethod
    def getPrbInfo(cls, inviteInfo):
        return (inviteInfo.get('peripheryID', 0), inviteInfo.get('unitMgrID', 0))

    @classmethod
    def getVersion(cls):
        return _InviteVersion.NEW

    def isFromHangar(self):
        return self.extraData.get('arenaUniqueID') is None

    def isSameBattle(self, arenaUniqueID):
        invArenaUniqueID = self.extraData.get('arenaUniqueID')
        return invArenaUniqueID is not None and invArenaUniqueID == arenaUniqueID

    def isIncoming(self):
        return not isCurrentPlayer(self.ownerID)

    def isExpired(self):
        expiryTime = self.getExpiryTime()
        return expiryTime is not None and expiryTime < time_utils.getCurrentTimestamp()

    def getState(self):
        return PRB_INVITE_STATE.getFromNewState(self)

    def accept(self, callback=None):
        if self.connectionMgr.peripheryID == self.peripheryID:
            BigWorld.player().prebattleInvitations.acceptInvitation(self.id, self.creatorVehID or self.creatorID, callback)
        else:
            _logger.error('Invalid periphery. %s', ((self.prebattleID, self.peripheryID), self.connectionMgr.peripheryID))

    def decline(self, callback=None):
        BigWorld.player().prebattleInvitations.declineInvitation(self.id, self.creatorVehID or self.creatorID, callback)

    def revoke(self, callback=None):
        _logger.warning('Need to call valid Account method')


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
    return BigWorld.player().prebattleInvitations.getInvites() if hasattr(BigWorld.player(), 'prebattleInvitations') else {}


class InvitesManager(UsersInfoHelper):
    __clanInfo = None
    itemsCache = dependency.descriptor(IItemsCache)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, loader):
        super(InvitesManager, self).__init__()
        self.__loader = loader
        self._IDGen = SequenceIDGenerator()
        self._IDMap = {}
        self.__invites = {}
        self.__invitesIgnored = {}
        self.__unreadInvitesCount = 0
        self.__eventManager = Event.EventManager()
        self.__acceptChain = None
        self.onInvitesListInited = Event.Event(self.__eventManager)
        self.onReceivedInviteListModified = Event.Event(self.__eventManager)
        self.onSentInviteListModified = Event.Event(self.__eventManager)
        self.__isInBattle = False
        return

    def __del__(self):
        _logger.debug('InvitesManager deleted')
        super(InvitesManager, self).__del__()

    def init(self):
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        g_messengerEvents.users.onUsersListReceived += self.__onUsersListReceived
        g_messengerEvents.users.onUserActionReceived += self.__onUserActionReceived
        g_messengerEvents.users.onBattleUserActionReceived += self.__onUserActionReceived
        g_playerEvents.onPrebattleInvitesChanged += self.__onPrebattleInvitesChanged
        g_playerEvents.onPrebattleInvitationsChanged += self.__onPrebattleInvitationsChanged
        g_playerEvents.onPrebattleInvitesStatus += self.__onPrebattleInvitesStatus

    def fini(self):
        self.__clearAcceptChain()
        self.__inited = PRB_INVITES_INIT_STEP.UNDEFINED
        self.__loader = None
        g_messengerEvents.users.onUsersListReceived -= self.__onUsersListReceived
        g_messengerEvents.users.onUserActionReceived -= self.__onUserActionReceived
        g_messengerEvents.users.onBattleUserActionReceived -= self.__onUserActionReceived
        g_playerEvents.onPrebattleInvitationsChanged -= self.__onPrebattleInvitationsChanged
        g_playerEvents.onPrebattleInvitesChanged -= self.__onPrebattleInvitesChanged
        g_playerEvents.onPrebattleInvitesStatus -= self.__onPrebattleInvitesStatus
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
        if self.__inited & PRB_INVITES_INIT_STEP.STARTED == 0:
            self.__inited |= PRB_INVITES_INIT_STEP.STARTED
            if self.__inited == PRB_INVITES_INIT_STEP.INITED:
                self.onInvitesListInited()
        self.__isInBattle = True
        self.__clearAcceptChain()

    @storage_getter('users')
    def users(self):
        return None

    def isInited(self):
        return self.__inited == PRB_INVITES_INIT_STEP.INITED

    def acceptInvite(self, inviteID, postActions=None):
        try:
            invite = self.__invites[inviteID]
        except KeyError:
            _logger.error('Invite ID is invalid. %s', (inviteID, self._IDMap))
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
            _logger.error('Invite ID is invalid. %s', (inviteID, self._IDMap))
            return

        invite.decline()
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def revokeInvite(self, inviteID):
        try:
            invite = self.__invites[inviteID]
        except KeyError:
            _logger.error('Invite ID is invalid. %s', (inviteID, self._IDMap))
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
                if invite.alreadyJoined:
                    return False
                if dispatcher.getEntity().hasLockedState():
                    return False
            another = invite.anotherPeriphery
            if another:
                if g_preDefinedHosts.periphery(invite.peripheryID) is None:
                    _logger.error('Periphery not found')
                    result = False
                elif self.lobbyContext.getCredentials() is None:
                    _logger.error('Login info not found')
                    result = False
                elif g_preDefinedHosts.isRoamingPeriphery(invite.peripheryID) and not isRoamingEnabled(self.itemsCache.items.stats.attributes):
                    _logger.error('Roaming is not supported')
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
            result = invite.clientID > 0 and invite.isActive() and isCurrentPlayer(invite.creatorID)
        return result

    def getInvites(self, incoming=None, version=None, onlyActive=None):
        result = self.__invites.values()
        if incoming is not None:
            result = [ item for item in result if item.isIncoming() is incoming ]
        if version is not None:
            result = [ item for item in result if item.getVersion() == version ]
        if onlyActive is not None:
            result = [ item for item in result if item.isActive() is onlyActive ]
        return result

    def getInvite(self, inviteID):
        invite = None
        if inviteID in self.__invites:
            invite = self.__invites[inviteID]
        return invite

    def getReceivedInviteCount(self):
        return len(self.getReceivedInvites())

    def getReceivedInvites(self, ids=None):
        result = self.getInvites(incoming=True)
        if ids is not None:
            result = [ item for item in result if item.clientID in ids ]
        return result

    def getSentInvites(self, ids=None):
        result = self.getInvites(incoming=False)
        if ids is not None:
            result = [ item for item in result if item.clientID in ids ]
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
        for invite in self.getInvites(version=_InviteVersion.NEW):
            if invite.creatorID in names or invite.receiverID in names:
                inviteUniqueId = UniqueId(id=invite.id, senderID=invite.creatorVehID or invite.creatorID)
                inviteData = prebattleInvitations.get(inviteUniqueId)
                inviteID, invite = inviteMaker(inviteData)
                if inviteData and self._updateInvite(invite):
                    updated[invite.isIncoming()].append(inviteID)

        for isIncoming, event in ((True, self.onReceivedInviteListModified), (False, self.onSentInviteListModified)):
            if updated[isIncoming]:
                event([], updated[isIncoming], [])

    def _makeInviteID(self, prebattleID, peripheryID, senderID, receiverID):
        inviteKey = (prebattleID,
         peripheryID,
         senderID,
         receiverID)
        inviteID = self._IDMap.get(inviteKey)
        if inviteID is None:
            inviteID = self._IDGen.next()
            self._IDMap[inviteKey] = inviteID
        return inviteID

    def _addInvite(self, invite, creator):
        if self.__isInviteSenderIgnored(invite, creator):
            self.__invitesIgnored[invite.clientID] = invite
            return False
        self.__invites[invite.clientID] = invite
        if invite.isActive():
            self.__unreadInvitesCount += 1
        return True

    def _updateInvite(self, other):
        inviteID = other.clientID
        isIgnored = False
        if inviteID in self.__invites:
            invite = self.__invites[inviteID]
        else:
            isIgnored = True
            invite = self.__invitesIgnored[inviteID]
        if invite == other:
            return False
        if isIgnored:
            invite = invite.merge(other)
            self.__invitesIgnored[inviteID] = invite
            return False
        prevCount = invite.count
        invite = invite.merge(other)
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
        for invitesData, maker in invitesLists:
            for item in invitesData:
                _, invite = maker(item)
                if invite:
                    creator = self.users.getUser(invite.creatorID, scope=UserEntityScope.BATTLE if invite.creatorVehID is not None else UserEntityScope.LOBBY)
                    self._addInvite(invite, creator)

        if self.appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE:
            self.syncUsersInfo()
        return

    def _rebuildInvitesLists(self):
        rosterGetter = self.users.getUser
        self._buildReceivedInvitesList([(_getOldInvites().items(), self._getOldInviteMaker()), (_getNewInvites().values(), self._getNewInviteMaker(rosterGetter))])

    def _getOldInviteMaker(self):
        receiver = getPlayerName()
        receiverID = getPlayerDatabaseID()
        receiverClanAbbrev = self.lobbyContext.getClanAbbrev(self.__clanInfo)

        def _inviteMaker(item):
            (prebattleID, peripheryID), data = item
            creatorID = data['creatorDBID']
            inviteID = self._makeInviteID(prebattleID, peripheryID, creatorID, receiverID)
            if data is not None:
                invite = PrbInviteWrapper(clientID=inviteID, creatorID=creatorID, receiver=receiver, receiverID=receiverID, receiverClanAbbrev=receiverClanAbbrev, peripheryID=peripheryID, prebattleID=prebattleID, **data)
            else:
                invite = None
            return (inviteID, invite)

        return _inviteMaker

    def _getNewInviteMaker(self, rosterGetter):

        def _getUserName(userID, scope):
            name, abbrev = ('', None)
            if userID:
                if self.appLoader.getSpaceID() == GuiGlobalSpaceID.BATTLE:
                    ctx = self.sessionProvider.getCtx()
                    isUserInBattle = ctx.getVehIDBySessionID(userID) != 0
                    if isUserInBattle:
                        name, abbrev = ctx.getPlayerFullNameParts(avatarSessionID=userID, showVehShortName=False)[1:3]
                if not name:
                    userName = self.getUserName(userID, scope)
                    userClanAbbrev = self.getUserClanAbbrev(userID)
                    user = rosterGetter(userID, scope=scope)
                    if user and user.hasValidName():
                        name, abbrev = userName, userClanAbbrev
            return (name, abbrev)

        def _inviteMaker(item):
            peripheryID, prebattleID = PrbInvitationWrapper.getPrbInfo(item.get('info', {}))
            creatorIDScope = UserEntityScope.LOBBY
            receiverIDScope = UserEntityScope.LOBBY
            creatorID = item.get('senderDBID', 0)
            receiverID = item.get('receiverDBID', 0)
            if creatorID <= 0:
                if self.appLoader.getSpaceID() == GuiGlobalSpaceID.BATTLE:
                    ctx = self.sessionProvider.getCtx()
                    if 'senderVehID' in item:
                        creatorID = ctx.getSessionIDByVehID(item['senderVehID'])
                        creatorIDScope = UserEntityScope.BATTLE
            else:
                item['senderVehID'] = 0
            if receiverID <= 0:
                if self.appLoader.getSpaceID() == GuiGlobalSpaceID.BATTLE:
                    ctx = self.sessionProvider.getCtx()
                    if 'receiverVehID' in item:
                        receiverID = ctx.getSessionIDByVehID(item['receiverVehID'])
                        receiverIDScope = UserEntityScope.BATTLE
            else:
                item['receiverVehID'] = 0
            inviteID = self._makeInviteID(prebattleID, peripheryID, creatorID, receiverID)
            senderName, senderClanAbbrev = _getUserName(creatorID, creatorIDScope)
            receiverName, receiverClanAbbrev = _getUserName(receiverID, receiverIDScope)
            return (inviteID, PrbInvitationWrapper(inviteID, creatorID=creatorID, sender=senderName, senderClanAbbrev=senderClanAbbrev, receiverID=receiverID, receiver=receiverName, receiverClanAbbrev=receiverClanAbbrev, **item))

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

    def __onUsersListReceived(self, tags):
        doInit = False
        if USER_TAG.FRIEND in tags:
            doInit = True
            step = PRB_INVITES_INIT_STEP.FRIEND_RECEIVED
            if self.__inited & step == 0:
                self.__inited |= step
        if USER_TAG.IGNORED in tags or USER_TAG.IGNORED_TMP in tags:
            doInit = True
            step = PRB_INVITES_INIT_STEP.IGNORED_RECEIVED
            if self.__inited & step == 0:
                self.__inited |= step
        if doInit:
            self.__initReceivedInvites()

    def __onUserActionReceived(self, actionID, user, *args):
        if actionID in (USER_ACTION_ID.IGNORED_REMOVED, USER_ACTION_ID.TMP_IGNORED_REMOVED):
            self.__refreshIgnoredInvitesRemove(user)
        if actionID in (USER_ACTION_ID.IGNORED_ADDED, USER_ACTION_ID.TMP_IGNORED_ADDED):
            self.__refreshIgnoredInvitesAdd(user)

    def __onPrebattleInvitesChanged(self, diff):
        step = PRB_INVITES_INIT_STEP.CONTACTS_RECEIVED
        if self.__inited & step != step:
            _logger.debug('Received invites are ignored. Manager waits for client will receive contacts')
            return
        if ('prebattleInvites', '_r') in diff:
            self._rebuildInvitesLists()
        if 'prebattleInvites' in diff:
            self.__updateOldPrebattleInvites(_getOldInvites())

    def __onPrebattleInvitationsChanged(self, invitations):
        step = PRB_INVITES_INIT_STEP.CONTACTS_RECEIVED
        if self.__inited & step != step:
            _logger.debug('Received invites are ignored. Manager waits for client will receive contacts')
            return
        self.__updateNewPrebattleInvites(invitations)

    @staticmethod
    def __onPrebattleInvitesStatus(dbID, name, status):
        if status != PREBATTLE_INVITE_STATUS.OK:
            statusName = PREBATTLE_INVITE_STATUS_NAMES[status]
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.invite.status.dyn(statusName)()), name=name, type=SystemMessages.SM_TYPE.Warning)

    def __updateOldPrebattleInvites(self, prbInvites):
        added = []
        changed = []
        deleted = []
        modified = False
        inviteMaker = self._getOldInviteMaker()
        for item in prbInvites.iteritems():
            inviteID, invite = inviteMaker(item)
            if invite is None:
                if self._delInvite(inviteID):
                    modified = True
                    deleted.append(inviteID)
                continue
            inList = inviteID in self.__invites or inviteID in self.__invitesIgnored
            if not inList:
                creator = self.users.getUser(invite.creatorID)
                if self._addInvite(invite, creator):
                    modified = True
                    added.append(inviteID)
            if self._updateInvite(invite):
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
            if self.appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE and invite.creatorVehID:
                continue
            if inviteID not in newInvites or invite.createTime > newInvites[inviteID].createTime:
                newInvites[inviteID] = invite

        for invite in self.getInvites(version=_InviteVersion.NEW):
            inviteID = invite.clientID
            if (self.appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE and invite.creatorVehID or inviteID not in newInvites) and self._delInvite(inviteID):
                isIncoming = invite.isIncoming()
                modified[isIncoming] = True
                deleted[isIncoming].append(inviteID)

        for inviteID, invite in newInvites.iteritems():
            isIncoming = invite.isIncoming()
            if inviteID not in self.__invites and inviteID not in self.__invitesIgnored:
                creator = rosterGetter(invite.creatorID, scope=UserEntityScope.BATTLE if invite.creatorVehID is not None else UserEntityScope.LOBBY)
                if self._addInvite(invite, creator):
                    modified[isIncoming] = True
                    added[isIncoming].append(inviteID)
            if self._updateInvite(invite):
                modified[isIncoming] = True
                changed[isIncoming].append(inviteID)

        for isIncoming, event in ((True, self.onReceivedInviteListModified), (False, self.onSentInviteListModified)):
            if modified[isIncoming]:
                event(added[isIncoming], changed[isIncoming], deleted[isIncoming])

        if self.appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE:
            self.syncUsersInfo()
        return

    def __accept_onPostActionsStopped(self, isCompleted):
        if not isCompleted:
            return
        invite = self.__acceptChain.invite
        invite.accept()
        if self.__unreadInvitesCount > 0:
            self.__unreadInvitesCount -= 1

    def __clearInvites(self):
        self.__invites.clear()
        self.__invitesIgnored.clear()
        self.__unreadInvitesCount = 0

    def __isInviteSenderIgnored(self, invite, user):
        if self.__isInBattle and invite.isIncoming():
            arenaDP = self.sessionProvider.getArenaDP()
            if arenaDP and arenaDP.getVehicleInfo().prebattleID > 0:
                return True
        return isInviteSenderIgnored(user, g_settings.userPrefs.invitesFromFriendsOnly, invite.isCreatedInBattle())

    def __refreshIgnoredInvitesRemove(self, user):
        invitations = []
        for invite in self.__invitesIgnored.itervalues():
            if invite.creatorID == user.getID():
                invitations.append(invite.clientID)

        for inviteID in invitations:
            self.__invites[inviteID] = self.__invitesIgnored.pop(inviteID)

        self.onReceivedInviteListModified(invitations, [], [])
        if self.appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE:
            self.syncUsersInfo()

    def __refreshIgnoredInvitesAdd(self, user):
        invitations = []
        for invite in self.__invites.itervalues():
            if invite.creatorID == user.getID():
                invitations.append(invite.clientID)

        for inviteID in invitations:
            self.__invitesIgnored[inviteID] = self.__invites.pop(inviteID)

        self.onReceivedInviteListModified([], [], invitations)
        if self.appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE:
            self.syncUsersInfo()


class AutoInvitesNotifier(object):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, loader):
        super(AutoInvitesNotifier, self).__init__()
        self.__notified = set()
        self.__isStarted = False
        self.__loader = loader

    def __del__(self):
        _logger.debug('AutoInvitesNotifier deleted')

    def start(self):
        if self.__isStarted:
            self.__doNotify()
            return
        self.__isStarted = True
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__pe_onPrbAutoInvitesChanged
        self.__doNotify()

    def stop(self):
        if not self.__isStarted:
            return
        self.__isStarted = False
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.__pe_onPrbAutoInvitesChanged
        self.__notified.clear()

    def fini(self):
        self.stop()
        self.__loader = None
        return

    def getNotified(self):
        result = []
        for invite in prb_seqs.AutoInvitesIterator():
            if invite.prbID in self.__notified:
                result.append(invite)

        return result

    @classmethod
    def hasInvite(cls, prbID):
        return prbID in prb_getters.getPrebattleAutoInvites()

    @classmethod
    def getInvite(cls, prbID):
        return prb_seqs.AutoInviteItem(prbID, **prb_getters.getPrebattleAutoInvites().get(prbID, {}))

    def canAcceptInvite(self, invite):
        result = True
        dispatcher = self.__loader.getDispatcher()
        if dispatcher is not None and dispatcher.getEntity().hasLockedState():
            result = False
        peripheryID = invite.peripheryID
        if result and self.lobbyContext.isAnotherPeriphery(peripheryID):
            result = self.lobbyContext.isPeripheryAvailable(peripheryID)
        return result

    def __doNotify(self):
        haveInvites = False
        for invite in prb_seqs.AutoInvitesIterator():
            prbID = invite.prbID
            haveInvites = True
            if prbID in self.__notified:
                continue
            if not invite.description:
                continue
            g_eventDispatcher.fireAutoInviteReceived(invite)
            showInvitationInWindowsBar()
            self.__notified.add(prbID)

        if not haveInvites:
            self.__notified.clear()

    def __pe_onPrbAutoInvitesChanged(self):
        self.__doNotify()
