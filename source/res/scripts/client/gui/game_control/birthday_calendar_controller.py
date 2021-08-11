# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/birthday_calendar_controller.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from adisp import process
from chat_shared import SYS_MESSAGE_TYPE
from constants import Configs
from frameworks.wulf import WindowStatus, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency, time_utils, server_settings
from messenger.proto.events import g_messengerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.game_control import IBrowserController, IBirthdayCalendarController, IBootcampController
from skeletons.gui.game_window_controller import GameWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from web.web_client_api import webApiCollection, w2c, W2CSchema, w2capi
from web.web_client_api.birthday_calendar import BirthdayCalendarWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.sound import SoundWebApi
from web.web_client_api.ui import CloseViewWebApi, CloseWindowWebApi, OpenTabWebApi, OpenWindowWebApi, UtilWebApi
_logger = logging.getLogger(__name__)
_BROWSER_SIZE = (1014, 654)
_BIRTHDAY_TOKEN = 'birthday_calendar_stage'
_BIRTHDAY_EVENT_POSTFIX = '_birthday_calendar'

@w2capi(name='close_window', key='window_id')
class _CloseWindowWebApi(CloseWindowWebApi):
    __birthdayCalendarController = dependency.descriptor(IBirthdayCalendarController)

    @w2c(W2CSchema, 'birthday_calendar')
    def birthdayCalendar(self, *_):
        self.__birthdayCalendarController.hideWindow()


def _createIntroWebApiCollection():
    return webApiCollection(CloseViewWebApi, BirthdayCalendarWebApi, OpenTabWebApi, ShopWebApi)


def _createCalendarWebApiCollection():
    return webApiCollection(_CloseWindowWebApi, BirthdayCalendarWebApi, OpenTabWebApi, OpenWindowWebApi, ShopWebApi, SoundWebApi, UtilWebApi)


class BirthdayCalendarController(GameWindowController, IBirthdayCalendarController):
    lobbyContext = dependency.descriptor(ILobbyContext)
    appLoader = dependency.descriptor(IAppLoader)
    browserCtrl = dependency.descriptor(IBrowserController)
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    bootcampController = dependency.descriptor(IBootcampController)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(BirthdayCalendarController, self).__init__()
        self.browserCtrl.onBrowserDeleted += self.__onBrowserDeleted
        self.__enabled = False
        self.__isSpaceCreate = False
        self.__browserID = None
        self.__introWindow = None
        self.__eventDates = None
        self.__tokenUpdated = False
        self.__url = ''
        self.__introUrl = ''
        return

    def init(self):
        super(BirthdayCalendarController, self).init()
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreate
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__chatMessageReceive

    def __onSpaceCreate(self, *args, **kwargs):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__isSpaceCreate = True
        self._updateActions()
        if self.__tokenUpdated and self.__enabled and not self.bootcampController.isInBootcamp():
            if self._needShowIntro():
                self._showIntro()
            else:
                self.showWindow()
            self.__tokenUpdated = False

    def onAvatarBecomePlayer(self):
        self.__isSpaceCreate = False
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(BirthdayCalendarController, self).onAvatarBecomePlayer()

    def fini(self):
        if self.__introWindow:
            self.__introWindow.onStatusChanged -= self.__onIntroStatusChanged
            self.__introWindow = None
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__chatMessageReceive
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.browserCtrl.onBrowserDeleted -= self.__onBrowserDeleted
        super(BirthdayCalendarController, self).fini()
        return

    def onDisconnected(self):
        self.__enabled = False
        self.__isSpaceCreate = False
        self.__introWindow = None
        self.__eventDates = None
        self.__tokenUpdated = False
        self.__url = ''
        self.__introUrl = ''
        super(BirthdayCalendarController, self).onDisconnected()
        return

    def showWindow(self, url=None, invokedFrom=None):
        self._showWindow(url, invokedFrom)

    def hideWindow(self):
        if self.__browserID is None:
            return
        else:
            app = self.appLoader.getApp()
            if app is not None and app.containerManager is not None:
                browserWindow = app.containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.UNIQUE_NAME: VIEW_ALIAS.BIRTHDAY_CALENDAR})
                if browserWindow is not None:
                    browserWindow.destroy()
                    self.__browserID = None
                else:
                    self.browserCtrl.delBrowser(self.__browserID)
            return

    @property
    def isInPrimeTime(self):
        start, end = self.__eventDates
        return start <= time_utils.getServerUTCTime() < end

    @property
    def eventDates(self):
        return self.__eventDates

    @property
    def hasTokens(self):
        return self.tokenCount > 0

    @property
    def tokenCount(self):
        return self.itemsCache.items.tokens.getTokenCount(_BIRTHDAY_TOKEN)

    def _updateActions(self):
        bdayCalendarConfig = self.lobbyContext.getServerSettings().birthdayCalendar
        self.__enabled = bdayCalendarConfig.enabled
        self.__url = bdayCalendarConfig.calendarURL
        self.__introUrl = bdayCalendarConfig.calendarIntroUrl
        actions = self.eventsCache.getActions(self.__eventFilter()).values()
        now = time_utils.getServerUTCTime()
        for action in actions:
            if action.getFinishTimeRaw() < now:
                continue
            self.__eventDates = (int(action.getStartTimeRaw()), int(action.getFinishTimeRaw()))

    def _showIntro(self):
        self.__introWindow = SFWindow(SFViewLoadParams(VIEW_ALIAS.BROWSER_OVERLAY_INTRO), EVENT_BUS_SCOPE.LOBBY, ctx={'url': self.__introUrl,
         'allowRightClick': False,
         'webHandlers': _createIntroWebApiCollection(),
         'forcedSkipEscape': True,
         'browserParams': makeBrowserParams(isCloseBtnVisible=True)})
        self.__introWindow.onStatusChanged += self.__onIntroStatusChanged
        self.__introWindow.load()
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        settings[GuiSettingsBehavior.BIRTHDAY_CALENDAR_INTRO_SHOWED] = True
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)

    def _needShowIntro(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        isShowed = settings[GuiSettingsBehavior.BIRTHDAY_CALENDAR_INTRO_SHOWED]
        return not isShowed

    def _openWindow(self, url, invokedFrom=None):
        if self.appLoader.getSpaceID() != GuiGlobalSpaceID.LOBBY:
            return
        elif self.__getBrowserView() is not None:
            return
        else:
            self.__loadBrowser(url, _BROWSER_SIZE)
            _logger.debug('Birthday calendar opened in web browser (browserID=%d)', self.__browserID)
            return

    def _updateBrowser(self):
        browser = self.browserCtrl.getBrowser(self.__browserID)
        browser.navigate(self._getUrl())

    def _getUrl(self):
        return self.__url

    @server_settings.serverSettingsChangeListener(Configs.BIRTHDAY_CALENDAR_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self._updateActions()

    @staticmethod
    def __eventFilter():
        return lambda q: _BIRTHDAY_EVENT_POSTFIX in q.getID()

    def __chatMessageReceive(self, _, message):

        def isValidMessage(msg):
            return msg and msg.type == SYS_MESSAGE_TYPE.tokenQuests.index() and msg.data and 'tokens' in msg.data

        if not isValidMessage(message) or self.__introWindow is not None:
            return
        else:
            if _BIRTHDAY_TOKEN in message.data['tokens']:
                if self.__isSpaceCreate and self.__enabled and not self.bootcampController.isInBootcamp():
                    if self.__browserID:
                        self._updateBrowser()
                    elif self._needShowIntro():
                        self._showIntro()
                    else:
                        self.showWindow()
                else:
                    self.__tokenUpdated = True
            return

    def __onIntroStatusChanged(self, status):
        if status == WindowStatus.DESTROYED:
            _logger.debug('Birthday calendar intro destroyed')
            self.__introWindow.onStatusChanged -= self.__onIntroStatusChanged
            self.__introWindow = None
            self.showWindow()
        return

    def __onBrowserDeleted(self, browserID):
        if browserID == self.__browserID:
            _logger.debug('Birthday calendar web browser destroyed (browserID=%d)', browserID)
            self.__browserID = None
        return

    def __getBrowserView(self):
        app = self.appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserView = app.containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BIRTHDAY_CALENDAR})
            return browserView
        else:
            return

    @process
    def __loadBrowser(self, url, browserSize):
        title = backport.text(R.strings.eleventh_birthday_calendar.window.title())

        def showBrowser():
            ctx = {'size': browserSize,
             'title': title,
             'handlers': _createCalendarWebApiCollection(),
             'browserID': self.__browserID,
             'alias': VIEW_ALIAS.BIRTHDAY_CALENDAR,
             'showCloseBtn': False,
             'showWaiting': True,
             'showActionBtn': False}
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BIRTHDAY_CALENDAR), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

        self.__browserID = yield self.browserCtrl.load(url=url, browserSize=browserSize, isAsync=False, useBrowserWindow=False, showBrowserCallback=showBrowser, showCreateWaiting=True, title=title)
        browser = self.browserCtrl.getBrowser(self.__browserID)
        if browser:
            browser.useSpecialKeys = False
