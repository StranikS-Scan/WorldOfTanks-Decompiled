# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/year_hare_affair_controller.py
import logging
import random
import typing
import adisp
import year_hare_affair_common
from Event import Event
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.wgcg.yha.contexts import YhaVideoCtx
from helpers import dependency, time_utils, isPlayerAccount
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_control import IYearHareAffairController
from skeletons.gui.game_window_controller import GameWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from helpers.server_settings import ServerSettings, YearHareAffairConfig
_logger = logging.getLogger(__name__)
_UPDATE_PERIOD = time_utils.HALF_HOUR
_REQUEST_DELAY_INTERVAL = (10, 70)

class YearHareAffairController(GameWindowController, IYearHareAffairController, CallbackDelayer):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        GameWindowController.__init__(self)
        CallbackDelayer.__init__(self)
        self.onStateChanged = Event()
        self.__isVideoAvailable = False
        self.__nextUpdateTime = None
        return

    def fini(self):
        self.__clear()
        self.onStateChanged.clear()
        CallbackDelayer.destroy(self)
        super(YearHareAffairController, self).fini()

    def onDisconnected(self):
        self.__clear()
        super(YearHareAffairController, self).onDisconnected()

    @property
    def isVideoAvailable(self):
        return self.__isVideoAvailable

    def onAvatarBecomePlayer(self):
        self.clearCallbacks()

    def onLobbyInited(self, event):
        super(YearHareAffairController, self).onLobbyInited(event)
        if self.isEnabled():
            self.__updateVideoStatus()

    def isEnabled(self):
        return self.__config.isEnabled

    def getFinishTime(self):
        if not self.isEnabled():
            return None
        else:
            action = self.eventsCache.getYearHareAffairAction()
            return None if action is None else action.getFinishTimeRaw()

    def showWindow(self, url=None, invokedFrom=None):
        if not self.isEnabled():
            _logger.warning('Failed to open YearHareAffair view. Event is disabled.')
            return
        self._showWindow(url, invokedFrom)

    def hideWindow(self):
        pass

    def _getUrl(self):
        return self.__config.url

    def _addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _openWindow(self, url, _=None):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.YEAR_HARE_AFFAIR_VIEW), ctx={'url': url}), EVENT_BUS_SCOPE.LOBBY)

    @property
    def __config(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        return serverSettings.yearHareAffair

    def __onServerSettingsChange(self, diff):
        if year_hare_affair_common.SERVER_SETTINGS_KEY not in diff:
            return
        if self.isEnabled():
            if isPlayerAccount():
                delay = random.randint(*_REQUEST_DELAY_INTERVAL)
                self.__scheduleUpdate(delay)
        else:
            self.__clear()
        _logger.debug('YHA state has been changed.')
        self.onStateChanged()

    def __onVideoBecomeAvailable(self):
        self.__isVideoAvailable = True
        self.onStateChanged()

    def __clear(self):
        self.clearCallbacks()
        self.__isVideoAvailable = False
        self.__nextUpdateTime = None
        return

    @adisp.process
    def __updateVideoStatus(self):
        if not self.isEnabled() or not isPlayerAccount() or self.isVideoAvailable:
            return
        else:
            delay = self.__getDelayFromScheduledUpdate()
            if delay:
                self.__scheduleUpdate(delay)
                return
            videoCtx = yield self.__requestVideoCtx()
            if videoCtx is None:
                self.__scheduleUpdate(time_utils.ONE_MINUTE)
            elif videoCtx.getVideo():
                self.__onVideoBecomeAvailable()
            else:
                delay = self.__getDelayFromAvailabilityTime(videoCtx.getAvailableAt())
                self.__scheduleUpdate(delay)
            return

    @adisp.async
    @adisp.process
    def __requestVideoCtx(self, callback=None):
        if not self.__webCtrl.isAvailable():
            _logger.warning('Could not update YHA video status. WebController is not available.')
            callback(None)
            return
        else:
            response = yield self.__webCtrl.sendRequest(ctx=YhaVideoCtx())
            if response.isSuccess():
                result = YhaVideoCtx.getDataObj(response.data)
            else:
                result = YhaVideoCtx.getDefDataObj()
            callback(result)
            return

    def __scheduleUpdate(self, delay):
        _logger.debug('YHA video status update delayed: %s.', delay)
        self.__nextUpdateTime = time_utils.getServerUTCTime() + delay
        self.delayCallback(delay, self.__updateVideoStatus)

    def __getDelayFromScheduledUpdate(self):
        return None if self.__nextUpdateTime is None else max(0, self.__nextUpdateTime - time_utils.getServerUTCTime())

    @staticmethod
    def __getDelayFromAvailabilityTime(availabilityTime):
        if availabilityTime:
            delay = max(0, availabilityTime - time_utils.getServerUTCTime())
            delay += random.randint(*_REQUEST_DELAY_INTERVAL)
        else:
            delay = _UPDATE_PERIOD
        return delay
