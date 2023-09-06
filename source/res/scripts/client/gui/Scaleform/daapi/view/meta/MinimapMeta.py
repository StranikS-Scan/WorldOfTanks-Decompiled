# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MinimapMeta(BaseDAAPIComponent):

    def onMinimapClicked(self, x, y, buttonIdx, mapScaleIndex):
        self._printOverrideError('onMinimapClicked')

    def applyNewSize(self, sizeIndex):
        self._printOverrideError('applyNewSize')

    def as_setSizeS(self, size):
        return self.flashObject.as_setSize(size) if self._isDAAPIInited() else None

    def as_setVisibleS(self, isVisible):
        return self.flashObject.as_setVisible(isVisible) if self._isDAAPIInited() else None

    def as_setAlphaS(self, alpha):
        return self.flashObject.as_setAlpha(alpha) if self._isDAAPIInited() else None

    def as_showVehiclesNameS(self, visibility):
        return self.flashObject.as_showVehiclesName(visibility) if self._isDAAPIInited() else None

    def as_setBackgroundS(self, path):
        return self.flashObject.as_setBackground(path) if self._isDAAPIInited() else None

    def as_enableHintPanelWithDataS(self, isStrategicArtyView, isSPG):
        return self.flashObject.as_enableHintPanelWithData(isStrategicArtyView, isSPG) if self._isDAAPIInited() else None

    def as_disableHintPanelS(self):
        return self.flashObject.as_disableHintPanel() if self._isDAAPIInited() else None

    def as_updateHintPanelDataS(self, isStrategicArtyView, isSPG):
        return self.flashObject.as_updateHintPanelData(isStrategicArtyView, isSPG) if self._isDAAPIInited() else None

    def as_initPrebattleSizeS(self, preferableSize):
        return self.flashObject.as_initPrebattleSize(preferableSize) if self._isDAAPIInited() else None

    def as_setScenarioEventS(self, id, path, type):
        return self.flashObject.as_setScenarioEvent(id, path, type) if self._isDAAPIInited() else None

    def as_setScenarioEventVisibleS(self, id, visible):
        return self.flashObject.as_setScenarioEventVisible(id, visible) if self._isDAAPIInited() else None

    def as_clearScenarioEventS(self, id):
        return self.flashObject.as_clearScenarioEvent(id) if self._isDAAPIInited() else None
