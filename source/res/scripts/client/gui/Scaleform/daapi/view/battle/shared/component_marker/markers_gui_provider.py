# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/component_marker/markers_gui_provider.py
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class MarkerGUIProvider(object):

    def __init__(self, pluginID):
        super(MarkerGUIProvider, self).__init__()
        self.__markers2DPlugin = None
        self.__minimapPlugin = None
        self.__inited = False
        self.__pluginID = pluginID
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def getMinimapPlugin(self):
        return self.__minimapPlugin

    def getMarkers2DPlugin(self):
        return self.__markers2DPlugin

    def clear(self):
        self.__minimapPlugin = None
        self.__markers2DPlugin = None
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def __onComponentRegistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP:
            plugin = event.componentPy.getPlugin(self.__pluginID)
            if plugin is not None:
                self.__minimapPlugin = plugin
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D:
            plugin = event.componentPy.getPlugin(self.__pluginID)
            if plugin is not None:
                self.__markers2DPlugin = plugin
        return

    def __onComponentUnregistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP and self.__minimapPlugin is not None:
            self.__minimapPlugin = None
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D and self.__markers2DPlugin is not None:
            self.__markers2DPlugin = None
        if self.__minimapPlugin is not None and self.__markers2DPlugin is not None:
            self.__inited = False
        return
