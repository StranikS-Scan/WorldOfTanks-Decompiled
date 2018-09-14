# Embedded file name: scripts/client/gui/clubs/items.py
from collections import namedtuple
import BigWorld
from ids_generators import SequenceIDGenerator
from helpers import i18n
from ClubDescr import ClubDescr
from club_shared import ClubStateHelper, ClubRolesHelper, ladderRating, CLUB_LIMITS, CLUB_INVITE_STATE as _CIS, EMBLEM_TYPE, ladderRatingLocal, CLUBS_SEASON_STATE
from dossiers2.custom.builders import getClubDossierDescr, getRated7x7DossierDescr
from gui.shared.utils import getPlayerDatabaseID
from gui.shared.utils.decorators import ReprInjector
from gui.shared.gui_items.dossier import ClubDossier, ClubMemberDossier
from gui.clubs import formatters as club_fmts
from gui.clubs.settings import MIN_MEMBERS_COUNT, getLeagueByDivision, TOP_DIVISION
from gui.clubs.settings import getLadderChevron16x16
from gui.clubs.restrictions import MemberPermissions, DefaultMemberPermissions, RestrictionsCollection
from messenger.storage import storage_getter

class _InvitesIDsManager(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.__idsGen = SequenceIDGenerator()
        self.__idsMap = {'inviteIDs': {},
         'clubIDs': {}}

    def getInviteID(self, clubDbID, userDbID, creationTime):
        uniqueID = (clubDbID, userDbID, creationTime)
        if uniqueID not in self.__idsMap['clubIDs']:
            inviteID, showAt = self.__idsGen.next(), None
            self.__idsMap['inviteIDs'][inviteID] = uniqueID
            self.__idsMap['clubIDs'][uniqueID] = (inviteID, showAt)
        else:
            inviteID, showAt = self.__idsMap['clubIDs'][uniqueID]
        return (inviteID, showAt)

    def setShowTime(self, inviteID, showAt):
        uniqueID = self.__idsMap['inviteIDs'][inviteID]
        self.__idsMap['clubIDs'][uniqueID] = (inviteID, showAt)


_g_invitesIDs = _InvitesIDsManager()

def clearInvitesIDs():
    _g_invitesIDs.clear()


class OtherPlayerClubInfo(namedtuple('OtherPlayerClubInfo', ['clubDBID',
 'joined_at',
 'clubName',
 'role',
 'emblemIDs',
 'division'])):

    def getClubDbID(self):
        return self.clubDBID

    def getClubUserName(self):
        return self.clubName

    def getDisivision(self):
        return self.division

    def getDivisionString(self):
        return club_fmts.getDivisionString(self.division)

    def getLadderChevron(self):
        return getLadderChevron16x16(self.division)

    def getLeagueString(self):
        return club_fmts.getLeagueString(getLeagueByDivision(self.division))

    def getRoleString(self):
        return club_fmts.getRoleUserName(self.role)

    def isInLadder(self):
        return self.division is not None

    def getEmblem32x32(self):
        return self.emblemIDs.get(EMBLEM_TYPE.SIZE_32x32)


class _ClubState(object):

    def __init__(self, state):
        self.__state = state

    def getState(self):
        return self.__state

    def isOpened(self):
        return ClubStateHelper.isOpenForApplicants(self.__state)

    def isClosed(self):
        return ClubStateHelper.isCloseForApplicants(self.__state)

    def isDisbanded(self):
        return ClubStateHelper.isClubDisbanded(self.__state)

    def __repr__(self):
        if self.isOpened():
            state = 'opened'
        elif self.isClosed():
            state = 'closed'
        elif self.isDisbanded():
            state = 'disbanded'
        else:
            state = 'unknown'
        return '%s(%d)' % (state, self.__state)


class _LadderInfo(namedtuple('_LadderInfo', ['division',
 'group',
 'position',
 'rating'])):

    def getDivision(self):
        if self.isInLadder():
            return self.division
        else:
            return None

    def getRatingPoints(self):
        if self.isInLadder():
            return ladderRatingLocal(self.rating, self.division)
        return 0

    def getGlobalRatingPoints(self):
        return ladderRating(self.rating)

    def getLeague(self):
        if self.isInLadder():
            return getLeagueByDivision(self.getDivision())
        else:
            return None

    def isInLadder(self):
        return self.group is not None and self.division is not None

    def isTop(self):
        return self.division == TOP_DIVISION


_ApplicantsRequirements = namedtuple('_ApplicantsRequirements', ['minWinRate', 'minBattleCount', 'description'])
_MemberExtra = namedtuple('_MemberExtra', ['timestamp', 'seasonDossierDescr', 'totalDossierDescr'])

@ReprInjector.simple(('getDbID', 'dbID'))

class _User(object):

    def __init__(self, dbID):
        self._dbID = dbID

    def getDbID(self):
        return self._dbID


@ReprInjector.withParent(('getRoleMask', 'role'), ('getJoiningTime', 'join'), ('isOwner', 'owner'))

class _Member(_User):

    def __init__(self, dbID, roleMask, extra, clubDbID = None):
        super(_Member, self).__init__(dbID)
        self.__roleMask = roleMask
        self.__extra = extra
        self.__clubDbID = clubDbID

    def getRoleMask(self):
        return self.__roleMask

    def getJoiningTime(self):
        return self.__extra.timestamp

    def getSeasonDossier(self):
        return ClubMemberDossier(self.__extra.seasonDossierDescr or '', self.__clubDbID, self._dbID)

    def getTotalDossier(self):
        return ClubMemberDossier(self.__extra.totalDossierDescr or '', self.__clubDbID, self._dbID)

    def isOwner(self):
        return ClubRolesHelper.isOwner(self.__roleMask)

    def isOfficer(self):
        return ClubRolesHelper.isOfficer(self.__roleMask)

    def isPrivate(self):
        return ClubRolesHelper.isPrivate(self.__roleMask)

    def getRoleUserName(self):
        return club_fmts.getRoleUserName(self.__roleMask)


@ReprInjector.simple(('getID', 'id'), ('getClubDbID', 'club'), ('getUserDbID', 'user'), ('getTimestamp', 'send'), ('isActive', 'active'), ('getUpdatingTime', 'updated'), ('getStatus', 'status'))

class _ClubInvitation(object):

    def __init__(self, clubDbID, userDbID, timestamp, status, updatingTime):
        self._id, self._showAt = _g_invitesIDs.getInviteID(clubDbID, userDbID, timestamp)
        self._clubDbID = clubDbID
        self._userDbID = userDbID
        self._timestamp = timestamp
        self._updatingTime = updatingTime
        self._status = status or _CIS.CANCELLED

    def getID(self):
        return self._id

    def getClubDbID(self):
        return self._clubDbID

    def getUserDbID(self):
        return self._userDbID

    def getTimestamp(self):
        return self._timestamp

    def getUpdatingTime(self):
        return self._updatingTime

    def isActive(self):
        return self._status == _CIS.ACTIVE

    def isAccepted(self):
        return self._status == _CIS.ACCEPTED

    def isDeclined(self):
        return self._status == _CIS.DECLINED

    def isCancelled(self):
        return self._status == _CIS.CANCELLED

    def showAt(self):
        return self._showAt

    def setShowTime(self, showAt):
        self._showAt = showAt
        _g_invitesIDs.setShowTime(self._id, showAt)

    def getStatus(self):
        return self._status

    def __cmp__(self, other):
        res = self._status - other.getStatus()
        if res:
            return res
        return self._timestamp - other.getTimestamp()


@ReprInjector.withParent(('getInviterDbID', 'inviter'))

class ClubInvite(_ClubInvitation):

    def __init__(self, clubDbID, userDbID, inviterDbID, timestamp, status, updatingTime):
        super(ClubInvite, self).__init__(clubDbID, userDbID, timestamp, status, updatingTime)
        self._inviterDbID = inviterDbID

    def getInviterDbID(self):
        return self._inviterDbID


@ReprInjector.withParent(('getComment', 'comment'))

class ClubApplication(_ClubInvitation):

    def __init__(self, clubDbID, userDbID, comment, timestamp, status, updatingTime):
        super(ClubApplication, self).__init__(clubDbID, userDbID, timestamp, status, updatingTime)
        self._comment = comment

    def getComment(self):
        return self._comment


def isApplication(invitation):
    return isinstance(invitation, ClubApplication)


def isInvite(invitation):
    return isinstance(invitation, ClubInvite)


class _UnitInfo(namedtuple('_UnitInfo', ['unitMgrID', 'peripheryID'])):

    def isInBattle(self):
        return False


class Club(object):

    def __init__(self, clubDbID, clubDescr):
        self._clubDescr = ClubDescr(clubDbID, clubDescr)
        self.__clubDbID = clubDbID
        self.__restrictions = RestrictionsCollection(self._clubDescr.restrictions)

    @storage_getter('users')
    def users(self):
        return None

    def getClubDbID(self):
        return self.__clubDbID

    def getDescriptor(self):
        return self._clubDescr

    def getUserName(self):
        return i18n.encodeUtf8(self._clubDescr.name)

    def getUserDescription(self):
        return i18n.encodeUtf8(self._clubDescr.description or '')

    def getUserShortDescription(self):
        return i18n.encodeUtf8(self._clubDescr.shortDescription or '')

    def getOwnerDbID(self):
        return self._clubDescr.owner

    def getOwner(self):
        return self.getMember(self._clubDescr.owner)

    def getState(self):
        return _ClubState(self._clubDescr.state)

    def getLadderInfo(self):
        return _LadderInfo(*self._clubDescr.ladder)

    def getEmblem16x16(self):
        return self._clubDescr.emblems.get(EMBLEM_TYPE.SIZE_16x16)

    def getEmblem24x24(self):
        return self._clubDescr.emblems.get(EMBLEM_TYPE.SIZE_24x24)

    def getEmblem32x32(self):
        return self._clubDescr.emblems.get(EMBLEM_TYPE.SIZE_32x32)

    def getEmblem64x64(self):
        return self._clubDescr.emblems.get(EMBLEM_TYPE.SIZE_64x64)

    def getEmblem256x256(self):
        return self._clubDescr.emblems.get(EMBLEM_TYPE.SIZE_256x256)

    def getApplicantsRequirements(self):
        return _ApplicantsRequirements(self._clubDescr.minWinRate, self._clubDescr.minBattleCount, self.getUserShortDescription())

    def hasMember(self, dbID):
        return dbID in self._clubDescr.members

    def isStaffed(self):
        return len(self._clubDescr.members) >= CLUB_LIMITS.MAX_MEMBERS

    def wasInRatedBattleThisSeason(self):
        return self.getSeasonDossier().getTotalStats().getBattlesCount() > 0

    def getMember(self, memberDbID = None):
        memberDbID = memberDbID or getPlayerDatabaseID()
        if self.hasMember(memberDbID):
            return self.__makeMemberItem(memberDbID, self._clubDescr.members[memberDbID])
        else:
            return None

    def getMembers(self):
        result = {}
        for memberDbID, roleMask in self._clubDescr.members.iteritems():
            result[memberDbID] = self.__makeMemberItem(memberDbID, roleMask)

        return result

    def getInvitation(self, invID):
        invites = self.getInvites()
        if invID in invites:
            return invites[invID]
        return self.getApplicants().get(invID)

    def getInvites(self, onlyActive = False):
        result = {}
        for inviteeDbID, data in self._clubDescr.invites.iteritems():
            timestamp, inviterDbID, status, updatingTime = data
            invite = ClubInvite(self.__clubDbID, inviteeDbID, inviterDbID, timestamp, status, updatingTime)
            if not onlyActive or invite.isActive():
                result[invite.getID()] = invite

        return result

    def getApplicants(self, onlyActive = False):
        result = {}
        for applicantDbID, data in self._clubDescr.applicants.iteritems():
            timestamp, comment, status, updatingTime = data
            app = ClubApplication(self.__clubDbID, applicantDbID, comment, timestamp, status, updatingTime)
            if not onlyActive or app.isActive():
                result[app.getID()] = app

        return result

    def getSeasonDossier(self):
        return ClubDossier(self._clubDescr.getDossierDescr()[0], self.__clubDbID)

    def getTotalDossier(self):
        return ClubDossier(self._clubDescr.getDossierDescr()[1], self.__clubDbID)

    def isChanged(self, newClub):
        return self._clubDescr.rev != newClub.getDescriptor().rev

    def getPermissions(self, memberDbID = None):
        if memberDbID is None:
            memberDbID = getPlayerDatabaseID()
        if self.hasMember(memberDbID):
            return MemberPermissions(self._clubDescr.members[memberDbID])
        else:
            return DefaultMemberPermissions()

    def getUnitInfo(self):
        from gui.clubs.club_helpers import getClubUnit
        unit = getClubUnit(self.__clubDbID)
        if unit is not None:
            return _UnitInfo(*unit)
        else:
            return

    def hasActiveUnit(self):
        return self.getUnitInfo() is not None

    def getRestrictions(self):
        return self.__restrictions

    def getCreationTime(self):
        return self._clubDescr.createdAt

    def canParticipateBattles(self):
        return len(self._clubDescr.members) >= MIN_MEMBERS_COUNT

    def __makeMemberItem(self, memberDbID, roleMask):
        return _Member(memberDbID, roleMask, clubDbID=self.__clubDbID, extra=_MemberExtra(*self._clubDescr.getMemberExtras(memberDbID)))

    def __repr__(self):
        return 'Club(dbID = %d, state = %s, members = %d)' % (self.__clubDbID, self.getState(), len(self.getMembers()))


class ClubListItem(object):

    def __init__(self, clubID, name, description, shortDescription, creatorID, membersCount, state, dossiers, ladder, minWinRate, minBattleCount):
        super(ClubListItem, self).__init__()
        self.__clubID = clubID
        self.__name = name
        self.__description = description
        self.__shortDescription = shortDescription
        self.__creatorID = creatorID
        self.__membersCount = membersCount
        self.__state = state
        self.__dossiers = dossiers
        self.__ladder = ladder
        self.__minWinRate = minWinRate
        self.__minBattleCount = minBattleCount

    def getID(self):
        return self.__clubID

    def getClubName(self):
        return self.__name

    def getCreatorID(self):
        return self.__creatorID

    def getRating(self):
        return _LadderInfo(*self.__ladder).getRatingPoints()

    def getMembersCount(self):
        return self.__membersCount

    def getCommandSize(self):
        return CLUB_LIMITS.MAX_MEMBERS

    def getDescription(self):
        return self.__description or ''

    def getShortDescription(self):
        return self.__shortDescription or ''

    def getDivision(self):
        return self.__ladder[0]

    @classmethod
    def build(cls, data):
        return cls(*data)


class ClubHistoryItem(namedtuple('ClubHistoryItem', ['clubDbID',
 'clubName',
 'joinTime',
 'leaveTime',
 'clubTotalDossier',
 'clubState',
 'clubRole'])):

    def getClubState(self):
        return _ClubState(self.clubState)

    def getFormattedDate(self):
        return BigWorld.wg_getShortDateFormat(self.joinTime) + ' - ' + BigWorld.wg_getShortDateFormat(self.leaveTime)

    def getTotalDossier(self):
        dossierDescr = getClubDossierDescr(self.clubTotalDossier or '')
        return ClubDossier(dossierDescr, self.clubDbID)

    @classmethod
    def build(cls, data):
        return cls(*data)


class ClubContenderItem(namedtuple('ClubContender', ['clubDBID',
 'clubName',
 'clubEmblemUrl',
 'ladderPoints',
 'ladderRank',
 'battlesCount',
 'winsCount'])):

    @classmethod
    def build(cls, data):
        return cls(*data)

    def getRatingPoints(self, division):
        return ladderRatingLocal(self.ladderPoints, division)


class SeasonState(object):

    def __init__(self, state):
        self.__state = state

    def isFinished(self):
        return self.__state == CLUBS_SEASON_STATE.INACTIVE

    def isSuspended(self):
        return self.__state == CLUBS_SEASON_STATE.SUSPENDED

    def isActive(self):
        return self.__state == CLUBS_SEASON_STATE.ACTIVE

    def getValue(self):
        return self.__state

    def getStateString(self):
        return CLUBS_SEASON_STATE.TO_TEXT.get(self.__state, 'UNKNOWN')

    def __repr__(self):
        return 'SeasonState(%s[%d])' % (self.getStateString(), self.__state)


class SeasonInfo(namedtuple('SeasonInfo', ['seasonID',
 'start',
 'finish',
 'dossierDescr'])):

    def getSeasonID(self):
        return self.seasonID

    def getDossierDescr(self):
        return getRated7x7DossierDescr(self.dossierDescr)

    def getUserName(self):
        return club_fmts.getSeasonUserName(self)

    def __cmp__(self, other):
        return other.start - self.start
