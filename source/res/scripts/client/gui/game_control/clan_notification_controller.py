# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/clan_notification_controller.py
import logging
from constants import ClansConfig
from Event import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CLAN_NOTIFICATION_COUNTERS, CLAN_NEWS_SEEN
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getClanQuestURL
from gui.Scaleform.daapi.view.lobby.clans.browser.web_handlers import createNotificationWebHandlers
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IClanNotificationController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_window_controller import GameWindowController
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class ClanNotificationController(GameWindowController, IClanNotificationController, MethodsRules):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __appLoader = dependency.descriptor(IAppLoader)
    __clansCtrl = dependency.descriptor(IWebController)
    CLAN_NEWS_ALIAS = 'clanNews'

    def __init__(self):
        super(ClanNotificationController, self).__init__()
        self.__enabled = False
        self.onClanNotificationUpdated = Event()

    @property
    def newsCounter(self):
        return sum(self.getCounters().values())

    def getCounters(self, aliases=None):
        counters = AccountSettings.getCounters(CLAN_NOTIFICATION_COUNTERS)
        return counters if not aliases else {elem:counters.get(elem, 0) for elem in aliases}

    @MethodsRules.delayable('onLobbyInited')
    def setCounters(self, alias, count, isIncrement=False):
        if not self.__enabled:
            return
        counters = self.getCounters()
        if isIncrement:
            count = counters.get(alias, 0) + count
        counters[alias] = count if count >= 0 else 0
        AccountSettings.setCounters(CLAN_NOTIFICATION_COUNTERS, counters)
        self.onClanNotificationUpdated()

    def resetCounters(self):
        AccountSettings.setCounters(CLAN_NOTIFICATION_COUNTERS, {})
        self.onClanNotificationUpdated()

    @MethodsRules.delayable()
    def onLobbyInited(self, event):
        self.__enabled = self.__lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.NOTIFICATION_ENABLED, False)
        self.__addListeners()
        self.__processClanNewsNotification()

    def onAvatarBecomePlayer(self):
        self.__removeListeners()

    def showWindow(self, url=None, invokedFrom=None):
        self._showWindow(url, invokedFrom)

    def hideWindow(self):
        browserView = self.__getBrowserView()
        if browserView:
            browserView.onCloseView()

    def _getUrl(self):
        return getClanQuestURL()

    def _openWindow(self, url, _=None):
        browserView = self.__getBrowserView()
        if browserView:
            return
        ctx = {'url': url,
         'webHandlers': createNotificationWebHandlers(),
         'browser_alias': VIEW_ALIAS.CLAN_NOTIFICATION_WINDOW,
         'showCloseBtn': True,
         'useSpecialKeys': True,
         'showWaiting': True,
         'showActionBtn': False,
         'allowRightClick': True}
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CLAN_NOTIFICATION_WINDOW), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def __getBrowserView(self):
        app = self.__appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserView = app.containerManager.getView(WindowLayer.SUB_VIEW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.CLAN_NOTIFICATION_WINDOW})
            return browserView
        else:
            return

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onServerSettingsChange(self, diff):
        clansDiff = diff.get(ClansConfig.SECTION_NAME, {})
        if ClansConfig.NOTIFICATION_ENABLED in clansDiff:
            self.__enabled = clansDiff[ClansConfig.NOTIFICATION_ENABLED]
            if not self.__enabled:
                self.resetCounters()

    def __processClanNewsNotification(self):
        account = self.__clansCtrl.getAccountProfile()
        notificationStartTime = self.__lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.NOTIFICATION_START_TIME, 0)
        if not account.isInClan() or account.getJoinedAt() > notificationStartTime:
            return
        if not AccountSettings.getNotifications(CLAN_NEWS_SEEN):
            AccountSettings.setNotifications(CLAN_NEWS_SEEN, True)
            self.setCounters(self.CLAN_NEWS_ALIAS, 1, isIncrement=True)
