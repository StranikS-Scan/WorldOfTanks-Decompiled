# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_about.py
import ResMgr
import GUI
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.server_events.events_dispatcher import showEventHangar
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventBrowserScreenMeta import EventBrowserScreenMeta
from web.web_client_api import webApiCollection
from web.web_client_api.sound import EventHangarSoundWebApi, SoundWebApi

class EventAboutTab(EventBrowserScreenMeta):
    __background_alpha__ = 0.0
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=VIEW_ALIAS.EVENT_ABOUT, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_halloween_2019_hangar_metagame_music_about', exitEvent='ev_halloween_2019_hangar_metagame_music_base')

    def __init__(self, ctx=None):
        url = ResMgr.resolveToAbsolutePath(GUI_SETTINGS.EventAboutPageURL)
        super(EventAboutTab, self).__init__(ctx={'url': url,
         'browserParams': makeBrowserParams(bgAlpha=0),
         'webHandlers': self.__makeHandlers()})
        self.__blur = GUI.WGUIBackgroundBlur()

    def onCloseView(self):
        showEventHangar()

    def onEscapePress(self):
        self.onCloseView()

    def _populate(self):
        super(EventAboutTab, self)._populate()
        self.__blur.enable = True
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.as_setBrowserPaddingS(True)

    def _dispose(self):
        self.__blur.enable = False
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        super(EventAboutTab, self)._dispose()

    def _getBrowserSkipEscape(self):
        return True

    @staticmethod
    def __makeHandlers():
        return webApiCollection(EventHangarSoundWebApi, SoundWebApi)
