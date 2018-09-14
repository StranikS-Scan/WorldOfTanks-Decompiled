# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MinimapMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def setAttentionToCell(self, x, y, isRightClick):
        """
        :param x:
        :param y:
        :param isRightClick:
        :return :
        """
        self._printOverrideError('setAttentionToCell')

    def as_setSizeS(self, size):
        """
        :param size:
        :return :
        """
        return self.flashObject.as_setSize(size) if self._isDAAPIInited() else None

    def as_setVisibleS(self, isVisible):
        """
        :param isVisible:
        :return :
        """
        return self.flashObject.as_setVisible(isVisible) if self._isDAAPIInited() else None

    def as_setAlphaS(self, alpha):
        """
        :param alpha:
        :return :
        """
        return self.flashObject.as_setAlpha(alpha) if self._isDAAPIInited() else None

    def as_showVehiclesNameS(self, visibility):
        """
        :param visibility:
        :return :
        """
        return self.flashObject.as_showVehiclesName(visibility) if self._isDAAPIInited() else None

    def as_setBackgroundS(self, path):
        """
        :param path:
        :return :
        """
        return self.flashObject.as_setBackground(path) if self._isDAAPIInited() else None
