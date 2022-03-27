# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSelectionMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleSelectionMeta(BaseDAAPIComponent):

    def setSelectionParams(self, topX, topY, bottomX, bottomY, finish):
        self._printOverrideError('setSelectionParams')

    def handleRightMouseBtn(self):
        self._printOverrideError('handleRightMouseBtn')

    def handleMouseOverUI(self, isOverUI):
        self._printOverrideError('handleMouseOverUI')

    def handleMouseWheel(self, delta):
        self._printOverrideError('handleMouseWheel')

    def as_setEnabledS(self, enabled):
        return self.flashObject.as_setEnabled(enabled) if self._isDAAPIInited() else None
