# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattlePageMeta.py
from gui.Scaleform.framework.entities.View import View

class BattlePageMeta(View):

    def as_checkDAAPIS(self):
        return self.flashObject.as_checkDAAPI() if self._isDAAPIInited() else None

    def as_setPostmortemTipsVisibleS(self, value):
        return self.flashObject.as_setPostmortemTipsVisible(value) if self._isDAAPIInited() else None

    def as_setComponentsVisibilityS(self, visible, hidden):
        """
        :param visible: Represented by Vector.<String> (AS)
        :param hidden: Represented by Vector.<String> (AS)
        """
        return self.flashObject.as_setComponentsVisibility(visible, hidden) if self._isDAAPIInited() else None

    def as_isComponentVisibleS(self, componentKey):
        return self.flashObject.as_isComponentVisible(componentKey) if self._isDAAPIInited() else None

    def as_getComponentsVisibilityS(self):
        return self.flashObject.as_getComponentsVisibility() if self._isDAAPIInited() else None

    def as_toggleCtrlPressFlagS(self, isCtrlPressed):
        return self.flashObject.as_toggleCtrlPressFlag(isCtrlPressed) if self._isDAAPIInited() else None
