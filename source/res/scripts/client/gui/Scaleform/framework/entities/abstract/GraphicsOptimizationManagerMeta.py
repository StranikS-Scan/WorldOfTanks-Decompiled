# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/GraphicsOptimizationManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class GraphicsOptimizationManagerMeta(BaseDAAPIComponent):

    def registerOptimizationArea(self, x, y, width, height):
        self._printOverrideError('registerOptimizationArea')

    def unregisterOptimizationArea(self, optimizationID):
        self._printOverrideError('unregisterOptimizationArea')

    def updateOptimizationArea(self, optimizationID, x, y, width, height):
        self._printOverrideError('updateOptimizationArea')

    def isOptimizationAvailable(self, alias):
        self._printOverrideError('isOptimizationAvailable')

    def isOptimizationEnabled(self, alias):
        self._printOverrideError('isOptimizationEnabled')

    def as_invalidateRectanglesS(self):
        return self.flashObject.as_invalidateRectangles() if self._isDAAPIInited() else None
