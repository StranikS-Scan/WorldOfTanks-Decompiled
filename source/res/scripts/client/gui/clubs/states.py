# Embedded file name: scripts/client/gui/clubs/states.py
from gui.shared.utils.decorators import ReprInjector
from gui.clubs.settings import CLIENT_CLUB_STATE
from gui.clubs.restrictions import AccountClubLimits, DefaultAccountClubLimits

@ReprInjector.simple(('getStateID', 'state'))

class _AccountClubsState(object):

    def __init__(self, stateID):
        self.__stateID = stateID

    def getStateID(self):
        return self.__stateID

    def getLimits(self):
        return DefaultAccountClubLimits()

    def update(self, clubsCtrl, privateData):
        pass

    def isAvailable(self):
        return True


@ReprInjector.withParent()

class UnavailableClubsState(_AccountClubsState):

    def __init__(self):
        super(UnavailableClubsState, self).__init__(CLIENT_CLUB_STATE.UNKNOWN)

    def update(self, clubsCtrl, profile):
        if profile.hasClub():
            clubsCtrl._changeState(HasClubState(profile.getClubInfo(), profile.getInvites(), profile.getRestrictions()))
        elif profile.wasSentApplication():
            clubsCtrl._changeState(SentAppState(profile.getApplication(), profile.getInvites(), profile.getRestrictions()))
        elif profile.isSynced():
            clubsCtrl._changeState(NoClubState(profile.getInvites(), profile.getRestrictions()))

    def isAvailable(self):
        return False


@ReprInjector.withParent(('getInvites', 'invites'))

class _AvailableClubState(_AccountClubsState):

    def __init__(self, stateID, invites, restrs):
        super(_AvailableClubState, self).__init__(stateID)
        self._invites = invites
        self._restrs = restrs

    def getInvites(self):
        return self._invites

    def getLimits(self):
        return AccountClubLimits(self._restrs)

    def update(self, clubsCtrl, profile):
        self._invites = profile.getInvites()
        self._restrs = profile.getRestrictions()


@ReprInjector.withParent(('getClubDbID', 'clubDbID'), ('getJoiningTime', 'join'))

class HasClubState(_AvailableClubState):

    def __init__(self, clubInfo, invites, restrs):
        super(HasClubState, self).__init__(CLIENT_CLUB_STATE.HAS_CLUB, invites, restrs)
        self.__clubInfo = clubInfo

    def getClubDbID(self):
        return self.__clubInfo.id

    def getJoiningTime(self):
        return self.__clubInfo.joined_at

    def update(self, clubsCtrl, profile):
        if not profile.isSynced():
            clubsCtrl._changeState(UnavailableClubsState())
        elif not profile.hasClub():
            if profile.wasSentApplication():
                clubsCtrl._changeState(SentAppState(profile.getApplication(), profile.getInvites(), profile.getRestrictions()))
            else:
                clubsCtrl._changeState(NoClubState(profile.getInvites(), profile.getRestrictions()))
        else:
            super(HasClubState, self).update(clubsCtrl, profile)


@ReprInjector.withParent()

class NoClubState(_AvailableClubState):

    def __init__(self, invites, restrs):
        super(NoClubState, self).__init__(CLIENT_CLUB_STATE.NO_CLUB, invites, restrs)

    def update(self, clubsCtrl, profile):
        if not profile.isSynced():
            clubsCtrl._changeState(UnavailableClubsState())
        elif profile.wasSentApplication():
            clubsCtrl._changeState(SentAppState(profile.getApplication(), profile.getInvites(), profile.getRestrictions()))
        elif profile.hasClub():
            clubsCtrl._changeState(HasClubState(profile.getClubInfo(), profile.getInvites(), profile.getRestrictions()))
        else:
            super(NoClubState, self).update(clubsCtrl, profile)


@ReprInjector.withParent(('getClubDbID', 'club'), ('getSendingTime', 'sent'), ('getComment', 'comment'))

class SentAppState(_AvailableClubState):

    def __init__(self, app, invites, restrs):
        super(SentAppState, self).__init__(CLIENT_CLUB_STATE.SENT_APP, invites, restrs)
        self._app = app
        self._invites = invites

    def getClubDbID(self):
        return self._app.getClubDbID()

    def getSendingTime(self):
        return self._app.getTimestamp()

    def getComment(self):
        return self._app.getComment()

    def update(self, clubsCtrl, profile):
        if not profile.isSynced():
            clubsCtrl._changeState(UnavailableClubsState())
        elif profile.hasClub():
            clubsCtrl._changeState(HasClubState(profile.getClubInfo(), profile.getInvites(), profile.getRestrictions()))
        elif not profile.wasSentApplication():
            clubsCtrl._changeState(NoClubState(profile.getInvites(), profile.getRestrictions()))
        else:
            super(SentAppState, self).update(clubsCtrl, profile)
