# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampGUI.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager, plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings as _markers2d_settings
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP
from BootCampEvents import g_bootcampEvents
from BootcampConstants import UI_STATE
from helpers import i18n
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from frameworks.wulf import WindowLayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
import BigWorld
_Event = events.ComponentEvent

def getDirectionIndicator():
    indicator = None
    try:
        indicator = indicators.createDirectIndicator()
    except Exception:
        LOG_CURRENT_EXCEPTION_BOOTCAMP()

    return indicator


class BootcampMarkersComponent(MarkersManager):

    def setFocusVehicle(self, vehicleID):
        pass

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


class BaseBootcampGUI(object):

    def __init__(self):
        g_bootcampEvents.onBCGUIComponentLifetime += self.onBCGUIComponentLifetime
        self._minimap = None
        self._markers2D = None
        self._inited = False
        return

    @property
    def inited(self):
        return self._inited

    def getMinimapPlugin(self):
        return self._minimap

    def getMarkers2DPlugin(self):
        return self._markers2D

    def fini(self):
        self.clear()

    def reload(self):
        self._minimap = None
        self._markers2D = None
        self._inited = False
        return

    def clear(self):
        self._minimap = None
        self._markers2D = None
        self._inited = False
        g_bootcampEvents.onBCGUIComponentLifetime -= self.onBCGUIComponentLifetime
        return

    def onBCGUIComponentLifetime(self, alias, component):
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D:
            self._markers2D = component


class BootcampGUI(BaseBootcampGUI):

    def __init__(self):
        super(BootcampGUI, self).__init__()
        addListener = g_eventBus.addListener
        addListener(_Event.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_Event.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, scope=EVENT_BUS_SCOPE.GLOBAL)

    def clear(self):
        super(BootcampGUI, self).clear()
        removeListener = g_eventBus.removeListener
        removeListener(_Event.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_Event.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, scope=EVENT_BUS_SCOPE.GLOBAL)

    def onBCGUIComponentLifetime(self, alias, component):
        super(BootcampGUI, self).onBCGUIComponentLifetime(alias, component)
        self.checkInit()

    def checkInit(self):
        newInit = self._minimap is not None and self._markers2D is not None
        if newInit != self._inited and not self._inited:
            g_bootcampEvents.onUIStateChanged(UI_STATE.START)
        self._inited = newInit
        return

    def __onComponentRegistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP:
            plugin = event.componentPy.getPlugin('bootcamp')
            if plugin is not None:
                self._minimap = plugin
        self.checkInit()
        return

    def __onComponentUnregistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP and self._minimap is not None:
            self._minimap.stop()
            self._minimap = None
            self._inited = False
        return


class RTSBootcampGUI(BaseBootcampGUI):

    def __init__(self):
        super(RTSBootcampGUI, self).__init__()
        avatar = BigWorld.player()
        if avatar is None:
            return
        else:
            app = avatar.appLoader.getApp()
            battleContainer = app.containerManager.getContainer(WindowLayer.VIEW)
            battleView = battleContainer.findView(ViewKey(VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE))
            externList = battleView.getExternals()
            markersList = [ x for x in externList if x.alias == BATTLE_VIEW_ALIASES.MARKERS_2D ]
            markerComponent = markersList[0] if markersList else None
            if markerComponent is None:
                return
            self._minimap = battleView.components['minimap'].getPlugin('bootcamp')
            self._markers2D = markerComponent.getPlugin('bootcamp')
            return

    @property
    def inited(self):
        return True
