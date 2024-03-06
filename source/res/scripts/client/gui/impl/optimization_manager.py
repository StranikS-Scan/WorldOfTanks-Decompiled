# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/optimization_manager.py
import logging
from frameworks.wulf import WindowStatus
from frameworks.wulf.gui_constants import ShowingStatus
from gui.graphics_optimization_controller.utils import rescaleRectBounds
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from skeletons.gui.game_control import IGraphicsOptimizationController
from visual_script_client.arena_blocks import dependency
_logger = logging.getLogger(__name__)
DEFAULT_APPLICATION_SCALE = 1.0

class GraphicsOptimizationManager(object):
    __optimizationController = dependency.descriptor(IGraphicsOptimizationController)

    def __init__(self):
        self.__gfWindowsOptimizationIDs = {}
        self.__windowsManager = None
        self.__scale = DEFAULT_APPLICATION_SCALE
        return

    def init(self, windowsManager, scale):
        self.__scale = scale
        self.__windowsManager = windowsManager
        self.__windowsManager.onWindowShowingStatusChanged += self.__onWindowShowingStatusChanged
        g_eventBus.addListener(GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResolutionChanged, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__optimizationController.onUiVisibilityToggled += self.__handleGuiVisibility
        self.__optimizationController.onSettingsChanged += self.__onSettingsChanged

    def fini(self):
        self.__optimizationController.onSettingsChanged -= self.__onSettingsChanged
        self.__optimizationController.onUiVisibilityToggled -= self.__handleGuiVisibility
        g_eventBus.removeListener(GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResolutionChanged, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__windowsManager.onWindowShowingStatusChanged -= self.__onWindowShowingStatusChanged
        self.__windowsManager = None
        self.__scale = DEFAULT_APPLICATION_SCALE
        for optimizationID in self.__gfWindowsOptimizationIDs.itervalues():
            self.__optimizationController.unregisterOptimizationArea(optimizationID)

        self.__gfWindowsOptimizationIDs.clear()
        return

    def switchOptimizationEnabled(self, value):
        self.__optimizationController.switchOptimizationEnabled(value)

    def __isOptimizationAvailable(self, alias):
        return self.__optimizationController.isOptimizationAvailable(alias)

    def __isOptimizationEnabled(self, alias):
        return self.__optimizationController.isOptimizationEnabled(alias)

    def __onAppResolutionChanged(self, event):
        scale = event.ctx.get('scale')
        if scale is not None:
            self.__scale = scale
            for uniqueID, optimizationID in self.__gfWindowsOptimizationIDs.iteritems():
                window = self.__windowsManager.getWindow(uniqueID)
                if window and window.content and window.windowStatus not in (WindowStatus.DESTROYING, WindowStatus.DESTROYED):
                    self.__optimizationController.updateOptimizationArea(optimizationID, *rescaleRectBounds(self.__scale, *(window.globalPosition + window.size)))
                _logger.warning('Window %d is loaded, but its content is None', uniqueID)

        else:
            _logger.warning('Parameter scale is missing in event ctx')
        return

    def __onWindowSizeChanged(self, uniqueID, width, height):
        optimizationID = self.__gfWindowsOptimizationIDs.get(uniqueID)
        if optimizationID:
            window = self.__windowsManager.getWindow(uniqueID)
            self.__optimizationController.updateOptimizationArea(optimizationID, *rescaleRectBounds(self.__scale, *(window.globalPosition + (width, height))))

    def __onWindowPositionChanged(self, uniqueID, x, y):
        optimizationID = self.__gfWindowsOptimizationIDs.get(uniqueID)
        if optimizationID:
            window = self.__windowsManager.getWindow(uniqueID)
            self.__optimizationController.updateOptimizationArea(optimizationID, *rescaleRectBounds(self.__scale, *((x, y) + window.size)))

    def __onWindowShowingStatusChanged(self, uniqueID, status):
        window = self.__windowsManager.getWindow(uniqueID)
        if window:
            if status == ShowingStatus.SHOWN.value:
                if window.content:
                    if self.__isOptimizationAvailable(window.content.layoutID) and self.__isOptimizationEnabled(window.content.layoutID):
                        optimizationID = self.__optimizationController.registerOptimizationArea(*rescaleRectBounds(self.__scale, *(window.globalPosition + window.size)))
                        self.__gfWindowsOptimizationIDs[uniqueID] = optimizationID
                        self.__addWindowListeners(window)
            elif status == ShowingStatus.HIDING.value:
                if uniqueID in self.__gfWindowsOptimizationIDs:
                    optimizationID = self.__gfWindowsOptimizationIDs.pop(uniqueID)
                    self.__optimizationController.unregisterOptimizationArea(optimizationID)
                    self.__removeWindowListeners(window)

    def __addWindowListeners(self, window):
        window.onSizeChanged += self.__onWindowSizeChanged
        window.onPositionChanged += self.__onWindowPositionChanged

    def __removeWindowListeners(self, window):
        window.onPositionChanged -= self.__onWindowPositionChanged
        window.onSizeChanged -= self.__onWindowSizeChanged

    def __invalidateRectangles(self):
        for uniqueID, optimizationID in self.__gfWindowsOptimizationIDs.copy().iteritems():
            window = self.__windowsManager.getWindow(uniqueID)
            if window and window.content:
                if self.__isOptimizationAvailable(window.content.layoutID) and self.__isOptimizationEnabled(window.content.layoutID):
                    if optimizationID is None:
                        optimizationID = self.__optimizationController.registerOptimizationArea(*rescaleRectBounds(self.__scale, *(window.globalPosition + window.size)))
                        self.__gfWindowsOptimizationIDs[uniqueID] = optimizationID
                        self.__addWindowListeners(window)
                else:
                    self.__removeWindowListeners(window)
                    self.__optimizationController.unregisterOptimizationArea(optimizationID)
                    self.__gfWindowsOptimizationIDs[uniqueID] = None

        return

    def __handleGuiVisibility(self):
        self.__invalidateRectangles()

    def __onSettingsChanged(self):
        self.__invalidateRectangles()
