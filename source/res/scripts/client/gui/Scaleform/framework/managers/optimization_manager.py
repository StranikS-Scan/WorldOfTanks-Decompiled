# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/optimization_manager.py
import GUI
import Math
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.abstract.GraphicsOptimizationManagerMeta import GraphicsOptimizationManagerMeta
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from ids_generators import Int32IDGenerator
from skeletons.account_helpers.settings_core import ISettingsCore
_PERMANENT_SETTING_ID = ''

class OptimizationSetting(object):
    __slots__ = ('__id', '__isInvert')

    def __init__(self, settingID=_PERMANENT_SETTING_ID, isInvert=False):
        super(OptimizationSetting, self).__init__()
        self.__id = settingID
        self.__isInvert = isInvert

    @property
    def id(self):
        return self.__id

    @property
    def isInvert(self):
        return self.__isInvert


def _getRectBounds(x, y, width, height):
    x, y, width, height = (int(x),
     int(y),
     int(width),
     int(height))
    return Math.Vector4(x, y, x + width, y + height)


def _getSettingsNames(config):
    return set([ setting.id for setting in config.itervalues() if setting.id != _PERMANENT_SETTING_ID ])


class GraphicsOptimizationManager(GraphicsOptimizationManagerMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, config=None):
        super(GraphicsOptimizationManager, self).__init__()
        self.__idsGenerator = Int32IDGenerator()
        self.__optimizer = GUI.WGUIOptimizer()
        self.__cache = {}
        self.__isUiVisible = True
        self.__config = config or {}
        self.__settingsNames = _getSettingsNames(self.__config)

    def registerOptimizationArea(self, x, y, width, height):
        bounds = _getRectBounds(x, y, width, height)
        optimizationID = self.__idsGenerator.next()
        self.__cache[optimizationID] = bounds
        self.__optimizer.registerRect(optimizationID, bounds)
        return optimizationID

    def unregisterOptimizationArea(self, optimizationID):
        if optimizationID in self.__cache:
            self.__cache.pop(optimizationID)
            self.__optimizer.unregisterRect(optimizationID)
        else:
            LOG_ERROR('Graphics optimization ID is not found', optimizationID)

    def updateOptimizationArea(self, optimizationID, x, y, width, height):
        if optimizationID in self.__cache:
            bounds = _getRectBounds(x, y, width, height)
            oldBounds = self.__cache[optimizationID]
            if bounds != oldBounds:
                self.__cache[optimizationID] = bounds
                self.__optimizer.updateRect(optimizationID, bounds)
        else:
            LOG_ERROR('Graphics optimization ID is not found', optimizationID)

    def isOptimizationAvailable(self, alias):
        return alias in self.__config

    def isOptimizationEnabled(self, alias):
        if alias in self.__config:
            settings = self.__config.get(alias)
            if settings.id == _PERMANENT_SETTING_ID:
                isEnabled = True
            else:
                value = self.settingsCore.getSetting(settings.id)
                isEnabled = not value if settings.isInvert else value
        else:
            isEnabled = False
        return self.__isUiVisible and isEnabled

    def _populate(self):
        super(GraphicsOptimizationManager, self)._populate()
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.addListener(events.GameEvent.GUI_VISIBILITY, self.__handleGuiVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        super(GraphicsOptimizationManager, self)._dispose()
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.removeListener(events.GameEvent.GUI_VISIBILITY, self.__handleGuiVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        for optimizationID in self.__cache.iterkeys():
            self.__optimizer.unregisterRect(optimizationID)

        self.__cache.clear()

    def __handleGuiVisibility(self, event):
        self.__isUiVisible = event.ctx['visible']
        self.as_invalidateRectanglesS()

    def __onSettingsChanged(self, diff):
        if self.__settingsNames.intersection(diff.keys()):
            self.as_invalidateRectanglesS()

    def __getSettingsIds(self, config):
        return set([ setting.id for setting in config.itervalues() ])
