# Embedded file name: scripts/client/gui/clubs/ClubsController.py
import weakref
from functools import partial
from collections import namedtuple
import BigWorld
from adisp import async, process
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE
from account_helpers import getPlayerDatabaseID
from PlayerEvents import g_playerEvents
from messenger import g_settings
from messenger.storage import storage_getter
from club_shared import ACCOUNT_NOTIFICATION_TYPE, WEB_CMD_RESULT
from gui import SystemMessages, DialogsInterface
from gui.game_control import g_instance as g_gameCtrl
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils import safeCancelCallback
from gui.clubs import subscriptions, contexts as club_ctx, states, formatters as club_fmts
from gui.clubs.items import Club, ClubInvite, ClubApplication, clearInvitesIDs, _UnitInfo
from gui.clubs.settings import BROKEN_WEB_CHECK_PERIOD, CLIENT_CLUB_STATE
from gui.clubs.club_helpers import getClientClubsMgr, isClubsEnabled
from gui.clubs.requests import ClubRequestsController

def _showError(result):
    i18nMsg = club_fmts.getRequestErrorMsg(result.errStr)
    if i18nMsg:
        SystemMessages.pushMessage(i18nMsg, type=SystemMessages.SM_TYPE.Error)


class _SYNC_TYPE(object):
    CLUBS = 1
    INVITES = 2
    APPS = 4
    RESTRICTIONS = 8
    ALL = CLUBS | INVITES | APPS | RESTRICTIONS


class _AccountClubProfile(object):
    _ClubInfo = namedtuple('_ClubInfo', ['id', 'joined_at', 'role'])

    def __init__(self, clubsCtrl):
        super(_AccountClubProfile, self).__init__()
        self.__state = states.UnavailableClubsState()
        self.__resyncCbID = None
        self._clear()
        self._clubsCtrl = weakref.proxy(clubsCtrl)
        return

    def stop(self):
        self.__cancelResyncCallback()
        self._clear()

    def getState(self):
        return self.__state

    def resync(self, firstInit = False, forceResync = False):
        if not isClubsEnabled():
            LOG_DEBUG('Clubs is not enabled on this server. Skip profile resync.')
            return
        clubsMgr = getClientClubsMgr()
        if not forceResync and clubsMgr and not clubsMgr.isRelatedToClubs():
            LOG_DEBUG('Account does not related to clubs. Skip profile resync.')
            if firstInit and self.__state.getStateID() != CLIENT_CLUB_STATE.NO_CLUB:
                self._changeState(states.NoClubState([], []))
            return
        if g_gameCtrl.roaming.isInRoaming():
            LOG_NOTE('There is no clubs in the roaming')
            return
        if self._waitForSync & _SYNC_TYPE.ALL:
            LOG_DEBUG('Club profile resync already in progress')
            return
        self._waitForSync |= _SYNC_TYPE.ALL
        self.__sendRequest(club_ctx.GetPrivateProfileCtx(), callback=partial(self.__onAccountProfileReceived, _SYNC_TYPE.ALL))

    def syncClubs(self):
        if self._waitForSync & _SYNC_TYPE.CLUBS:
            return

        def _cbWrapper(result):
            self.__onAccountProfileReceived(_SYNC_TYPE.CLUBS, result._replace(data={'clubs': result.data}))

        self._waitForSync |= _SYNC_TYPE.CLUBS
        self.__sendRequest(club_ctx.GetMyClubsCtx(), callback=_cbWrapper)

    def isSynced(self):
        return self._isSynced

    def hasClub(self):
        return bool(self._clubs)

    def wasSentApplication(self):
        return bool(self.getApplications(onlyActive=True))

    def getClubInfo(self, idx = 0):
        if idx < len(self._clubs):
            return self._clubs[idx]
        else:
            return None

    def getApplications(self, onlyActive = False):
        if onlyActive:
            return filter(lambda app: app.isActive(), self._apps.itervalues())
        else:
            return self._apps

    def getApplication(self, appID = None):
        apps = self.getApplications(onlyActive=True)
        if appID is None:
            return apps[0]
        else:
            return apps.get(appID)

    def getInvites(self):
        return self._invites

    def getInvite(self, inviteID):
        return self._invites.get(inviteID)

    def getRestrictions(self):
        return self._restrictions

    @storage_getter('users')
    def users(self):
        return None

    def requestMyClub(self, callback):
        if self.hasClub():
            clubDbID = self.getClubInfo().id
            if self._clubsCtrl.isSubscribed(clubDbID):
                callback(self._clubsCtrl.getClub(clubDbID))
            else:
                self.__sendRequest(club_ctx.GetClubCtx(clubDbID), callback=partial(self.__onMyClubSyncCompleted, callback, clubDbID))
        else:
            callback(None)
        return

    def _clear(self):
        self._changeState(states.UnavailableClubsState())
        self._clubs = []
        self._invites = {}
        self._apps = {}
        self._restrictions = []
        self._waitForSync = 0
        self._isSynced = False

    def _changeState(self, newState):
        oldState, self.__state = self.__state, newState
        if oldState.getStateID() != newState.getStateID():
            self.__loadResyncCallback()
            self.__notify('_onClubsStateChanged', newState)

    def _updateClubs(self, clubs):
        self._clubs = []
        for c in clubs:
            self._clubs.append(self._ClubInfo(*c))

    def _updateApps(self, apps):
        self._apps = {}
        for clubDbID, sendingTime, comment, status in apps:
            app = ClubApplication(clubDbID, getPlayerDatabaseID(), comment, sendingTime, status)
            self._apps[app.getID()] = app

        if not self._isSynced:
            self.__notify('onAccountClubAppsInited', self._apps.values())
        else:
            self.__notify('onAccountClubAppsChanged', self._apps.values())

    def _updateInvites(self, invites):
        prevInvites = self._invites
        self._invites = {}
        for sendingTime, inviterDbID, clubDbID, status in invites:
            invite = ClubInvite(clubDbID, getPlayerDatabaseID(), inviterDbID, sendingTime, status)
            if not self._isSenderIgnored(invite):
                self._invites[invite.getID()] = invite

        if not self._isSynced:
            self.__notify('onAccountClubInvitesInited', self._invites.values())
        else:
            added = []
            removed = []
            changed = []
            if prevInvites:
                for uniqueID, invite in self._invites.iteritems():
                    if uniqueID not in prevInvites:
                        added.append(invite)
                    elif invite.getStatus() != prevInvites[uniqueID].getStatus():
                        changed.append(invite)

                for uniqueID, invite in prevInvites.iteritems():
                    if uniqueID not in self._invites:
                        removed.append(invite)

            else:
                added = self._invites.values()
            self.__notify('onAccountClubInvitesChanged', added, removed, changed)

    def _updateRestrictions(self, restrs):
        oldRestrs, self._restrictions = self._restrictions, restrs
        return oldRestrs != restrs

    def _isSenderIgnored(self, invite):
        user = self.users.getUser(invite.getUserDbID())
        areFriendsOnly = g_settings.userPrefs.invitesFromFriendsOnly
        if user:
            if areFriendsOnly:
                if user.isFriend():
                    return False
                else:
                    LOG_DEBUG('Invite is ignored, shows invites from friends only', invite)
                    return True
            if user.isIgnored():
                LOG_DEBUG('Invite is ignored, there is the contact in ignore list', invite, user)
                return True
        elif areFriendsOnly:
            LOG_DEBUG('Invite is ignored, shows invites from friends only', invite)
        return areFriendsOnly

    def __getAccountResyncDelta(self):
        if self.__state.getStateID() == CLIENT_CLUB_STATE.UNKNOWN:
            return BROKEN_WEB_CHECK_PERIOD
        else:
            r = self.__state.getLimits().getNearestRestriction()
            if r:
                return r.getExpiryTimeLeft()
            return None

    def __loadResyncCallback(self):
        self.__cancelResyncCallback()
        deltaTime = self.__getAccountResyncDelta()
        if deltaTime:
            LOG_DEBUG('Load club resync callback', deltaTime)
            self.__resyncCbID = BigWorld.callback(deltaTime + 10.0, self.__onAccountProfileResync)

    def __cancelResyncCallback(self):
        if self.__resyncCbID is not None:
            safeCancelCallback(self.__resyncCbID)
            self.__resyncCbID = None
        return

    def __sendRequest(self, ctx, callback):
        if self._clubsCtrl is not None:
            self._clubsCtrl.getRequestCtrl().request(ctx, callback=callback)
        else:
            LOG_ERROR('Invalid clubs controller instance', ctx, callback)
        return

    def __notify(self, eventType, *args, **kwargs):
        if self._clubsCtrl is not None:
            self._clubsCtrl.notify(eventType, *args, **kwargs)
        else:
            LOG_ERROR('Invalid clubs controller instance', eventType, args, kwargs)
        return

    def __onAccountProfileReceived(self, flags, result):
        LOG_DEBUG('Clubs account profile has been received', flags, result)
        self._waitForSync ^= flags
        if result.isSuccess():
            profile = result.data
            if profile:
                if flags & _SYNC_TYPE.CLUBS:
                    self._updateClubs(profile.get('clubs', []))
                if flags & _SYNC_TYPE.APPS:
                    self._updateApps(profile.get('applications', tuple()))
                if flags & _SYNC_TYPE.INVITES:
                    self._updateInvites(profile.get('invites', []))
                if flags & _SYNC_TYPE.RESTRICTIONS:
                    isRestrsChanged = self._updateRestrictions(profile.get('restrictions', []))
                else:
                    isRestrsChanged = False
                self._isSynced = True
                self.__state.update(self, self)
                if isRestrsChanged:
                    self.__notify('onAccountClubRestrictionsChanged')
        else:
            self._clear()
        self.__loadResyncCallback()

    def __onMyClubSyncCompleted(self, callback, clubDbID, result):
        if result.isSuccess():
            callback(Club(clubDbID, result.data))
        else:
            callback(None)
        return

    def __onAccountProfileResync(self):
        self.__cancelResyncCallback()
        self.resync(forceResync=True)

    def __repr__(self):
        return 'AccountClubProfile(state = %s, synced = %s, waitForSync = %d)' % (self.__state, self._isSynced, self._waitForSync)


class ClubsController(subscriptions.ClubsListeners):

    def __init__(self):
        super(ClubsController, self).__init__()
        self.__subscriptions = {}
        self.__isAppsNotifyShown = False
        self._requestsCtrl = ClubRequestsController(self)
        self._accountProfile = _AccountClubProfile(self)

    def init(self):
        pass

    def fini(self):
        self.stop()
        self._requestsCtrl.fini()
        self.__subscriptions.clear()

    def start(self):
        clubsMgr = getClientClubsMgr()
        if clubsMgr is not None:
            clubsMgr.onClientClubsChanged += self.__onClientClubsChanged
            clubsMgr.onClientClubsNotification += self.__onClientClubsNotification
            clubsMgr.onClientClubsUnitInfoChanged += self.__onClientClubsUnitInfoChanged
        g_playerEvents.onCenterIsLongDisconnected += self.__onCenterIsLongDisconnected
        g_clientUpdateManager.addCallbacks({'cache.relatedToClubs': self.__onSpaAttrChanged,
         'cache.cybersportSeasonInProgress': self.__onSeasonStateChanged})
        self._accountProfile.resync(firstInit=True)
        return

    def stop(self, isDisconnected = False):
        if isDisconnected:
            self.__isAppsNotifyShown = False
        clearInvitesIDs()
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onCenterIsLongDisconnected -= self.__onCenterIsLongDisconnected
        clubsMgr = getClientClubsMgr()
        if clubsMgr is not None:
            clubsMgr.onClientClubsNotification -= self.__onClientClubsNotification
            clubsMgr.onClientClubsChanged -= self.__onClientClubsChanged
            clubsMgr.onClientClubsUnitInfoChanged -= self.__onClientClubsUnitInfoChanged
        self._accountProfile.stop()
        self._requestsCtrl.stopProcessing()
        for s in self.__subscriptions.itervalues():
            s.stop()

        self.__subscriptions.clear()
        return

    def markAppsNotificationShown(self):
        self.__isAppsNotifyShown = True

    def isAppsNotificationShown(self):
        return self.__isAppsNotifyShown

    def addListener(self, listener, forceResync = False):
        if not self._accountProfile.isSynced():
            self._accountProfile.resync(forceResync=forceResync)
        super(ClubsController, self).addListener(listener)

    def addClubListener(self, clubDbID, listener, subscriptionType, forceResync = False):
        if not self._accountProfile.isSynced():
            self._accountProfile.resync(forceResync=forceResync)
        s = self.__subscriptions.setdefault(clubDbID, subscriptions._Subscription(clubDbID, subscriptionType, self))
        s.addListener(listener)
        s.start()

    def removeClubListener(self, clubDbID, listener):
        if clubDbID in self.__subscriptions:
            s = self.__subscriptions[clubDbID]
            s.removeListener(listener)

    def getClub(self, clubDbID):
        if clubDbID in self.__subscriptions:
            return self.__subscriptions[clubDbID].getClub()
        else:
            return None

    def getProfile(self):
        return self._accountProfile

    def isSubscribed(self, clubDbID):
        return clubDbID in self.__subscriptions and self.__subscriptions[clubDbID].isSubscribed()

    @async
    @process
    def sendRequest(self, ctx, callback, allowDelay = None):
        yield lambda callback: callback(None)
        if ctx.getConfirmID():
            success = yield DialogsInterface.showI18nConfirmDialog(ctx.getConfirmID())
            if not success:
                return

        def _cbWrapper(result):
            isNeedToChangeState = False
            if not result.isSuccess():
                isNeedToChangeState = result.code in WEB_CMD_RESULT.WEB_UNAVAILABLE_ERRORS
                _showError(result)
            callback(result)
            if isNeedToChangeState:
                self._accountProfile._changeState(states.UnavailableClubsState())

        self._requestsCtrl.request(ctx, callback=_cbWrapper, allowDelay=allowDelay)

    def getRequestCtrl(self):
        return self._requestsCtrl

    def getState(self):
        return self._accountProfile.getState()

    def getLimits(self):
        return self._accountProfile.getState().getLimits()

    def _removeSubscription(self, clubDbID):
        if clubDbID in self.__subscriptions:
            self.__subscriptions[clubDbID].stop()

    def __onClientClubsChanged(self):
        self._accountProfile.resync()

    def __onClientClubsNotification(self, notificationType, notice):
        if notificationType == ACCOUNT_NOTIFICATION_TYPE.CLUB_CREATED:
            self.notify('onClubCreated', notice.clubDBID)
        self._accountProfile.resync()

    def __onCenterIsLongDisconnected(self, _):
        self._accountProfile.resync()

    def __onSpaAttrChanged(self, isRelatedToClubs):
        self.notify('onAccountClubRelationChanged', isRelatedToClubs)
        self._accountProfile.resync()

    def __onSeasonStateChanged(self, isSeasonInProgress):
        self.notify('onClubsSeasonStateChanged', isSeasonInProgress)
        self._accountProfile.resync()

    def __onClientClubsUnitInfoChanged(self, clubDbID, unit):
        if clubDbID in self.__subscriptions:
            unitInfo = _UnitInfo(*unit) if unit else None
            self.__subscriptions[clubDbID].notify('onClubUnitInfoChanged', unitInfo)
        return

    def __repr__(self):
        return 'ClubsCtrl(profile = %s, subscriptions = %s)' % (str(self._accountProfile), self.__subscriptions.keys())


g_clubsCtrl = ClubsController()
