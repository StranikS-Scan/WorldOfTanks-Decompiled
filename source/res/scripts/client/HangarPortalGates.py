# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarPortalGates.py
import WWISE
from ClientSelectableWebLinksOpener import ClientSelectableWebLinksOpener
from gui.shared import g_eventBus, events

class HangarPortalGates(ClientSelectableWebLinksOpener):

    def __init__(self):
        super(HangarPortalGates, self).__init__()
        self.__isMouseOver = False
        self.__isDragging = False
        self.__mouseOverMusicStarted = False
        self.__startEventName = self.mouseOverMusic
        self.__stopEventName = self.mouseOverMusic + '_stop'

    def onEnterWorld(self, prereqs):
        super(HangarPortalGates, self).onEnterWorld(prereqs)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)

    def onLeaveWorld(self):
        super(HangarPortalGates, self).onLeaveWorld()
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        self.__stopMusic()

    def highlight(self, show):
        super(HangarPortalGates, self).highlight(show)
        if not self.enabled:
            return
        if not self.mouseOverMusic:
            return
        self.__isMouseOver = show
        if self.__isDragging:
            return
        if show:
            self.__startMusic()
        else:
            self.__stopMusic()

    def __startMusic(self):
        if self.__mouseOverMusicStarted:
            return
        WWISE.WW_eventGlobal(self.__startEventName)
        self.__mouseOverMusicStarted = True

    def __stopMusic(self):
        if not self.__mouseOverMusicStarted:
            return
        WWISE.WW_eventGlobal(self.__stopEventName)
        self.__mouseOverMusicStarted = False

    def __onNotifyCursorDragging(self, event):
        self.__isDragging = event.ctx.get('isDragging', False)
        if self.__isDragging:
            self.__stopMusic()
        elif self.__isMouseOver:
            self.__startMusic()
