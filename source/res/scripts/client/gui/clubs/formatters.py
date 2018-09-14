# Embedded file name: scripts/client/gui/clubs/formatters.py
from helpers.i18n import makeString, doesTextExist
from club_shared import ClubRolesHelper
from gui import makeHtmlString
from gui.clubs.settings import CLUB_REQUEST_TYPE, getDivisionWithinLeague, getInviteStatusString
from messenger.storage import storage_getter

def getDivisionString(division):
    return chr(ord('A') + getDivisionWithinLeague(division))


def getLeagueString(league):
    return str(league + 1)


def getRequestUserName(rqTypeID):
    return _sysMsg('club/request/name/%s' % CLUB_REQUEST_TYPE.getKeyByValue(rqTypeID))


def getRoleUserName(clubRole):
    if ClubRolesHelper.isOwner(clubRole):
        key = 'owner'
    elif ClubRolesHelper.isOfficer(clubRole):
        key = 'officer'
    else:
        key = 'private'
    return makeString('#cybersport:clubs/roles/%s' % key)


class ClubInviteHtmlTextFormatter(object):

    @storage_getter('users')
    def users(self):
        return None

    def getTitle(self, invite):
        user = self.users.getUser(invite.getInviterDbID())
        if user:
            creatorFullName = user.getFullName()
        else:
            creatorFullName = ''
        if creatorFullName:
            creatorFullName = makeHtmlString('html_templates:lobby/prebattle', 'inviteTitleCreatorName', ctx={'name': creatorFullName})
        return makeHtmlString('html_templates:lobby/clubs', 'inviteTitle', ctx={'sender': creatorFullName})

    def getComment(self, invite):
        return makeHtmlString('html_templates:lobby/clubs', 'inviteComment', {'eventType': 'showClubProfile'})

    def getNote(self, invite):
        note = ''
        if len(note):
            note = makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': note})
        return note

    def getState(self, invite):
        stateString = getInviteStatusString(invite.getStatus())
        key = '#invites:clubs/state/%s' % stateString
        if not doesTextExist(key):
            return ''
        state = makeString(key)
        if state:
            state = makeHtmlString('html_templates:lobby/clubs', 'inviteState', {'state': state})
        return state

    def getText(self, invite):
        result = []
        text = self.getTitle(invite)
        if len(text):
            result.append(text)
        text = self.getComment(invite)
        if len(text):
            result.append(text)
        text = self.getNote(invite)
        if len(text):
            result.append(text)
        text = self.getState(invite)
        if len(text):
            result.append(text)
        return ''.join(result)


class ClubAppsHtmlTextFormatter(object):

    def getTitle(self):
        return makeHtmlString('html_templates:lobby/clubs', 'appsTitle')

    def getComment(self, appsCount):
        return makeHtmlString('html_templates:lobby/clubs', 'appsComment', {'appsCount': appsCount})

    def getText(self, appsCount):
        result = []
        text = self.getTitle()
        if len(text):
            result.append(text)
        text = self.getComment(appsCount)
        if len(text):
            result.append(text)
        return ''.join(result)


def getRequestErrorMsg(errorMsg):
    key = '#system_messages:clubs/request/errors/%s' % errorMsg
    if doesTextExist(key):
        return makeString(key)
    return ''


def getAppSentSysMsg(club = None):
    if club is not None:
        clubName = club.getUserName()
    else:
        clubName = ''
    return _sysMsg('clubs/request/success/application/sent', clubName=clubName)


def getAppRevokeSysMsg(club = None):
    if club is not None:
        clubName = club.getUserName()
    else:
        clubName = ''
    return _sysMsg('clubs/request/success/application/revoke', clubName=clubName)


def getAppAcceptSysMsg(userName):
    return _sysMsg('clubs/request/success/application/accept', userName=userName)


def getAppDeclineSysMsg(userName):
    return _sysMsg('clubs/request/success/application/decline', userName=userName)


def getAssignPrivateSysMsg(userName):
    return _sysMsg('clubs/request/success/users/assignPrivate', userName=userName)


def getAssignOfficerSysMsg(userName):
    return _sysMsg('clubs/request/success/users/assignOfficer', userName=userName)


def getTransferOwnershipSysMsg(userName):
    return _sysMsg('clubs/request/success/users/transferOwnership', userName=userName)


def getKickMemberSysMsg(userName):
    return _sysMsg('clubs/request/success/users/kick', userName=userName)


def getCreateClubSysMsg():
    return _sysMsg('clubs/request/success/createClub')


def getLeaveClubSysMsg(club = None):
    if club is not None:
        clubName = club.getUserName()
    else:
        clubName = ''
    return _sysMsg('clubs/request/success/leaveClub', clubName=clubName)


def getDestroyClubSysMsg(club = None):
    if club is not None:
        clubName = club.getUserName()
    else:
        clubName = ''
    return _sysMsg('clubs/request/success/destroyClub', clubName=clubName)


def getOpenClubSysMsg(isOpen):
    if isOpen:
        return _sysMsg('clubs/request/success/openClub')
    else:
        return _sysMsg('clubs/request/success/closeClub')


def getInviteRevokeSysMsg():
    return _sysMsg('clubs/request/success/invite/revoke')


class InvitesSysMsgFormatter(object):

    def __init__(self, accountsIDs, response, usersCache = None):
        if len(accountsIDs) > 1:
            errors = map(lambda (c, dbID): dbID, response.data.get('errors', []))
        else:
            errors = []
        self._successNames = []
        self._errorNames = []
        self._accountsIDs = accountsIDs
        if usersCache is None:
            usersGetter = storage_getter('users')()
        else:
            usersGetter = usersCache.get
        for dbID in accountsIDs:
            user = usersGetter(dbID)
            if not user:
                continue
            if dbID not in errors:
                self._successNames.append(user.getFullName(dbID))
            else:
                self._errorNames.append(user.getFullName(dbID))

        return

    def getSuccessSysMsg(self):
        if len(self._accountsIDs) > 1:
            if not len(self._errorNames):
                return _sysMsg('clubs/request/success/invites/sent')
            else:
                return _sysMsg('clubs/request/success/invites/sent/names/success', names=', '.join(self._successNames))
        else:
            return _sysMsg('clubs/request/success/invite/sent')

    def getErrorSysMsg(self):
        if len(self._errorNames) > 1:
            return _sysMsg('clubs/request/success/invites/sent/names/error', names=', '.join(self._errorNames))


def _sysMsg(i18nKey, *args, **kwargs):
    return makeString(('#system_messages:%s' % i18nKey), *args, **kwargs)
