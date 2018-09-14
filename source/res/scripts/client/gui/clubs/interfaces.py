# Embedded file name: scripts/client/gui/clubs/interfaces.py
from gui.clubs.settings import CLIENT_CLUB_RESTRICTIONS, error

class IClubListener(object):

    def onClubsSeasonStateChanged(self, seasonState):
        pass

    def onCompletedSeasonsInfoChanged(self):
        pass

    def onAccountClubRelationChanged(self, isRelatedToClubs):
        pass

    def onAccountClubInvitesInited(self, invites):
        pass

    def onAccountClubInvitesChanged(self, added, removed, changed):
        pass

    def onAccountClubAppsInited(self, apps):
        pass

    def onAccountClubAppsChanged(self, apps):
        pass

    def onAccountClubStateChanged(self, state):
        pass

    def onAccountClubRestrictionsChanged(self):
        pass

    def onClubUpdated(self, club):
        pass

    def onClubInvitesChanged(self, invites):
        pass

    def onClubSubscriptionStateChanged(self, newState, prevState):
        pass

    def onClubStateChanged(self, state):
        pass

    def onClubCreated(self, clubDBID):
        pass

    def onClubNameChanged(self, name):
        pass

    def onClubDescriptionChanged(self, description):
        pass

    def onClubEmblemsChanged(self, emblems):
        pass

    def onClubOwnerChanged(self, ownerDbID):
        pass

    def onClubLadderInfoChanged(self, ladderInfo):
        pass

    def onClubDossierChanged(self, seasonDossier, totalDossier):
        pass

    def onClubApplicantsRequirementsChanged(self, reqsInfo):
        pass

    def onClubMembersChanged(self, members):
        pass

    def onClubApplicantsChanged(self, applicants):
        pass

    def onClubUnitInfoChanged(self, unitInfo):
        pass

    def onClubRestrictionsChanged(self, restrictions):
        pass

    def _onClubsStateChanged(self, state):
        pass


class IClubValueComparator(object):

    def __call__(self, clubsCtrl, oldClub, newClub):
        pass


class IAccountClubLimits(object):

    def canCreateClub(self, profile):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canAcceptInvite(self, profile, inviteID):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canDeclineInvite(self, profile, inviteID):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canSendApplication(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canRevokeApplication(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canSeeContenders(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canSeeOtherPlayerInfo(self, profile, club = None, userDbID = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canGetClubSeasons(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canDestroyClub(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canLeaveClub(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canOpenClub(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canCloseClub(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canSendInvite(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canRevokeInvite(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canAcceptApplication(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canDeclineApplication(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canJoinUnit(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canCreateUnit(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canSeeApplicants(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canTransferOwnership(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canAssignOfficer(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canAssignPrivate(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canKickMember(self, profile, club = None, memberDbID = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canChangeClubRequirements(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)

    def canChangeWebSettings(self, profile, club = None):
        return error(CLIENT_CLUB_RESTRICTIONS.DEFAULT)
