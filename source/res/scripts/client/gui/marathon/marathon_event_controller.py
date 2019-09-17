# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_event_controller.py
import Event
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.app_loader import sf_lobby
from gui.marathon.festival_marathon import FestivalMarathon
from gui.marathon.racing_event import RacingEvent
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency, isPlayerAccount
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
MARATHON_EVENTS = [FestivalMarathon(), RacingEvent()]
DEFAULT_MARATHON_PREFIX = MARATHON_EVENTS[0].prefix if any(MARATHON_EVENTS) else None

class MarathonEventsController(IMarathonEventsController, Notifiable):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(MarathonEventsController, self).__init__()
        self.__isLobbyInited = False
        self.__isInHangar = False
        self.__eventManager = Event.EventManager()
        self.onFlagUpdateNotify = Event.Event(self.__eventManager)
        self.onVehicleReceived = Event.Event()
        self.__marathons = []
        for marathon in MARATHON_EVENTS:
            self.addMarathon(marathon)

    @sf_lobby
    def app(self):
        pass

    def addMarathon(self, marathonEvent):
        marathonEvent.setFlagUpdateNotify(self.onFlagUpdateNotify)
        self.__marathons.append(marathonEvent)

    def delMarathon(self, prefix):
        self.__marathons.remove(self.__findByPrefix(prefix))

    def getMarathon(self, prefix):
        return self.__findByPrefix(prefix)

    def getMarathons(self):
        return self.__marathons

    def getPrimaryMarathon(self):
        return self.__marathons[0] if self.__marathons else None

    def getFirstShowedMarathon(self):
        for marathon in self.__marathons:
            if marathon.doesShowMissionsTab():
                return marathon

        return None

    def getPrefix(self, eventID):
        for marathon in self.__marathons:
            if eventID.startswith(marathon.prefix):
                return marathon.prefix

        return None

    def getVisibleInPostBattleQuests(self):
        result = {}
        for marathon in self.__marathons:
            if marathon.doesShowInPostBattle():
                result.update(marathon.getMarathonQuests())

        return result

    def getQuestsData(self, prefix=None, postfix=None):
        return self.getPrimaryMarathon().getQuestsData(prefix, postfix) if self.isAnyActive() else {}

    def getTokensData(self, prefix=None, postfix=None):
        return self.getPrimaryMarathon().getTokensData(prefix, postfix) if self.isAnyActive() else {}

    def isAnyActive(self):
        return any((marathon.isAvailable() for marathon in self.__marathons))

    def doesShowAnyMissionsTab(self):
        return any((marathon.doesShowMissionsTab() for marathon in self.__marathons))

    def fini(self):
        self.__stop()
        super(MarathonEventsController, self).fini()

    def onDisconnected(self):
        super(MarathonEventsController, self).onDisconnected()
        self.__stop()

    def onAvatarBecomePlayer(self):
        super(MarathonEventsController, self).onAvatarBecomePlayer()
        self.__stop()

    def onLobbyInited(self, event):
        if not isPlayerAccount():
            return
        self.__isLobbyInited = True

    def onLobbyStarted(self, ctx):
        super(MarathonEventsController, self).onLobbyStarted(ctx)
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._eventsCache.onProgressUpdated += self.__onSyncCompleted
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.__initMarathons()
        self.__onSyncCompleted()

    def tryShowRewardScreen(self):
        if self.__isLobbyInited and self.__isInHangar:
            for marathon in self.__marathons:
                marathon.showRewardScreen()

    def __onViewLoaded(self, pyView, _):
        if self.__isLobbyInited:
            if pyView.alias == VIEW_ALIAS.LOBBY_HANGAR:
                self.__isInHangar = True
                self.tryShowRewardScreen()
            elif pyView.viewType == ViewTypes.LOBBY_SUB:
                self.__isInHangar = False

    def __initMarathons(self):
        for m in self.__marathons:
            m.init()

    def __finiMarathons(self):
        for m in self.__marathons:
            m.fini()

    def __onSyncCompleted(self, *args):
        self.__checkEvents()
        self.tryShowRewardScreen()
        self.__reloadNotification()

    def __checkEvents(self):
        for marathon in self.__marathons:
            marathon.updateQuestsData()
            marathon.setState()

    def __updateFlagState(self):
        self.__checkEvents()
        self.tryShowRewardScreen()
        self.onFlagUpdateNotify()

    def __getClosestStatusUpdateTime(self):
        if self.__marathons:
            return min([ marathon.getClosestStatusUpdateTime() for marathon in self.__marathons ])

    def __reloadNotification(self):
        self.clearNotification()
        timePeriod = self.__getClosestStatusUpdateTime()
        if timePeriod:
            self.addNotificator(PeriodicNotifier(self.__getClosestStatusUpdateTime, self.__updateFlagState))
            self.startNotification()

    def __stop(self):
        self.clearNotification()
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._eventsCache.onProgressUpdated -= self.__onSyncCompleted
        self.__finiMarathons()
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.__isLobbyInited = False

    def __findByPrefix(self, prefix):
        for marathon in self.__marathons:
            if marathon.prefix == prefix:
                return marathon

        return None
