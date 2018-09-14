# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattlePageMeta.py
from gui.Scaleform.framework.entities.View import View

class BattlePageMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def as_checkDAAPIS(self):
        """
        :return :
        """
        return self.flashObject.as_checkDAAPI() if self._isDAAPIInited() else None

    def as_setPostmortemTipsVisibleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setPostmortemTipsVisible(value) if self._isDAAPIInited() else None

    def as_setComponentsVisibilityS(self, visible, hidden):
        """
        :param visible:
        :param hidden:
        :return :
        """
        return self.flashObject.as_setComponentsVisibility(visible, hidden) if self._isDAAPIInited() else None

    def as_isComponentVisibleS(self, componentKey):
        """
        :param componentKey:
        :return Boolean:
        """
        return self.flashObject.as_isComponentVisible(componentKey) if self._isDAAPIInited() else None

    def as_getComponentsVisibilityS(self):
        """
        :return Array:
        """
        return self.flashObject.as_getComponentsVisibility() if self._isDAAPIInited() else None

    def as_toggleCtrlPressFlagS(self, isCtrlPressed):
        """
        :param isCtrlPressed:
        :return :
        """
        return self.flashObject.as_toggleCtrlPressFlag(isCtrlPressed) if self._isDAAPIInited() else None
