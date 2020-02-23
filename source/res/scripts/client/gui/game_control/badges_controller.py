# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/badges_controller.py
import Event
import constants
from adisp import process
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items.processors.common import BadgesSelector
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.scheduled_notifications import Notifiable, AcyclicNotifier
from helpers import dependency
from skeletons.gui.game_control import IBadgesController
from skeletons.gui.shared import IItemsCache

class BadgesController(IBadgesController, Notifiable):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BadgesController, self).__init__()
        self.onUpdated = Event.Event()
        self.__currentSelectedPrefix = None
        self.__currentAchievedSuffix = None
        self.__pendingBadges = None
        return

    def init(self):
        super(BadgesController, self).init()
        self.addNotificator(AcyclicNotifier(self.__getTimer, self.__timerUpdate))

    def fini(self):
        self.onUpdated.clear()
        self.clearNotification()
        super(BadgesController, self).fini()

    def onDisconnected(self):
        self.__clear()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onLobbyStarted(self, ctx):
        self.__initCurrentBadges()
        g_clientUpdateManager.addCallbacks({'badges': self.__updateBadges})
        self.itemsCache.onSyncCompleted += self.__onSyncCompleted

    def select(self, badges):
        self.__selectOnClient(badges)

    def getPrefix(self):
        return self.__currentSelectedPrefix

    def getSuffix(self):
        return self.__currentAchievedSuffix

    def __clear(self):
        self.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__currentSelectedPrefix = None
        self.__currentAchievedSuffix = None
        self.__pendingBadges = None
        return

    def __updateBadges(self, *_):
        if self.__pendingBadges is not None:
            return
        else:
            self.__initCurrentBadges()
            self.onUpdated()
            return

    def __onSyncCompleted(self, updateReason, _):
        if updateReason in (CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            self.__updateBadges()

    def __initCurrentBadges(self):
        self.__currentSelectedPrefix = None
        self.__currentAchievedSuffix = None
        for badge in self.itemsCache.items.getBadges().itervalues():
            if badge.isPrefixLayout() and badge.isSelected and badge.isAchieved:
                self.__currentSelectedPrefix = badge
            if badge.isSuffixLayout() and badge.isAchieved:
                self.__currentAchievedSuffix = badge

        return

    @staticmethod
    def __getTimer():
        return constants.REQUEST_COOLDOWN.BADGES

    def __timerUpdate(self):
        self.__selectOnServer()

    def __selectOnClient(self, badges):
        if self.__pendingBadges == badges:
            return
        else:
            self.__currentSelectedPrefix = None
            if self.__currentAchievedSuffix is not None:
                self.__currentAchievedSuffix.isSelected = False
            for badgeID in badges:
                badge = self.itemsCache.items.getBadgeByID(badgeID)
                if badge is not None:
                    if badge.isPrefixLayout():
                        badge.isSelected = True
                        self.__currentSelectedPrefix = badge
                    elif badge.isSuffixLayout() and self.__currentAchievedSuffix is not None:
                        self.__currentAchievedSuffix.isSelected = True

            self.onUpdated()
            self.__pendingBadges = badges
            self.startNotification()
            return

    @process
    def __selectOnServer(self):
        result = yield BadgesSelector(self.__pendingBadges).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        else:
            self.__initCurrentBadges()
        self.__pendingBadges = None
        self.onUpdated()
        return
