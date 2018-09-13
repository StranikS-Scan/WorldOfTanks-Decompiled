# Embedded file name: scripts/client/notification/actions_handlers.py
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR
from gui import DialogsInterface, makeHtmlString, SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.prb_control.prb_helpers import prbInvitesProperty, prbDispatcherProperty
from gui.shared import g_eventBus, events, actions, EVENT_BUS_SCOPE
from gui.shared.utils.requesters import StatsRequester
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

    def __init__(self, eventType):
        super(_ShowArenaResultHandler, self).__init__()
        self.__eventType = eventType

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
        arenaUniqueID = notification.getSavedID()
        if not arenaUniqueID:
            self._updateNotification(notification)
            LOG_ERROR('arenaUniqueID not found', notification)
            return
        self._showWindow(notification, arenaUniqueID)

    def _updateNotification(self, notification):
        _, formatted, settings = self.proto.serviceChannel.getMessage(notification.getID())
        if formatted and settings:
            formatted['buttonsStates'].update({'submit': NOTIFICATION_BUTTON_STATE.HIDDEN})
            formatted['message'] += makeHtmlString('html_templates:lobby/system_messages', 'infoNoAvailable')
            notification.update(formatted)

    def _showWindow(self, notification, arenaUniqueID):
        g_eventBus.handleEvent(events.ShowWindowEvent(self.__eventType, {'arenaUniqueID': arenaUniqueID}))

    def _showI18nMessage(self, key, msgType):

        def showMessage():
            SystemMessages.pushI18nMessage(key, type=msgType)

        BigWorld.callback(0.0, showMessage)


class ShowBattleResultsHandler(_ShowArenaResultHandler):

    def __init__(self):
        super(ShowBattleResultsHandler, self).__init__(events.ShowWindowEvent.SHOW_BATTLE_RESULTS)

    def _updateNotification(self, notification):
        super(ShowBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    @process
    def _showWindow(self, notification, arenaUniqueID):
        Waiting.show('loadStats')
        results = yield StatsRequester().getBattleResults(long(arenaUniqueID))
        Waiting.hide('loadStats')
        if results:
            super(ShowBattleResultsHandler, self)._showWindow(notification, arenaUniqueID)
        else:
            self._updateNotification(notification)


class ShowTutorialBattleHistoryHandler(_ShowArenaResultHandler):
    _lastHistoryID = GlobalStorage(GLOBAL_VAR.LAST_HISTORY_ID, 0)

    def __init__(self):
        super(ShowTutorialBattleHistoryHandler, self).__init__(events.ShowWindowEvent.SHOW_TUTORIAL_BATTLE_HISTORY)

    def _updateNotification(self, notification):
        super(ShowTutorialBattleHistoryHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_tutorial:labels/results-are-not-available', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, arenaUniqueID):
        if arenaUniqueID == self._lastHistoryID:
            super(ShowTutorialBattleHistoryHandler, self)._showWindow(notification, arenaUniqueID)
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
        g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_BROWSER_WINDOW, {'url': link,
         'title': title,
         'showActionBtn': False}), EVENT_BUS_SCOPE.LOBBY)


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


class NotificationsActionsHandlers(object):

    def __init__(self):
        super(NotificationsActionsHandlers, self).__init__()
        nType = NOTIFICATION_TYPE
        self.__handlers = {(nType.MESSAGE, 'showBattleResults'): ShowBattleResultsHandler,
         (nType.MESSAGE, 'showTutorialBattleHistory'): ShowTutorialBattleHistoryHandler,
         (nType.MESSAGE, 'openPollInBrowser'): OpenPollHandler,
         (nType.INVITE, 'acceptInvite'): AcceptPrbInviteHandler,
         (nType.INVITE, 'declineInvite'): DeclinePrbInviteHandler}

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
