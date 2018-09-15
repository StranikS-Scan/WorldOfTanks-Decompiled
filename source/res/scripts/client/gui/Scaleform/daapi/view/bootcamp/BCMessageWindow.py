# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCMessageWindow.py
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.meta.BCMessageWindowMeta import BCMessageWindowMeta
import SoundGroups
from gui.Scaleform.genConsts.BOOTCAMP_MESSAGE_ALIASES import BOOTCAMP_MESSAGE_ALIASES

class BCMessageWindow(BCMessageWindowMeta):

    def __init__(self, data):
        super(BCMessageWindow, self).__init__()
        self.__messagesData = data
        self.__removedCallback = data.get('removedCallback', None)
        self.__buttonCallback = None
        self.__isButtonClicked = False
        return

    def onMessageButtonClicked(self):
        self.__isButtonClicked = True
        from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
        from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_NATIONS_WINDOW, None, {'callback': self.__removedCallback}), EVENT_BUS_SCOPE.LOBBY)
        return

    def onMessageAppear(self, type):
        if type == BOOTCAMP_MESSAGE_ALIASES.RENDERER_FIN_UI:
            SoundGroups.g_instance.playSound2D('bc_info_line_graduate')
        elif type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO:
            SoundGroups.g_instance.playSound2D('bc_info_line_universal')

    def onMessageDisappear(self, type):
        if type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO:
            SoundGroups.g_instance.playSound2D('bc_info_line_disappear')

    def onMessageRemoved(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.resumeLesson()
        if self.__removedCallback is not None and not self.__isButtonClicked:
            from bootcamp.Bootcamp import g_bootcamp
            if g_bootcamp.getLessonNum() == 1:
                g_bootcamp.changeNation(g_bootcamp.nation, self.__removedCallback)
            else:
                self.__removedCallback()
                self.__removedCallback = None
        self.destroy()
        return

    def _populate(self):
        super(BCMessageWindow, self)._populate()
        self.as_setMessageDataS(self.__messagesData['messages'])
        g_bootcampEvents.onRequestBootcampMessageWindowClose += self.onMessageRemoved

    def _dispose(self):
        super(BCMessageWindow, self)._dispose()
        g_bootcampEvents.onRequestBootcampMessageWindowClose -= self.onMessageRemoved
