# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationInvitesAndRequestsWindow.py
from collections import namedtuple
from debug_utils import LOG_DEBUG, LOG_ERROR
from adisp import process
from gui import SystemMessages
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.view_helpers import UsersInfoHelper
from gui.shared.formatters import text_styles
from gui.clubs import contexts as club_ctx, formatters as club_fmts
from gui.clubs.items import isInvite
from gui.clubs.club_helpers import ClubListener
from gui.clubs.settings import CLIENT_CLUB_STATE
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.daapi.view.meta.StaticFormationInvitesAndRequestsMeta import StaticFormationInvitesAndRequestsMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT

def _getAppDescr(reqs):
    return reqs.description or CYBERSPORT.WINDOW_UNIT_DESCRIPTIONDEFAULT


_DataItem = namedtuple('_DataItem', ['id',
 'fullname',
 'rating',
 'accept',
 'reject',
 'waiting',
 'status'])

def _formatInviteStatus(invitation):
    if invitation.isAccepted():
        return text_styles.success('#cybersport:InvitesAndRequestsWindow/accepted')
    if invitation.isDeclined():
        return text_styles.error('#cybersport:InvitesAndRequestsWindow/rejected')
    if invitation.isCancelled():
        return text_styles.error('#cybersport:InvitesAndRequestsWindow/cancelled')
    return ''


class _DataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(_DataProvider, self).__init__()
        self._list = []

    @property
    def collection(self):
        return self._list

    def buildList(self, data):
        self._list = []
        for item in data:
            self._list.append({'id': item.id,
             'name': item.fullname,
             'rating': item.rating,
             'showAcceptBtn': item.accept,
             'showRejectBtn': item.reject,
             'status': item.status,
             'showProgressIndicator': item.waiting})

    def emptyItem(self):
        return None

    def clearList(self):
        while len(self._list):
            self._list.pop()

        self._list = None
        return


class StaticFormationInvitesAndRequestsWindow(StaticFormationInvitesAndRequestsMeta, ClubListener, UsersInfoHelper):

    def __init__(self, ctx = None):
        super(StaticFormationInvitesAndRequestsWindow, self).__init__()
        raise 'clubDbID' in ctx or AssertionError
        self.__clubDbID = ctx['clubDbID']
        self.__isOnlyInvites = False
        self.__dataProvider = _DataProvider()

    def onWindowClose(self):
        self.destroy()

    def setShowOnlyInvites(self, onlyInvites):
        self.__isOnlyInvites = onlyInvites
        self.__updateMembers()

    @process
    def setDescription(self, description):
        self._showWaiting('clubs/invitations/requirements/change')
        yield lambda callback: callback(None)
        if description is not None:
            yield self.clubsCtrl.sendRequest(club_ctx.SetApplicantsRequirements(self.__clubDbID, description=description))
        self.as_hideWaitingS()
        return

    @process
    def resolvePlayerRequest(self, inviteID, isAccepted):
        self._showWaiting('clubs/invitations/list/change')
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club is not None:
            invitation = club.getInvitation(inviteID)
            playerDbID = invitation.getUserDbID()
            if isInvite(invitation):
                result = yield self.clubsCtrl.sendRequest(club_ctx.RevokeInviteCtx(club.getClubDbID(), playerDbID))
                sysMsg = club_fmts.getInviteRevokeSysMsg()
            elif isAccepted:
                result = yield self.clubsCtrl.sendRequest(club_ctx.AcceptApplicationCtx(club.getClubDbID(), playerDbID))
                sysMsg = club_fmts.getAppAcceptSysMsg(self.getUserFullName(playerDbID))
            else:
                result = yield self.clubsCtrl.sendRequest(club_ctx.DeclineApplicationCtx(club.getClubDbID(), playerDbID))
                sysMsg = club_fmts.getAppDeclineSysMsg(self.getUserFullName(playerDbID))
            if result.isSuccess():
                SystemMessages.pushMessage(sysMsg)
        else:
            LOG_ERROR('No club attached', inviteID, isAccepted)
        self.as_hideWaitingS()
        return

    def onUserNamesReceived(self, names):
        if not self.isDisposed():
            self.__updateMembers()

    def onUserRatingsReceived(self, ratings):
        if not self.isDisposed():
            self.__updateMembers()

    def onClubApplicantsRequirementsChanged(self, reqsInfo):
        self.as_setTeamDescriptionS(_getAppDescr(reqsInfo))

    def onClubApplicantsChanged(self, _):
        self.__updateMembers()

    def onClubInvitesChanged(self, _):
        self.__updateMembers()

    def onClubUpdated(self, _):
        self.__updateHeader()
        self.__updateMembers()

    def onAccountClubStateChanged(self, state):
        if state.getStateID() == CLIENT_CLUB_STATE.UNKNOWN:
            self.destroy()
        else:
            self.__updateHeader()

    def onAccountClubRestrictionsChanged(self):
        limits = self.clubsState.getLimits()
        profile = self.clubsCtrl.getProfile()
        if not limits.canSendInvite(profile, self.clubsCtrl.getClub(self.__clubDbID)):
            self.destroy()
        else:
            self.__updateHeader()

    def onClubRestrictionsChanged(self, restrictions):
        self.onAccountClubRestrictionsChanged()

    def _populate(self):
        super(StaticFormationInvitesAndRequestsWindow, self)._populate()
        self.startClubListening(self.__clubDbID)
        self.as_setTeamDescriptionS('')
        self._showWaiting('club/apps/get')
        self.__dataProvider.setFlashObject(self.as_getDataProviderS())
        self.__updateHeader()
        self.__updateMembers(syncUserData=True)

    def _dispose(self):
        self.stopClubListening(self.__clubDbID)
        super(StaticFormationInvitesAndRequestsWindow, self)._dispose()

    def __updateHeader(self):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club is not None:
            limits = self.clubsState.getLimits()
            profile = self.clubsCtrl.getProfile()
            permissions = club.getPermissions()
            appReqs = club.getApplicantsRequirements()
            if permissions.isOwner():
                header = CYBERSPORT.INVITESANDREQUESTSWINDOW_OWNERDESCRIPTION
                description = _getAppDescr(appReqs)
            else:
                header = CYBERSPORT.INVITESANDREQUESTSWINDOW_OFFICERDESCRIPTION
                description = ''
            self.as_setStaticDataS({'windowDescription': header,
             'isTeamDescriptionEditable': limits.canChangeClubRequirements(profile, club).success,
             'teamDescription': description,
             'tableHeader': self._createTableHeader()})
        return

    def _createTableHeader(self):
        return [self._createTableBtnInfo('name', CYBERSPORT.INVITESANDREQUESTSWINDOW_PLAYERNAME, CYBERSPORT.INVITESANDREQUESTSWINDOW_PLAYERNAME, 175), self._createTableBtnInfo('rating', '', CYBERSPORT.INVITESANDREQUESTSWINDOW_PLAYERNAME, 81, iconSource=RES_ICONS.MAPS_ICONS_STATISTIC_RATING24), self._createTableBtnInfo('status', CYBERSPORT.INVITESANDREQUESTSWINDOW_STATUS, CYBERSPORT.INVITESANDREQUESTSWINDOW_STATUS, 139, showSeparator=False)]

    def _createTableBtnInfo(self, id, label, toolTip, buttonWidth, iconSource = '', showSeparator = True):
        return {'id': id,
         'label': label,
         'iconSource': iconSource,
         'toolTip': toolTip,
         'buttonWidth': buttonWidth,
         'showSeparator': showSeparator,
         'buttonHeight': 30}

    def __updateMembers(self, syncUserData = False):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club is not None:
            invites = []
            apps = []
            limits = self.clubsState.getLimits()
            profile = self.clubsCtrl.getProfile()
            if not self.__isOnlyInvites:
                for app in sorted(club.getApplicants().itervalues()):
                    dbID = app.getUserDbID()
                    if app.isActive():
                        canAccept = limits.canAcceptApplication(profile, club).success
                        canDecline = limits.canDeclineApplication(profile, club).success
                    else:
                        canAccept = canDecline = False
                    apps.append(_DataItem(app.getID(), self.getGuiUserFullName(dbID), self.getUserRating(dbID), canAccept, canDecline, False, _formatInviteStatus(app)))

            for invite in sorted(club.getInvites().itervalues()):
                dbID = invite.getUserDbID()
                if invite.isActive():
                    canRevoke = limits.canRevokeInvite(profile, club).success
                else:
                    canRevoke = False
                invites.append(_DataItem(invite.getID(), self.getGuiUserFullName(dbID), self.getUserRating(dbID), False, canRevoke, invite.isActive(), _formatInviteStatus(invite)))

            if syncUserData:
                self.syncUsersInfo()
            self.__dataProvider.buildList(invites + apps)
            self.__dataProvider.refresh()
            self.as_hideWaitingS()
        return

    def _showWaiting(self, key):
        self.as_showWaitingS('#waiting:%s' % key, {})
