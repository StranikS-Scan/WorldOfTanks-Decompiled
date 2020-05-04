# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampGUI.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager, plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings as _markers2d_settings
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP
from BootCampEvents import g_bootcampEvents
from BootcampConstants import UI_STATE
from helpers import i18n
_Event = events.ComponentEvent

def getDirectionIndicator():
    indicator = None
    try:
        indicator = indicators.createDirectIndicator()
    except Exception:
        LOG_CURRENT_EXCEPTION_BOOTCAMP()

    return indicator


class BootcampMarkersComponent(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BootcampMarkersComponent, self)._setupPlugins(arenaVisitor)
        setup['bootcamp'] = BootcampStaticObjectsPlugin
        return setup


class BootcampStaticObjectsPlugin(plugins.MarkerPlugin):
    __slots__ = ('__weakref__', '__objects')

    def __init__(self, parentObj):
        super(BootcampStaticObjectsPlugin, self).__init__(parentObj)
        self.__objects = {}

    def start(self):
        g_bootcampEvents.onBCGUIComponentLifetime(BATTLE_VIEW_ALIASES.MARKERS_2D, self)

    def stop(self):
        g_bootcampEvents.onBCGUIComponentLifetime(BATTLE_VIEW_ALIASES.MARKERS_2D, None)
        return

    def addStaticObject(self, objectID, position):
        if objectID in self.__objects:
            return False
        markerID = self._createMarkerWithPosition(_markers2d_settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER, position, active=True)
        self.__objects[objectID] = markerID
        return True

    def addDynObject(self, objectID, matrix):
        if objectID in self.__objects:
            return False
        markerID = self._createMarkerWithMatrix(_markers2d_settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER, matrix, active=True)
        self.__objects[objectID] = markerID
        return True

    def delStaticObject(self, objectID):
        markerID = self.__objects.pop(objectID, None)
        if markerID is not None:
            self._destroyMarker(markerID)
            return True
        else:
            return False

    def setupStaticObject(self, objectID, shape, minDistance, maxDistance, distance, color):
        if objectID in self.__objects:
            self._invokeMarker(self.__objects[objectID], 'init', shape, minDistance, maxDistance, distance, i18n.makeString(INGAME_GUI.MARKER_METERS), color)

    def setDistanceToObject(self, objectID, distance):
        if objectID in self.__objects:
            self._invokeMarker(self.__objects[objectID], 'setDistance', distance)

    def setBlinking(self, objectID, speed, isShow):
        if objectID in self.__objects:
            self._invokeMarker(self.__objects[objectID], 'setBlinking', isShow, speed)


class BootcampGUI(object):

    def __init__(self):
        super(BootcampGUI, self).__init__()
        addListener = g_eventBus.addListener
        addListener(_Event.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_Event.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_bootcampEvents.onBCGUIComponentLifetime += self.onBCGUIComponentLifetime
        self.__minimap = None
        self.__markers2D = None
        self.__inited = False
        return

    @property
    def inited(self):
        return self.__inited

    def getMinimapPlugin(self):
        return self.__minimap

    def getMarkers2DPlugin(self):
        return self.__markers2D

    def fini(self):
        self.clear()

    def reload(self):
        self.__minimap = None
        self.__markers2D = None
        self.__inited = False
        return

    def clear(self):
        self.__minimap = None
        self.__markers2D = None
        self.__inited = False
        g_bootcampEvents.onBCGUIComponentLifetime -= self.onBCGUIComponentLifetime
        removeListener = g_eventBus.removeListener
        removeListener(_Event.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_Event.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def onBCGUIComponentLifetime(self, alias, component):
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D:
            self.__markers2D = component
        self.checkInit()

    def checkInit(self):
        newInit = self.__minimap is not None and self.__markers2D is not None
        if newInit != self.__inited and not self.__inited:
            g_bootcampEvents.onUIStateChanged(UI_STATE.START)
        self.__inited = newInit
        return

    def __onComponentRegistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP:
            plugin = event.componentPy.getPlugin('bootcamp')
            if plugin is not None:
                self.__minimap = plugin
        self.checkInit()
        return

    def __onComponentUnregistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP and self.__minimap is not None:
            self.__minimap.stop()
            self.__minimap = None
            self.__inited = False
        return
