# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/CalendarController.py
import logging
from datetime import timedelta
from account_helpers.AccountSettings import AccountSettings, LAST_CALENDAR_SHOW_TIMESTAMP
from adisp import process
from gui import GUI_SETTINGS
from gui.game_control.links import URLMarcos
from gui.server_events.modifiers import CalendarSplashModifier
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleRequestCommand
from helpers import dependency
from helpers import time_utils
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import ICalendarController, IBrowserController
from skeletons.gui.server_events import IEventsCache
from web_client_api.commands import createRequestHandler
import constants
_BROWSER_SIZE = (1014, 654)
_MIN_BROWSER_ID = 827709
_START_OF_DAY_OFFSET = {'EU': timedelta(hours=5),
 'ASIA': timedelta(hours=6),
 'NA': timedelta(hours=11),
 'RU': timedelta(hours=6)}
_logger = logging.getLogger(__name__)
_browserIDGen = xrange(_MIN_BROWSER_ID, _MIN_BROWSER_ID + 10000).__iter__()

class CalendarInvokeOrigin(CONST_CONTAINER):
    ACTION = 'action'
    HANGAR = 'hangar'
    SPLASH = 'first'


class CalendarController(ICalendarController):
    """Advent calendar controller.
    
    This controller shows the in-game browser pointing to the advent calendar web-app in following scenarios:
      * The player clicks on related item in the Hangar.
      * The player clicks on related Action in the Shop.
      * On lobby startup once in a day, if allowed by server.
    """
    browserCtrl = dependency.descriptor(IBrowserController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(CalendarController, self).__init__()
        self.__browserID = None
        self.__showOnSplash = False
        self.__urlMacros = URLMarcos()
        return

    def init(self):
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.browserCtrl.onBrowserDeleted += self.__onBrowserDeleted

    def fini(self):
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.hideCalendar()
        self.browserCtrl.onBrowserDeleted -= self.__onBrowserDeleted
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        super(CalendarController, self).fini()
        return

    def onLobbyStarted(self, event):
        if self.__showOnSplash:
            lastShowTstamp = self.__getShowTimestamp()
            now = time_utils.getServerUTCTime()
            if lastShowTstamp is not None:
                today = time_utils.getDayTimeBoundsForUTC(now)[0]
                offset = _START_OF_DAY_OFFSET.get(constants.CURRENT_REALM, timedelta(0)).total_seconds()
                dayStart = today + offset
                mustShow = lastShowTstamp < dayStart <= now or lastShowTstamp > now
            else:
                mustShow = True
            if mustShow:
                self.showCalendar(CalendarInvokeOrigin.SPLASH)
                self.__setShowTimestamp(now)
        return

    def onAvatarBecomePlayer(self):
        self.hideCalendar()

    def onDisconnected(self):
        self.hideCalendar()

    def showCalendar(self, invokedFrom):
        """Show the advent calendar in browser window."""
        self.hideCalendar()
        try:
            while self.__browserID is None:
                browserID = next(_browserIDGen)
                if self.browserCtrl.getBrowser(browserID) is None:
                    self.__browserID = browserID

        except StopIteration:
            _logger.error('Could not allocate a browser ID for calendar')
            return

        self.__openBrowser(self.__browserID, _BROWSER_SIZE, invokedFrom)
        _logger.debug('Calendar opened in web browser (browserID=%d)' % self.__browserID)
        return

    def hideCalendar(self):
        if self.__browserID is None:
            return
        else:
            self.browserCtrl.delBrowser(self.__browserID)
            return

    def __onSyncCompleted(self, *_):

        def calendarEnabledActionFilter(act):
            return any((isinstance(mod, CalendarSplashModifier) for mod in act.getModifiers()))

        self.__showOnSplash = len(self.eventsCache.getActions(calendarEnabledActionFilter)) > 0

    def __onBrowserDeleted(self, browserID):
        if browserID == self.__browserID:
            _logger.debug('Calendar web browser destroyed (browserID=%d)' % browserID)
            self.__browserID = None
        return

    def __getShowTimestamp(self):
        tstampStr = AccountSettings.getSettings(LAST_CALENDAR_SHOW_TIMESTAMP)
        if tstampStr:
            try:
                return float(tstampStr)
            except (TypeError, ValueError):
                _logger.warning('Invalid calendar show timestamp')

        return None

    def __setShowTimestamp(self, tstamp):
        AccountSettings.setSettings(LAST_CALENDAR_SHOW_TIMESTAMP, str(tstamp))

    @process
    def __openBrowser(self, browserID, browserSize, invokedFrom):
        """Shows the event calendar browser window, pointing to remote calendar
        single-page web application.
        """
        url = yield self.__urlMacros.parse(GUI_SETTINGS.adventCalendarBaseURL, params={'called': invokedFrom})
        if not url:
            _logger.error('Invalid calendar URL')
            return
        browserHandlers = [createRequestHandler(handleRequestCommand)]

        def showBrowserWindow():
            ctx = {'size': browserSize,
             'handlers': browserHandlers,
             'browserID': browserID,
             'alias': VIEW_ALIAS.ADVENT_CALENDAR,
             'showCloseBtn': False,
             'showWaiting': True,
             'showActionBtn': False}
            browser = self.browserCtrl.getBrowser(browserID)
            browser.useSpecialKeys = False
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.ADVENT_CALENDAR, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

        yield self.browserCtrl.load(url=url, browserID=browserID, browserSize=browserSize, isAsync=False, useBrowserWindow=False, showBrowserCallback=showBrowserWindow, showCreateWaiting=False)
