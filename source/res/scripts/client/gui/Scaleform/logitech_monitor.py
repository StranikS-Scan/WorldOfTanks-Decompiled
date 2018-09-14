# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/logitech_monitor.py
import importlib
import weakref
from collections import namedtuple
import CommandMapping
import LcdKeyboard
from account_helpers.settings_core.options import KeyboardSettings
from debug_utils import LOG_DEBUG, LOG_WARNING
from game import convertKeyEvent
from gui import g_keyEventHandlers
from gui.Scaleform.Flash import Flash
from gui.Scaleform.framework import ViewTypes
from gui.app_loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import AppLifeCycleEvent
_LOGITECH_SWF_MONO = 'keyboardMono.swf'
_LOGITECH_SWF_COLORED = 'keyboard.swf'

class _LogitechScreen(object):
    LOGO = 'logo'
    HANGAR = 'hangar'
    BATTLE_LOADING = 'battleloading'
    BATTLE = 'battle'
    DEFAULT = LOGO


ScreenInfo = namedtuple('ScreenInfo', ('mono', 'colored', 'frame'))

def _lazyLoad(className):
    moduleName, className = className.rsplit('.', 1)
    module = importlib.import_module(moduleName)
    return getattr(module, className)


def __lll(relName):
    return lambda : _lazyLoad(className='gui.Scaleform.daapi.view.logitech.' + relName)


_SCREENS = {_LogitechScreen.LOGO: ScreenInfo(mono=__lll('logo_screen.LogitechMonitorLogoMonoScreen'), colored=__lll('logo_screen.LogitechMonitorLogoColoredScreen'), frame='logo'),
 _LogitechScreen.HANGAR: ScreenInfo(mono=__lll('hangar_screen.LogitechMonitorHangarMonoScreen'), colored=__lll('hangar_screen.LogitechMonitorHangarColoredScreen'), frame='stats'),
 _LogitechScreen.BATTLE_LOADING: ScreenInfo(mono=__lll('battle_loading.LogitechMonitorBattleLoadingMonoScreen'), colored=__lll('battle_loading.LogitechMonitorBattleLoadingColoredScreen'), frame='mapLoading'),
 _LogitechScreen.BATTLE: ScreenInfo(mono=__lll('battle_screen.LogitechMonitorBattleMonoScreen'), colored=__lll('battle_screen.LogitechMonitorBattleColoredScreen'), frame='battle')}

class LogitechMonitorEntry(object):
    """
    LogitechMonitor still uses AS2, cause it's an old crap.
    Monitor lives from start to the client's end, cause we use same flash object for all screens
    We embed different logic in screens which works with same flash object
    """

    def __init__(self):
        super(LogitechMonitorEntry, self).__init__()
        self.__navigator = _ScreenNavigator()
        self.__flashObject = None
        self.__screen = None
        self.__screenName = None
        self.__frame = None
        self.__clearDeviceInfo()
        return

    @property
    def isInitialized(self):
        """
        :return: lcd was initialized and we've got notification and performed initial setup
        """
        return self.__width != 0 and self.__height != 0

    @property
    def isColored(self):
        return self.__isColored

    @property
    def component(self):
        return self.__flashObject.component if self.__flashObject else None

    @property
    def screen(self):
        """
        :return: Returns screen name
        """
        return self.__screenName

    def activate(self):
        if LcdKeyboard.g_instance:
            LcdKeyboard.g_instance.changeNotifyCallback = self.__onMonitorInitialized
        else:
            LOG_DEBUG("Can't activate")

    def close(self):
        if LcdKeyboard.g_instance:
            LcdKeyboard.g_instance.changeNotifyCallback = None
        self._stop()
        return

    def startScreen(self, screenName):
        assert screenName is not None
        if not self.isInitialized:
            LOG_WARNING("Monitor isn't active yet. Ignore.", screenName)
            return
        elif screenName == self.__screenName:
            LOG_DEBUG('Requested screen is active already. Ignore', screenName)
            return
        else:
            self.__startScreen(screenName)
            return

    def changeView(self):
        """
        Switch to the next view inside screen if it has more than one
        """
        if self.__screen is not None:
            LOG_DEBUG('Changing view')
            self.__screen.as_changeViewS()
        else:
            LOG_WARNING("No active screen. Can't change view.")
        return

    def _start(self, isColored, width, height):
        LOG_DEBUG('Starting monitor', isColored, width, height)
        self.__isColored = isColored
        self.__width = width
        self.__height = height
        self.__navigator.start(weakref.proxy(self))
        g_keyEventHandlers.add(self.__handleKeyEvent)

    def _stop(self):
        self.__clearDeviceInfo()
        self.__navigator.stop()
        if self.__handleKeyEvent in g_keyEventHandlers:
            g_keyEventHandlers.remove(self.__handleKeyEvent)
        self.__stopCurrentScreen()
        self.__releaseFlash()

    def __onMonitorInitialized(self, isEnabled, isColored, width, height):
        """
        Currently it's fired only if device is created or released while callback is set
        :param isEnabled if device is initialized, otherwise it's released
        """
        if self.isInitialized == isEnabled and self.__isColored == isColored and self.__width == width and self.__height:
            LOG_DEBUG('Monitor is initialized already. Ignore.')
            return
        if isEnabled:
            LOG_DEBUG('Monitor is attahced', isColored, width, height)
            self._start(isColored, width, height)
        else:
            LOG_DEBUG('Monitor is detached')
            self._stop()
        needOption = isEnabled and isColored
        KeyboardSettings.hideGroup('logitech_keyboard', hide=not needOption)

    def __clearDeviceInfo(self):
        self.__isColored = True
        self.__width = 0
        self.__height = 0

    def __handleKeyEvent(self, event):
        cmdMap = CommandMapping.g_instance
        isDown, key, _, isRepeat = convertKeyEvent(event)
        if cmdMap.isFired(CommandMapping.CMD_LOGITECH_SWITCH_VIEW, key) and isDown and not isRepeat:
            self.changeView()

    def __startScreen(self, screenName):
        currentFrame = self.__frame
        self.__stopCurrentScreen()
        screenInfo = _SCREENS[screenName]
        screenCls = screenInfo.colored() if self.__isColored else screenInfo.mono()
        frameName = screenInfo.frame
        LOG_DEBUG("Starting screen '{}' with frame '{}'".format(screenName, frameName))
        self.__screenName = screenName
        self.__screen = screenCls(frameName)
        self.__frame = frameName
        self.__createFlashIfNeeded()
        self.__screen.start(self.__flashObject)
        if currentFrame == frameName:
            LOG_DEBUG("New screen is loaded with same frame. Forcing 'onLoaded' callback", frameName)
            self.__screen.loadedWithOldFrame()

    def __stopCurrentScreen(self):
        if self.__screen is not None:
            self.__frame = None
            self.__screen.stop()
            self.__screen = None
            self.__screenName = None
        return

    def __createFlashIfNeeded(self):
        if self.__flashObject is None:
            self.__flashObject = Flash(_LOGITECH_SWF_COLORED) if self.__isColored else Flash(_LOGITECH_SWF_MONO)
            self.__flashObject.movie.wg_outputToLogitechLcd = True
        return

    def __releaseFlash(self):
        if self.__flashObject is not None:
            self.__flashObject.close()
            self.__flashObject = None
        return


_EventToScreen = namedtuple('_EventToScreen', ('screen', 'eventTypes', 'scope'))
_EVENT_TO_SCREEN = (_EventToScreen(screen=_LogitechScreen.LOGO, eventTypes=(VIEW_ALIAS.LOGIN,), scope=EVENT_BUS_SCOPE.LOBBY),
 _EventToScreen(screen=_LogitechScreen.HANGAR, eventTypes=(VIEW_ALIAS.LOBBY,), scope=EVENT_BUS_SCOPE.LOBBY),
 _EventToScreen(screen=_LogitechScreen.BATTLE_LOADING, eventTypes=VIEW_ALIAS.LOADINGS, scope=EVENT_BUS_SCOPE.LOBBY),
 _EventToScreen(screen=_LogitechScreen.BATTLE, eventTypes=VIEW_ALIAS.BATTLE_PAGES, scope=EVENT_BUS_SCOPE.BATTLE))

class _ScreenNavigator(EventSystemEntity):
    """ Connects screens navigation from main UI with logitech's
    """

    def __init__(self):
        super(_ScreenNavigator, self).__init__()
        self.monitor = None
        return

    def start(self, monitor):
        self.monitor = monitor
        startScreen = self._guessCurrentScreen() or _LogitechScreen.DEFAULT
        self.monitor.startScreen(startScreen)
        for ets in _EVENT_TO_SCREEN:
            for eventType in ets.eventTypes:
                self.addListener(eventType, self.__eventReceived, ets.scope)

        self.addListener(AppLifeCycleEvent.INITIALIZED, self.__appInitialized, EVENT_BUS_SCOPE.GLOBAL)

    def stop(self):
        self.removeListener(AppLifeCycleEvent.INITIALIZED, self.__appInitialized, EVENT_BUS_SCOPE.GLOBAL)
        for ets in _EVENT_TO_SCREEN:
            for eventType in ets.eventTypes:
                self.removeListener(eventType, self.__eventReceived, ets.scope)

        self.monitor = None
        return

    def _guessCurrentScreen(self):
        app = g_appLoader.getApp()
        if app is not None:
            if hasattr(app, 'containerManager'):
                view = app.containerManager.getView(ViewTypes.DEFAULT)
                if view is not None:
                    alias = view.settings.alias
                    for ets in _EVENT_TO_SCREEN:
                        if alias in ets.eventTypes:
                            LOG_DEBUG('Guessed current screen', ets.screen)
                            return ets.screen

            if app.appNS is APP_NAME_SPACE.SF_BATTLE:
                return _LogitechScreen.BATTLE
        return

    def __eventReceived(self, event):
        if self.monitor is not None:
            eventType = event.eventType
            for ets in _EVENT_TO_SCREEN:
                if eventType in ets.eventTypes:
                    self.monitor.startScreen(ets.screen)
                    return

            LOG_WARNING('Unexpected event', eventType)
        return

    def __appInitialized(self, event):
        if event.ns == APP_NAME_SPACE.SF_BATTLE:
            self.monitor.startScreen(_LogitechScreen.BATTLE)
