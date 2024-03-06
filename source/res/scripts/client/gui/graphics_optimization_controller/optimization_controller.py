# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/graphics_optimization_controller/optimization_controller.py
import logging
import GUI
import Event
from gui.graphics_optimization_controller.settings import OPTIMIZED_VIEWS_SETTINGS
from gui.graphics_optimization_controller.utils import getRectBounds, PERMANENT_SETTING_ID, getSettingsNames
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.system_factory import collectOptimizedViews, registerOptimizedViews
from helpers import dependency
from ids_generators import Int32IDGenerator
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGraphicsOptimizationController
_logger = logging.getLogger(__name__)
registerOptimizedViews(OPTIMIZED_VIEWS_SETTINGS)

class GraphicsOptimizationController(IGraphicsOptimizationController):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(GraphicsOptimizationController, self).__init__()
        self.__idsGenerator = Int32IDGenerator()
        self.__optimizer = GUI.WGUIOptimizer()
        self.__cache = {}
        self.__config = {}
        self.__isUiVisible = True
        self.__settingsNames = getSettingsNames(self.__config)
        self.__em = Event.EventManager()
        self.onUiVisibilityToggled = Event.Event(self.__em)
        self.onSettingsChanged = Event.Event(self.__em)

    def init(self):
        self.__config.update(collectOptimizedViews())
        g_eventBus.addListener(events.GameEvent.GUI_VISIBILITY, self.__handleGuiVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged

    def fini(self):
        super(GraphicsOptimizationController, self).fini()
        self.__em.clear()
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_eventBus.removeListener(events.GameEvent.GUI_VISIBILITY, self.__handleGuiVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        for optimizationId in self.__cache.iterkeys():
            self.__optimizer.unregisterRect(optimizationId)

        self.__cache = {}

    def getConfig(self):
        return self.__config

    def updateConfig(self, config):
        self.__config.update(config)

    def registerOptimizationArea(self, x, y, width, height):
        if width < 0 or height < 0:
            _logger.warning('Optimization rect width and height can not be less than 0')
        bounds = getRectBounds(x, y, max(0, width), max(0, height))
        optimizationID = self.__idsGenerator.next()
        self.__cache[optimizationID] = bounds
        self.__optimizer.registerRect(optimizationID, bounds)
        return optimizationID

    def unregisterOptimizationArea(self, optimizationID):
        if optimizationID in self.__cache:
            self.__cache.pop(optimizationID)
            self.__optimizer.unregisterRect(optimizationID)
        else:
            _logger.error('Graphics optimization ID - %d is not found', optimizationID)

    def updateOptimizationArea(self, optimizationID, x, y, width, height):
        if optimizationID in self.__cache:
            bounds = getRectBounds(x, y, width, height)
            oldBounds = self.__cache[optimizationID]
            if bounds != oldBounds:
                self.__cache[optimizationID] = bounds
                self.__optimizer.updateRect(optimizationID, bounds)
        else:
            _logger.error('Graphics optimization ID - %d is not found', optimizationID)

    def switchOptimizationEnabled(self, value):
        self.__optimizer.setEnable(value)

    def getEnable(self):
        return self.__optimizer.getEnable()

    def isOptimizationAvailable(self, alias):
        return alias in self.__config

    def isOptimizationEnabled(self, alias):
        isEnabled = False
        if alias in self.__config:
            settings = self.__config.get(alias)
            if settings.id == PERMANENT_SETTING_ID:
                isEnabled = True
            else:
                value = self.__settingsCore.getSetting(settings.id)
                isEnabled = not value if settings.isInvert else value
        return self.__isUiVisible and isEnabled

    def __handleGuiVisibility(self, event):
        visibility = event.ctx['visible']
        if visibility != self.__isUiVisible:
            self.__isUiVisible = visibility
            self.onUiVisibilityToggled()

    def __onSettingsChanged(self, diff):
        if self.__settingsNames.intersection(diff.keys()):
            self.onSettingsChanged()
