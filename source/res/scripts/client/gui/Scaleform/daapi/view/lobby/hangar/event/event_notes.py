# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_notes.py
import ResMgr
import GUI
import SoundGroups
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby import BrowserView
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.daapi.view.lobby.hangar.web_handlers import createHangarWebHandlers
from gui.server_events.events_dispatcher import showEventHangar
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class EventNotesTab(BrowserView):
    __background_alpha__ = 0.0
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=VIEW_ALIAS.EVENT_NOTES, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_halloween_2019_hangar_metagame_music_evidence', exitEvent='ev_halloween_2019_hangar_metagame_music_base')

    def __init__(self, ctx=None):
        super(EventNotesTab, self).__init__({'url': ResMgr.resolveToAbsolutePath(GUI_SETTINGS.EventHangarNotesURL),
         'webHandlers': createHangarWebHandlers(onBrowserClose=self.onCloseView),
         'browserParams': makeBrowserParams(bgAlpha=0)})
        self.__blur = GUI.WGUIBackgroundBlur()

    def onCloseView(self):
        showEventHangar()

    def onEscapePress(self):
        self.onCloseView()

    def _populate(self):
        super(EventNotesTab, self)._populate()
        self.__blur.enable = True
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        SoundGroups.g_instance.playSound2D('ev_halloween_2020_evidence_exit')
        self.__blur.enable = False
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        super(EventNotesTab, self)._dispose()
