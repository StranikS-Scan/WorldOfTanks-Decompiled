# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/badges_controller.py
import typing
import Event
import constants
from adisp import adisp_process
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items.processors.common import BadgesSelector
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.scheduled_notifications import Notifiable, AcyclicNotifier
from helpers import dependency
from skeletons.gui.game_control import IBadgesController
from skeletons.gui.shared import IItemsCache
from tutorial.control.context import GLOBAL_FLAG
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items.badge import Badge

class BadgesController(IBadgesController, Notifiable):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BadgesController, self).__init__()
        self.onUpdated = Event.Event()
        self.__currentSelectedPrefix = None
        self.__currentSelectedSuffix = None
        self.__pendingBadges = None
        self.__tutorStorage = getTutorialGlobalStorage()
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
        badges = self.itemsCache.items.getBadges()
        self.__initCurrentBadges(badges)
        self.__badgesProcessing(badges)
        g_clientUpdateManager.addCallbacks({'badges': self.__updateBadges,
         'stats.dossier': self.__updateBadges})

    def select(self, badges):
        self.__selectOnClient(badges)

    def getPrefix(self):
        return self.__currentSelectedPrefix

    def getSuffix(self):
        return self.__currentSelectedSuffix

    def __clear(self):
        self.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__currentSelectedPrefix = None
        self.__currentSelectedSuffix = None
        self.__pendingBadges = None
        return

    def __updateBadges(self, *_):
        if self.__pendingBadges is not None:
            return
        else:
            badges = self.itemsCache.items.getBadges()
            self.__initCurrentBadges(badges)
            self.__badgesProcessing(badges)
            self.onUpdated()
            return

    def __initCurrentBadges(self, badges):
        self.__currentSelectedPrefix = None
        self.__currentSelectedSuffix = None
        for badge in badges.itervalues():
            if badge.isSelected:
                if badge.isPrefixLayout() and badge.isAchieved:
                    self.__currentSelectedPrefix = badge
                elif badge.isSuffixLayout() and badge.isAchieved:
                    self.__currentSelectedSuffix = badge

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
            self.__currentSelectedSuffix = None
            self.__currentSelectedPrefix = None
            for badgeID in badges:
                badge = self.itemsCache.items.getBadgeByID(badgeID)
                if badge is not None:
                    badge.isSelected = True
                    if badge.isPrefixLayout():
                        self.__currentSelectedPrefix = badge
                    elif badge.isSuffixLayout():
                        self.__currentSelectedSuffix = badge

            self.onUpdated()
            self.__pendingBadges = badges
            self.startNotification()
            return

    @adisp_process
    def __selectOnServer(self):
        result = yield BadgesSelector(self.__pendingBadges).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        else:
            self.__initCurrentBadges(self.itemsCache.items.getBadges())
        self.__pendingBadges = None
        self.onUpdated()
        return

    def __badgesProcessing(self, badges):
        currentSelectedPrefix = self.__currentSelectedPrefix
        for badge in badges.itervalues():
            if self.__tutorStorage is not None and badge.isNew() and badge.isAchieved:
                if badge.isPrefixLayout():
                    self.__tutorStorage.setValue(GLOBAL_FLAG.HAVE_NEW_BADGE, True)
                elif badge.isSuffixLayout():
                    self.__tutorStorage.setValue(GLOBAL_FLAG.HAVE_NEW_SUFFIX_BADGE, True)
            if currentSelectedPrefix is not None and currentSelectedPrefix.isCollapsible() and badge.isCollapsible() and badge.group == currentSelectedPrefix.group and badge.getBadgeClass() > currentSelectedPrefix.getBadgeClass() and badge.isAchieved:
                currentSelectedPrefix = badge

        if currentSelectedPrefix != self.__currentSelectedPrefix and self.itemsCache.isSynced():
            self.__currentSelectedPrefix.isSelected = False
            self.__currentSelectedPrefix = currentSelectedPrefix
            self.select([ b.badgeID for b in (self.__currentSelectedPrefix, self.__currentSelectedSuffix) if b is not None ])
        return
