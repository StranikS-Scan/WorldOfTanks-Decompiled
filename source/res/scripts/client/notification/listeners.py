# Embedded file name: scripts/client/notification/listeners.py
import weakref
import BigWorld
from constants import EVENT_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING, LOG_ERROR
from gui.server_events import events_dispatcher as quests_events
from gui.Scaleform.daapi.view.dialogs import I18PunishmentDialogMeta
from gui.prb_control.prb_helpers import GlobalListener, prbInvitesProperty
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger.formatters import SYS_MSG_EXTRA_HANDLER_TYPE
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from notification.decorators import MessageDecorator, PrbInviteDecorator
from notification.settings import NOTIFICATION_TYPE

class _NotificationListener(object):

    def __init__(self):
        super(_NotificationListener, self).__init__()
        self._model = lambda : None

    def start(self, model):
        self._model = weakref.ref(model)
        return True

    def stop(self):
        self._model = lambda : None

    def request(self):
        pass


class ServiceChannelListener(_NotificationListener):
    _handlers = {SYS_MSG_EXTRA_HANDLER_TYPE.PUNISHMENT: ('handlePunishWindow', True),
     SYS_MSG_EXTRA_HANDLER_TYPE.REF_QUEST_AWARD: ('handleRefQuestsWindow', True),
     SYS_MSG_EXTRA_HANDLER_TYPE.REF_SYS_STATUS: ('handleRefSysStatusWindow', True),
     SYS_MSG_EXTRA_HANDLER_TYPE.FORT_RESULTS: ('handleFortResultsWindow', True),
     SYS_MSG_EXTRA_HANDLER_TYPE.POTAPOV_QUEST_AWARD: ('handlePotapovQuestsWindow', True),
     SYS_MSG_EXTRA_HANDLER_TYPE.POTAPOV_QUEST_AUTO_REWARD: ('handlePotapovQuestsAutoWindow', True)}

    def __init__(self):
        super(ServiceChannelListener, self).__init__()
        self.__isLobbyLoaded = False
        self.__delayedHandlers = []

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def start(self, model):
        result = super(ServiceChannelListener, self).start(model)
        if result:
            channel = g_messengerEvents.serviceChannel
            channel.onServerMessageReceived += self.__onMessageReceived
            channel.onClientMessageReceived += self.__onMessageReceived
            g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)
            serviceChannel = self.proto.serviceChannel
            messages = serviceChannel.getReadMessages()
            addNotification = model.collection.addItem
            for clientID, (_, formatted, settings) in messages:
                addNotification(MessageDecorator(clientID, formatted, settings))

            serviceChannel.handleUnreadMessages()
        return result

    def stop(self):
        super(ServiceChannelListener, self).stop()
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)
        channel = g_messengerEvents.serviceChannel
        channel.onServerMessageReceived -= self.__onMessageReceived
        channel.onClientMessageReceived -= self.__onMessageReceived
        self.__delayedHandlers = []

    def handlePunishWindow(self, data):
        from gui.DialogsInterface import showDialog
        showDialog(I18PunishmentDialogMeta('punishmentWindow', None, data), lambda *args: None)
        return

    def handleRefQuestsWindow(self, data):
        from gui.game_control import g_instance as g_gameCtrl
        completedQuestIDs = data['completedQuestIDs']
        for tankman in data['tankmen']:
            g_gameCtrl.refSystem.showTankmanAwardWindow(tankman, completedQuestIDs)

        for vehicle in data['vehicles']:
            g_gameCtrl.refSystem.showVehicleAwardWindow(vehicle, completedQuestIDs)

        if 'credits' in data:
            g_gameCtrl.refSystem.showCreditsAwardWindow(data['credits'], completedQuestIDs)

    def handleRefSysStatusWindow(self, data):
        windowID, ctx = data['window'], data['ctx']
        if windowID == 1:
            self.__showRefSystemNotification('showReferrerIntroWindow', invitesCount=ctx.get('invites_count', 0))
        elif windowID == 2:
            self.__showRefSystemNotification('showReferralIntroWindow', nickname=ctx['nickname'], isNewbie=True)
        elif windowID == 3:
            self.__showRefSystemNotification('showReferralIntroWindow', nickname=ctx['nickname'], isNewbie=False)
        else:
            LOG_WARNING('Unknown referral system user status window', data)

    def handlePotapovQuestsWindow(self, data):
        from gui.server_events import g_eventsCache
        allQuests = g_eventsCache.getAllQuests(includePotapovQuests=True)
        if 'tokens' in data and len(data['tokens']):
            quests_events.showTokensAward(data['tokens'])
        if 'achievements' in data and len(data['achievements']):
            quests_events.showAchievementsAward(data['achievements'])
        needToShowVehAwardWindow = False
        for qID in data.get('completedQuestIDs', set()):
            if qID in allQuests:
                for tokenID, children in allQuests[qID].getChildren().iteritems():
                    for chID in children:
                        chQuest = allQuests[chID]
                        if chQuest.getType() == EVENT_TYPE.POTAPOV_QUEST:
                            needToShowVehAwardWindow = True
                            break

        if needToShowVehAwardWindow:
            for vehicle in data.get('vehicles', []):
                quests_events.showVehicleAward(vehicle)

    def handlePotapovQuestsAutoWindow(self, data):
        from gui.server_events import g_eventsCache
        for potapovQuestID, (isMain, isAdd) in data.iteritems():
            quests_events.showRegularAward(g_eventsCache.potapov.getQuests()[potapovQuestID], isMain, isAdd)

    def handleFortResultsWindow(self, data):
        from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
        if data:
            g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx={'data': data}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __handleLobbyLoaded(self, _):
        self.__isLobbyLoaded = True
        for handlerName, data in self.__delayedHandlers:
            getattr(self, handlerName)(data)

    def __handleExtraData(self, handlerType, data):
        if handlerType in self._handlers:
            handlerName, isLobbyRequired = self._handlers[handlerType]
            if isLobbyRequired and not self.__isLobbyLoaded:
                self.__delayedHandlers.append((handlerName, data))
            else:
                getattr(self, handlerName)(data)
        else:
            LOG_WARNING('Unknown handler for system message', handlerType, data)

    def __onMessageReceived(self, clientID, formatted, settings):
        model = self._model()
        if model:
            model.addNotification(MessageDecorator(clientID, formatted, settings))
            for eHandler in settings.extraHandlerData:
                self.__handleExtraData(eHandler.type, eHandler.data)

    @classmethod
    def __showRefSystemNotification(cls, methodName, **ctx):
        try:
            from gui import game_control
            getattr(game_control.g_instance.refSystem, methodName)(**ctx)
        except:
            LOG_ERROR('There is exception while processing notification center window', methodName, ctx)
            LOG_CURRENT_EXCEPTION()


class PrbInvitesListener(_NotificationListener, GlobalListener):

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def start(self, model):
        result = super(PrbInvitesListener, self).start(model)
        self.startGlobalListening()
        prbInvites = self.prbInvites
        if result and prbInvites:
            prbInvites.onReceivedInviteListInited += self.__onInviteListInited
            prbInvites.onReceivedInviteListModified += self.__onInviteListModified
            if prbInvites.isInited():
                self.__addInvites()
        return result

    def stop(self):
        super(PrbInvitesListener, self).stop()
        self.stopGlobalListening()
        prbInvites = self.prbInvites
        if prbInvites:
            prbInvites.onReceivedInviteListInited -= self.__onInviteListInited
            prbInvites.onReceivedInviteListModified -= self.__onInviteListModified

    def onPrbFunctionalInited(self):
        self.__updateInvites()

    def onPrbFunctionalFinished(self):
        self.__updateInvites()

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self.__updateInvites()

    def onIntroUnitFunctionalInited(self):
        self.__updateInvites()

    def onIntroUnitFunctionalFinished(self):
        self.__updateInvites()

    def onUnitFunctionalInited(self):
        self.__updateInvites()

    def onUnitFunctionalFinished(self):
        self.__updateInvites()

    def onUnitStateChanged(self, state, timeLeft):
        self.__updateInvites()

    def onPreQueueFunctionalInited(self):
        self.__updateInvites()

    def onPreQueueFunctionalFinished(self):
        self.__updateInvites()

    def onEnqueued(self):
        self.__updateInvites()

    def onDequeued(self):
        self.__updateInvites()

    def __onInviteListInited(self):
        if self.prbInvites.getUnreadCount() > 0:
            self.__notifyClient()
        self.__addInvites()

    def __onInviteListModified(self, added, changed, deleted):
        self.__notifyClient()
        model = self._model()
        if model is None:
            return
        else:
            for inviteID in added:
                invite = self.prbInvites.getReceivedInvite(inviteID)
                if invite:
                    model.addNotification(PrbInviteDecorator(invite))

            for inviteID in deleted:
                model.removeNotification(NOTIFICATION_TYPE.INVITE, inviteID)

            for inviteID in changed:
                invite = self.prbInvites.getReceivedInvite(inviteID)
                if invite:
                    model.updateNotification(NOTIFICATION_TYPE.INVITE, inviteID, invite, True)

            return

    def __notifyClient(self):
        try:
            BigWorld.WGWindowsNotifier.onInvitation()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

    def __addInvites(self):
        model = self._model()
        if model is None:
            return
        else:
            model.removeNotificationsByType(NOTIFICATION_TYPE.INVITE)
            invites = self.prbInvites.getReceivedInvites()
            invites = sorted(invites, cmp=lambda invite, other: cmp(invite.createTime, other.createTime))
            for invite in invites:
                model.addNotification(PrbInviteDecorator(invite))

            return

    def __updateInvites(self):
        model = self._model()
        if model:
            invites = self.prbInvites.getReceivedInvites()
            for invite in invites:
                model.updateNotification(NOTIFICATION_TYPE.INVITE, invite.id, invite, False)


class NotificationsListeners(_NotificationListener):

    def __init__(self):
        super(NotificationsListeners, self).__init__()
        self.__serviceListener = ServiceChannelListener()
        self.__invitesListener = PrbInvitesListener()

    def start(self, model):
        self.__serviceListener.start(model)
        self.__invitesListener.start(model)

    def stop(self):
        self.__serviceListener.stop()
        self.__invitesListener.stop()
