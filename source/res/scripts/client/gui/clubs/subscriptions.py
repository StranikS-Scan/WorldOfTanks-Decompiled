# Embedded file name: scripts/client/gui/clubs/subscriptions.py
import weakref
from debug_utils import LOG_WARNING
from AccountCommands import RES_FAILURE
from helpers.time_utils import getCurrentTimestamp
from club_shared import SUBSCRIPTION_EXPIRY_TIME as _SET
from shared_utils import forEach
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.ListenersCollection import ListenersCollection
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable
from gui.clubs import contexts as club_ctx
from gui.clubs.club_helpers import getClientClubsMgr
from gui.clubs.items import Club
from gui.clubs.interfaces import IClubListener
from gui.clubs.settings import SUBSCRIPTION_STATE
from gui.clubs.comparators import SimpleTypeComparator

class ClubsListeners(ListenersCollection):

    def __init__(self):
        super(ClubsListeners, self).__init__()
        self._setListenerClass(IClubListener)

    def isEmpty(self):
        return not len(self._listeners)

    def notify(self, eventType, *args):
        self._invokeListeners(eventType, *args)

    def clear(self):
        while len(self._listeners):
            self._listeners.pop()

    def addListener(self, listener):
        if not self.hasListener(listener):
            super(ClubsListeners, self).addListener(listener)


@ReprInjector.simple(('getClubDbID', 'clubDbID'), ('getSubscriptionType', 'sType'), ('getClub', 'club'), ('getState', 'state'), ('isExpired', 'expired'))

class _Subscription(Notifiable, ClubsListeners):

    def __init__(self, clubDbID, subscriptionType, clubsCtrl = None):
        super(_Subscription, self).__init__()
        self.__clubDbID = clubDbID
        self.__subscriptionType = subscriptionType
        self.__club = None
        self.__state = SUBSCRIPTION_STATE.NOT_SUBSCRIBED
        self.__lastRequestTime = -1
        if clubsCtrl is not None:
            self.__clubsCtrl = weakref.proxy(clubsCtrl)
        else:
            self.__clubsCtrl = None
        self.addNotificator(PeriodicNotifier(lambda : _SET - 10.0, self.__onSubscriptionUpdate, (_SET,)))
        self.__comparators = [SimpleTypeComparator('name', 'onClubNameChanged', 'getUserName'),
         SimpleTypeComparator('description', 'onClubDescriptionChanged', 'getUserDescription'),
         SimpleTypeComparator('owner', 'onClubOwnerChanged', 'getOwnerDbID'),
         SimpleTypeComparator('state', 'onClubStateChanged', 'getState'),
         SimpleTypeComparator('ladder', 'onClubLadderInfoChanged', 'getLadderInfo'),
         SimpleTypeComparator('members', 'onClubMembersChanged', 'getMembers'),
         SimpleTypeComparator('membersExtras', 'onClubMembersChanged', 'getMembers'),
         SimpleTypeComparator('invites', 'onClubInvitesChanged', 'getInvites'),
         SimpleTypeComparator('applicants', 'onClubApplicantsChanged', 'getApplicants'),
         SimpleTypeComparator('restrictions', 'onClubRestrictionsChanged', 'getRestrictions'),
         SimpleTypeComparator('minWinRate', 'onClubApplicantsRequirementsChanged', 'getApplicantsRequirements'),
         SimpleTypeComparator('minBattleCount', 'onClubApplicantsRequirementsChanged', 'getApplicantsRequirements'),
         SimpleTypeComparator('shortDescription', 'onClubApplicantsRequirementsChanged', 'getApplicantsRequirements')]
        return

    def start(self):
        if self.isNotSubscribed():
            self.__doSubscribe()
            self.startNotification()

    def stop(self):
        self.clear()
        self.stopNotification()
        if self.isSubscribed():
            self.__doUnsubscribe()

    def fini(self):
        self.stop()
        self.__lastRequestTime = -1
        self.__club = None
        self.__clubsCtrl = None
        self.__comparators = []
        self.clear()
        return

    def isSubscribed(self):
        return self.__checkState(SUBSCRIPTION_STATE.SUBSCRIBED)

    def isNotSubscribed(self):
        return self.__checkState(SUBSCRIPTION_STATE.NOT_SUBSCRIBED)

    def isExpired(self):
        return self.__lastRequestTime + _SET <= getCurrentTimestamp()

    def getState(self):
        return self.__state

    def getClubDbID(self):
        return self.__clubDbID

    def getSubscriptionType(self):
        return self.__subscriptionType

    def getClub(self):
        return self.__club

    def _request(self, ctx, callback = None):
        if self.__clubsCtrl is not None:
            self.__clubsCtrl.sendRequest(ctx, allowDelay=True)(callback)
        else:
            LOG_WARNING('Trying to send club request while clubs control is not specified', self, ctx)
            callback(RES_FAILURE, '', None)
        return

    def _changeState(self, newState):
        if newState != self.__state:
            prevState, self.__state = self.__state, newState
            self.notify('onClubSubscriptionStateChanged', newState, prevState)

    def _onClubUpdated(self, clubDbID, clubCompactDescr):
        if clubDbID == self.__clubDbID:
            if not clubCompactDescr:
                self.notify('onClubUpdated', None)
                if self.__clubsCtrl is not None:
                    self.__clubsCtrl._removeSubscription(clubDbID)
                return
            oldClub, newClub = self.__club, Club(clubDbID, clubCompactDescr)
            self.__club = newClub
            if oldClub is None:
                self.notify('onClubUpdated', newClub)
            elif oldClub.isChanged(newClub):
                forEach(lambda c: c(self, oldClub, newClub), self.__comparators)
        return

    def __checkState(self, *states):
        return self.__state in states

    def __onSubscriptionUpdate(self):
        if not self.isEmpty():
            self.__doSubscribe()
        else:
            self.__doUnsubscribe()

    def __doSubscribe(self):

        def _onSubscribed(result):
            if result.isSuccess():
                self._changeState(SUBSCRIPTION_STATE.SUBSCRIBED)
                self._onClubUpdated(self.__clubDbID, result.data)

        self._request(club_ctx.SubscribeCtx(self.__clubDbID, self.__subscriptionType, self._onClubUpdated), callback=_onSubscribed)
        if self.isNotSubscribed():
            self._changeState(SUBSCRIPTION_STATE.SUBSCRIBING)
        self.__lastRequestTime = getCurrentTimestamp()

    def __doUnsubscribe(self):

        def _onUnsubscribed(result):
            if result.isSuccess():
                self._changeState(SUBSCRIPTION_STATE.NOT_SUBSCRIBED)

        if getClientClubsMgr():
            self._request(club_ctx.UnsubscribeCtx(self.__clubDbID), _onUnsubscribed)
            self._changeState(SUBSCRIPTION_STATE.NOT_SUBSCRIBED)
