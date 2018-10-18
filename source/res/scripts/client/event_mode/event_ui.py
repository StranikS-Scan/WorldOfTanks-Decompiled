# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_mode/event_ui.py
from bootcamp.BootcampConstants import UI_STATE
from bootcamp.BootcampGUI import BootcampStaticObjectsPlugin
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from event_mode.events import g_eventModeEvents

class EventStaticObjectsPlugin(BootcampStaticObjectsPlugin):

    def start(self):
        g_eventModeEvents.onUIComponentLifetime(BATTLE_VIEW_ALIASES.MARKERS_2D, self)

    def stop(self):
        g_eventModeEvents.onUIComponentLifetime(BATTLE_VIEW_ALIASES.MARKERS_2D, None)
        return


class EventUI(object):

    def __init__(self):
        super(EventUI, self).__init__()
        self.__markers2D = None
        self.__inited = False
        g_eventModeEvents.onUIComponentLifetime += self.onUIComponentLifetime
        return

    @property
    def inited(self):
        return self.__inited

    def getMarkers2DPlugin(self):
        return self.__markers2D

    def onUIComponentLifetime(self, alias, component):
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D:
            self.__markers2D = component
            self.__checkState()

    def __clear(self):
        self.__markers2D = None
        self.__inited = False
        g_eventModeEvents.onUIComponentLifetime -= self.onUIComponentLifetime
        return

    def __checkState(self):
        isInited = self.__markers2D is not None
        if isInited is not self.__inited:
            self.__inited = isInited
            uiState = UI_STATE.START if self.__inited else UI_STATE.STOP
            g_eventModeEvents.onUIStateChanged(uiState)
            if uiState == UI_STATE.STOP:
                self.__clear()
        return
