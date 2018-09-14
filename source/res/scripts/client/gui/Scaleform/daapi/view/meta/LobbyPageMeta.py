# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyPageMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyPageMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def moveSpace(self, x, y, delta):
        """
        :param x:
        :param y:
        :param delta:
        :return :
        """
        self._printOverrideError('moveSpace')

    def getSubContainerType(self):
        """
        :return String:
        """
        self._printOverrideError('getSubContainerType')

    def notifyCursorOver3dScene(self, isOver3dScene):
        """
        :param isOver3dScene:
        :return :
        """
        self._printOverrideError('notifyCursorOver3dScene')

    def as_showHelpLayoutS(self):
        """
        :return :
        """
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        """
        :return :
        """
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None
