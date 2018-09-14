# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MinimapMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def setAttentionToCell(self, x, y, isRightClick):
        self._printOverrideError('setAttentionToCell')

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
