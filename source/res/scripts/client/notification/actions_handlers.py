# Embedded file name: scripts/client/notification/actions_handlers.py
from collections import defaultdict
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR
from gui import DialogsInterface, makeHtmlString, SystemMessages, game_control
from gui.clubs import contexts as club_ctx, events_dispatcher as club_events
from gui.clubs.club_helpers import ClubListener
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control import getBattleID
from gui.prb_control.prb_helpers import prbInvitesProperty, prbDispatcherProperty
from gui.shared import g_eventBus, events, actions, EVENT_BUS_SCOPE, event_dispatcher as shared_events
from gui.shared.utils.requesters import DeprecatedStatsRequester
from gui.shared.fortifications import fort_helpers, events_dispatcher as fort_events
from gui.wgnc import g_wgncProvider
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from notification.tutorial_helper import TutorialGlobalStorage, TUTORIAL_GLOBAL_VAR
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from predefined_hosts import g_preDefinedHosts

class _ActionHandler(object):

    def __init__(self):
        super(_ActionHandler, self).__init__()

    @classmethod
    def getNotType(cls):
        return NotImplementedError

    @classmethod
    def getActions(self):
        return ()

    def handleAction(self, model, entityID, action):
        raise action in self.getActions() or AssertionError('Handler does not handle action {0}'.format(action))


class _ShowArenaResultHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    def handleAction(self, model, entityID, action):
        super(_ShowArenaResultHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        savedData = notification.getSavedData()
        if not savedData:
            self._updateNotification(notification)
            LOG_ERROR('arenaUniqueID not found', notification)
            return
        self._showWindow(notification, savedData)

    def _updateNotification(self, notification):
        _, formatted, settings = self.proto.serviceChannel.getMessage(notification.getID())
        if formatted and settings:
            formatted['buttonsStates'].update({'submit': NOTIFICATION_BUTTON_STATE.HIDDEN})
            formatted['message'] += makeHtmlString('html_templates:lobby/system_messages', 'infoNoAvailable')
            notification.update(formatted)

    def _showWindow(self, notification, arenaUniqueID):
        pass

    def _showI18nMessage(self, key, msgType):

        def showMessage():
            SystemMessages.pushI18nMessage(key, type=msgType)

        BigWorld.callback(0.0, showMessage)


class ShowBattleResultsHandler(_ShowArenaResultHandler):

    def _updateNotification(self, notification):
        super(ShowBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    @classmethod
    def getActions(self):
        return ('showBattleResults',)

    @process
    def _showWindow(self, notification, arenaUniqueID):
        arenaUniqueID = long(arenaUniqueID)
        Waiting.show('loadStats')
        results = yield DeprecatedStatsRequester().getBattleResults(long(arenaUniqueID))
        Waiting.hide('loadStats')
        if results:
            shared_events.showBattleResultsFromData(results)
        else:
            self._updateNotification(notification)


class ShowFortBattleResultsHandler(_ShowArenaResultHandler):

    @classmethod
    def getActions(self):
        return ('showFortBattleResults',)

    def _updateNotification(self, notification):
        super(ShowFortBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, data):
        if data:
            battleResultData = data.get('battleResult', None)
            g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx={'data': battleResultData}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self._updateNotification(notification)
        return


class ShowTutorialBattleHistoryHandler(_ShowArenaResultHandler):
    _lastHistoryID = TutorialGlobalStorage(TUTORIAL_GLOBAL_VAR.LAST_HISTORY_ID, 0)

    @classmethod
    def getActions(self):
        return ('showTutorialBattleHistory',)

    def _triggerEvent(self, _, arenaUniqueID):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.SHOW_TUTORIAL_BATTLE_HISTORY, {'data': arenaUniqueID}))

    def _updateNotification(self, notification):
        super(ShowTutorialBattleHistoryHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_tutorial:labels/results-are-not-available', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, arenaUniqueID):
        if arenaUniqueID == self._lastHistoryID:
            self._triggerEvent(notification, arenaUniqueID)
        else:
            self._updateNotification(notification)


class OpenPollHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(self):
        return ('openPollInBrowser',)

    def handleAction(self, model, entityID, action):
        super(OpenPollHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification is not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        link, title = notification.getSettings().auxData
        if not link:
            LOG_ERROR('Poll link is not found', notification)
            return
        self.__doOpen(link, title)

    @process
    def __doOpen(self, link, title):
        yield game_control.g_instance.browser.load(link, title, showActionBtn=False)


class AcceptPrbInviteHandler(_ActionHandler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.INVITE

    @classmethod
    def getActions(self):
        return ('acceptInvite',)

    @process
    def handleAction(self, model, entityID, action):
        super(AcceptPrbInviteHandler, self).handleAction(model, entityID, action)
        yield lambda callback: callback(None)
        postActions = []
        invite = self.prbInvites.getInvite(entityID)
        state = self.prbDispatcher.getFunctionalState()
        if state.doLeaveToAcceptInvite(invite.type):
            postActions.append(actions.LeavePrbModalEntity())
        if invite and invite.anotherPeriphery:
            success = True
            if g_preDefinedHosts.isRoamingPeriphery(invite.peripheryID):
                success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
            if not success:
                return
            postActions.append(actions.DisconnectFromPeriphery())
            postActions.append(actions.ConnectToPeriphery(invite.peripheryID))
            postActions.append(actions.PrbInvitesInit())
        self.prbInvites.acceptInvite(entityID, postActions=postActions)


class DeclinePrbInviteHandler(_ActionHandler):

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.INVITE

    @classmethod
    def getActions(self):
        return ('declineInvite',)

    def handleAction(self, model, entityID, action):
        super(DeclinePrbInviteHandler, self).handleAction(model, entityID, action)
        if entityID:
            self.prbInvites.declineInvite(entityID)
        else:
            LOG_ERROR('Invite is invalid', entityID)


class AcceptPrbFortInviteHandler(_ActionHandler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(self):
        return ('acceptFortInvite',)

    def handleAction(self, model, entityID, action):
        super(AcceptPrbFortInviteHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        else:
            customData = notification.getSavedData()
            battleID = customData.get('battleID')
            peripheryID = customData.get('peripheryID')
            if battleID is not None and peripheryID is not None:
                if battleID == getBattleID():
                    fort_events.showFortBattleRoomWindow()
                else:
                    fort_helpers.tryToConnectFortBattle(battleID, peripheryID)
            else:
                LOG_ERROR('Invalid fort battle data', battleID, peripheryID)
            return


class ApproveFriendshipHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    @classmethod
    def getActions(self):
        return ('approveFriendship',)

    def handleAction(self, model, entityID, action):
        super(ApproveFriendshipHandler, self).handleAction(model, entityID, action)
        self.proto.contacts.approveFriendship(entityID)


class CancelFriendshipHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    @classmethod
    def getActions(self):
        return ('cancelFriendship',)

    def handleAction(self, model, entityID, action):
        super(CancelFriendshipHandler, self).handleAction(model, entityID, action)
        self.proto.contacts.cancelFriendship(entityID)


class WGNCActionsHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.WGNC_POP_UP

    def handleAction(self, model, entityID, action):
        notification = model.collection.getItem(NOTIFICATION_TYPE.WGNC_POP_UP, entityID)
        if notification:
            actorName = notification.getSavedData()
        else:
            actorName = ''
        g_wgncProvider.doAction(entityID, action, actorName)


class SecurityLinkHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(self):
        return ('securityLink',)

    def handleAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SECURITY_SETTINGS))


class AcceptClubInviteHandler(_ActionHandler, ClubListener):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLUB_INVITE

    @classmethod
    def getActions(self):
        return ('acceptClubInvite',)

    @process
    def handleAction(self, model, entityID, action):
        super(AcceptClubInviteHandler, self).handleAction(model, entityID, action)
        yield lambda callback: callback(None)
        invite = self.clubsCtrl.getProfile().getInvite(entityID)
        if invite:
            success = yield DialogsInterface.showI18nConfirmDialog('clubInvite')
            if success:
                yield self.clubsCtrl.sendRequest(club_ctx.AcceptInviteCtx(invite.getClubDbID(), entityID, waitingID='clubs/invite/accept'), allowDelay=True)


class DeclineClubInviteHandler(_ActionHandler, ClubListener):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLUB_INVITE

    @classmethod
    def getActions(self):
        return ('declineClubInvite',)

    @process
    def handleAction(self, model, entityID, action):
        super(DeclineClubInviteHandler, self).handleAction(model, entityID, action)
        invite = self.clubsCtrl.getProfile().getInvite(entityID)
        if invite:
            yield self.clubsCtrl.sendRequest(club_ctx.DeclineInviteCtx(invite.getClubDbID(), entityID, waitingID='clubs/invite/decline'), allowDelay=True)
        else:
            yield lambda callback: callback(None)


class ShowClubInviteHandler(_ActionHandler, ClubListener):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLUB_INVITE

    @classmethod
    def getActions(self):
        return ('showClubProfile',)

    def handleAction(self, model, entityID, action):
        super(ShowClubInviteHandler, self).handleAction(model, entityID, action)
        invite = self.clubsCtrl.getProfile().getInvite(entityID)
        if invite:
            return club_events.showClubProfile(invite.getClubDbID())


class ShowClubAppsHandler(_ActionHandler, ClubListener):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLUB_APPS

    @classmethod
    def getActions(self):
        return ('showClubStaffProfile',)

    def handleAction(self, model, entityID, action):
        super(ShowClubAppsHandler, self).handleAction(model, entityID, action)
        return club_events.showClubProfile(entityID, viewIdx=1)


_AVAILABLE_HANDLERS = (ShowBattleResultsHandler,
 ShowTutorialBattleHistoryHandler,
 ShowFortBattleResultsHandler,
 OpenPollHandler,
 AcceptPrbFortInviteHandler,
 AcceptPrbInviteHandler,
 DeclinePrbInviteHandler,
 ApproveFriendshipHandler,
 CancelFriendshipHandler,
 WGNCActionsHandler,
 SecurityLinkHandler,
 AcceptClubInviteHandler,
 DeclineClubInviteHandler,
 ShowClubInviteHandler,
 ShowClubAppsHandler)

class NotificationsActionsHandlers(object):
    __slots__ = ('__single', '__multi')

    def __init__(self, handlers = None):
        super(NotificationsActionsHandlers, self).__init__()
        self.__single = {}
        self.__multi = defaultdict(set)
        if not handlers:
            handlers = _AVAILABLE_HANDLERS
        for clazz in handlers:
            actions = clazz.getActions()
            if actions:
                if len(actions) == 1:
                    self.__single[clazz.getNotType(), actions[0]] = clazz
                else:
                    LOG_ERROR('Handler is not added to collection', clazz)
            else:
                self.__multi[clazz.getNotType()].add(clazz)

    def handleAction(self, model, typeID, entityID, actionName):
        key = (typeID, actionName)
        if key in self.__single:
            clazz = self.__single[key]
            clazz().handleAction(model, entityID, actionName)
        elif typeID in self.__multi:
            for clazz in self.__multi[typeID]:
                clazz().handleAction(model, entityID, actionName)

        else:
            LOG_ERROR('Action handler not found', typeID, entityID, actionName)

    def cleanUp(self):
        self.__single.clear()
        self.__multi.clear()
