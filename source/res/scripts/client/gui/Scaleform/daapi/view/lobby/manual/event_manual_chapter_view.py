# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/event_manual_chapter_view.py
import logging
import GUI
import SoundGroups
from helpers import dependency
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.Scaleform.daapi.view.meta.ManualChapterViewMeta import ManualChapterViewMeta
from gui.Scaleform.daapi.view.lobby.manual.manual_view_base import ManualViewBase
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_event_controller import IGameEventController
_logger = logging.getLogger(__name__)
EVENT_CHAPTER_INDEX = 0
EVENT_CHAPTER_SECTION = 'event_chapters'
_UNSHOWN_STATUS = 'done'

class EventManualChapterView(ManualViewBase, ManualChapterViewMeta):
    gameEventController = dependency.descriptor(IGameEventController)
    settingsCore = dependency.descriptor(ISettingsCore)
    __background_alpha__ = 0
    __HANGAR_UI_NEWS_OUT_SOUND = 'ev_2019_secret_event_1_hangar_event_news_out'
    __HANGAR_UI_NEWS_SWIPE_SOUND = 'ev_2019_secret_event_1_hangar_event_news_swipe'

    def __init__(self, ctx=None):
        super(EventManualChapterView, self).__init__(ctx)
        self.__blur = GUI.WGUIBackgroundBlur()

    def closeView(self):
        self._close()
        g_eventDispatcher.loadEventHangar()
        SoundGroups.g_instance.playSound2D(self.__HANGAR_UI_NEWS_OUT_SOUND)

    def pageClosed(self):
        pass

    def pageChanged(self):
        SoundGroups.g_instance.playSound2D(self.__HANGAR_UI_NEWS_SWIPE_SOUND)

    def linkClicked(self, link):
        self.fireEvent(events.OpenLinkEvent(link))

    def _populate(self):
        super(EventManualChapterView, self)._populate()
        self.__blur.enable = True
        self.updateData(True)
        g_eventBus.handleEvent(events.ManualEvent(events.ManualEvent.CHAPTER_OPENED), scope=EVENT_BUS_SCOPE.LOBBY)

    def _destroy(self):
        super(EventManualChapterView, self)._destroy()
        self.__blur.enable = False

    def _getGameEventServerSetting(self, key, default=None):
        value = self.settingsCore.serverSettings.getGameEventStorage().get(key)
        return default if value is None else value

    def pageOpened(self, index):
        self.settingsCore.serverSettings.setEventManualShowed(index)
        self.updateData(False)

    def updateData(self, jumpToPage):
        serverSettings = self.settingsCore.serverSettings
        data = self.manualController.getChapterUIData(EVENT_CHAPTER_INDEX, EVENT_CHAPTER_SECTION)
        pages = data['pages']
        showIndex = 0
        for index in reversed(xrange(len(pages))):
            showed = serverSettings.isEventManualShowed(index)
            if not showed:
                pages[index]['status'] = _UNSHOWN_STATUS
                showIndex = index

        data['pages'] = pages
        self.as_setInitDataS(data)
        if jumpToPage:
            self.as_showPageS(showIndex)
            self.settingsCore.serverSettings.setEventManualShowed(showIndex)
