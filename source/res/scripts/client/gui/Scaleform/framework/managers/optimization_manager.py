# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/optimization_manager.py
import logging
from gui.Scaleform.framework.entities.abstract.GraphicsOptimizationManagerMeta import GraphicsOptimizationManagerMeta
from helpers import dependency
from skeletons.gui.game_control import IGraphicsOptimizationController
_logger = logging.getLogger(__name__)

class GraphicsOptimizationManager(GraphicsOptimizationManagerMeta):
    __optimizationController = dependency.descriptor(IGraphicsOptimizationController)

    def __init__(self):
        super(GraphicsOptimizationManager, self).__init__()
        self.__optimizationIds = set()

    def registerOptimizationArea(self, x, y, width, height):
        optimizationID = self.__optimizationController.registerOptimizationArea(x, y, width, height)
        self.__optimizationIds.add(optimizationID)
        return optimizationID

    def unregisterOptimizationArea(self, optimizationID):
        if optimizationID in self.__optimizationIds:
            self.__optimizationController.unregisterOptimizationArea(optimizationID)
            self.__optimizationIds.remove(optimizationID)
        else:
            _logger.error('Graphics optimization ID - %d is not found', optimizationID)

    def updateOptimizationArea(self, optimizationID, x, y, width, height):
        self.__optimizationController.updateOptimizationArea(optimizationID, x, y, width, height)

    def isOptimizationAvailable(self, alias):
        return self.__optimizationController.isOptimizationAvailable(alias)

    def isOptimizationEnabled(self, alias):
        return self.__optimizationController.isOptimizationEnabled(alias)

    def switchOptimizationEnabled(self, value):
        self.__optimizationController.switchOptimizationEnabled(value)

    def getEnable(self):
        return self.__optimizationController.getEnable()

    def _populate(self):
        super(GraphicsOptimizationManager, self)._populate()
        self.as_switchOptimizationEnabledS(self.__optimizationController.getEnable())
        self.__optimizationController.onUiVisibilityToggled += self.__handleGuiVisibility
        self.__optimizationController.onSettingsChanged += self.__onSettingsChanged

    def _dispose(self):
        super(GraphicsOptimizationManager, self)._dispose()
        self.__optimizationController.onSettingsChanged -= self.__onSettingsChanged
        self.__optimizationController.onUiVisibilityToggled -= self.__handleGuiVisibility
        for optimizationID in self.__optimizationIds:
            self.__optimizationController.unregisterOptimizationArea(optimizationID)

        self.__optimizationIds.clear()

    def __handleGuiVisibility(self):
        self.as_invalidateRectanglesS()

    def __onSettingsChanged(self):
        self.as_invalidateRectanglesS()
