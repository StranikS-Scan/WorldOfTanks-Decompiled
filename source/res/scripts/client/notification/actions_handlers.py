# Embedded file name: scripts/client/notification/actions_handlers.py
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR
from gui import DialogsInterface, makeHtmlString, SystemMessages, game_control
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control import getBattleID
from gui.prb_control.prb_helpers import prbInvitesProperty, prbDispatcherProperty
from gui.shared import g_eventBus, events, actions, EVENT_BUS_SCOPE, event_dispatcher as shared_events
from gui.shared.utils.requesters import DeprecatedStatsRequester
from gui.shared.fortifications import fort_helpers, events_dispatcher as fort_events
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from predefined_hosts import g_preDefinedHosts
try:
    from tutorial import GlobalStorage
    from tutorial.control.context import GLOBAL_VAR
except ImportError:

    class GlobalStorage(object):

        def __init__(self, *args):
            pass

        def __get__(self, instance, owner = None):
            if instance is None:
                return self
            else:
                return 0


    class GLOBAL_VAR(object):
        SHOW_TUTORIAL_BATTLE_HISTORY = ''


class _ActionHandler(object):

    def __init__(self):
        super(_ActionHandler, self).__init__()

    def isRequiredType(self, typeID):
        return False

    def handleAction(self, model, entityID):
        pass


class _ShowArenaResultHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.MESSAGE

    def handleAction(self, model, entityID):
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

    def _updateNotification(self, notification):
        super(ShowFortBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, data):
        if data:
            g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx={'data': data}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self._updateNotification(notification)


class ShowTutorialBattleHistoryHandler(_ShowArenaResultHandler):
    _lastHistoryID = GlobalStorage(GLOBAL_VAR.LAST_HISTORY_ID, 0)

    def _triggerEvent(self, notification, arenaUniqueID):
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

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.MESSAGE

    def handleAction(self, model, entityID):
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

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.INVITE

    @process
    def handleAction(self, model, entityID):
        yield lambda callback: callback(None)
        postActions = []
        invite = self.prbInvites.getReceivedInvite(entityID)
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

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.INVITE

    def handleAction(self, model, entityID):
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

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.INVITE

    def handleAction(self, model, entityID):
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        else:
            battleID, peripheryID = notification.getSavedData()
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

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.FRIENDSHIP_RQ

    def handleAction(self, model, entityID):
        self.proto.contacts.approveFriendship(entityID)


class CancelFriendshipHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def isRequiredType(self, typeID):
        return typeID == NOTIFICATION_TYPE.FRIENDSHIP_RQ

    def handleAction(self, model, entityID):
        self.proto.contacts.cancelFriendship(entityID)


class NotificationsActionsHandlers(object):

    def __init__(self):
        super(NotificationsActionsHandlers, self).__init__()
        _TYPE = NOTIFICATION_TYPE
        self.__handlers = {(_TYPE.MESSAGE, 'showBattleResults'): ShowBattleResultsHandler,
         (_TYPE.MESSAGE, 'showTutorialBattleHistory'): ShowTutorialBattleHistoryHandler,
         (_TYPE.MESSAGE, 'showFortBattleResults'): ShowFortBattleResultsHandler,
         (_TYPE.MESSAGE, 'openPollInBrowser'): OpenPollHandler,
         (_TYPE.MESSAGE, 'acceptFortInvite'): AcceptPrbFortInviteHandler,
         (_TYPE.INVITE, 'acceptInvite'): AcceptPrbInviteHandler,
         (_TYPE.INVITE, 'declineInvite'): DeclinePrbInviteHandler,
         (_TYPE.FRIENDSHIP_RQ, 'approveFriendship'): ApproveFriendshipHandler,
         (_TYPE.FRIENDSHIP_RQ, 'cancelFriendship'): CancelFriendshipHandler}

    def handleAction(self, model, typeID, entityID, actionName):
        key = (typeID, actionName)
        if key in self.__handlers:
            clazz = self.__handlers[key]
            handler = clazz()
            handler.handleAction(model, entityID)
        else:
            LOG_ERROR('Action handler not found', typeID, entityID, actionName)

    def cleanUp(self):
        self.__handlers.clear()
