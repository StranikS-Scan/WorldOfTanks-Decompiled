# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattlePageMeta.py
from gui.Scaleform.framework.entities.View import View

class BattlePageMeta(View):

    def as_checkDAAPIS(self):
        return self.flashObject.as_checkDAAPI() if self._isDAAPIInited() else None

    def as_setPostmortemTipsVisibleS(self, value):
        return self.flashObject.as_setPostmortemTipsVisible(value) if self._isDAAPIInited() else None

    def as_setComponentsVisibilityS(self, visible, hidden):
        return self.flashObject.as_setComponentsVisibility(visible, hidden) if self._isDAAPIInited() else None

    def as_setComponentsVisibilityWithFadeS(self, visible, hidden):
        return self.flashObject.as_setComponentsVisibilityWithFade(visible, hidden) if self._isDAAPIInited() else None

    def as_isComponentVisibleS(self, componentKey):
        return self.flashObject.as_isComponentVisible(componentKey) if self._isDAAPIInited() else None

    def as_getComponentsVisibilityS(self):
        return self.flashObject.as_getComponentsVisibility() if self._isDAAPIInited() else None

    def as_toggleCtrlPressFlagS(self, isCtrlPressed):
        return self.flashObject.as_toggleCtrlPressFlag(isCtrlPressed) if self._isDAAPIInited() else None

    def as_createRoleDescriptionS(self):
        return self.flashObject.as_createRoleDescription() if self._isDAAPIInited() else None

    def as_setArtyShotIndicatorFlagS(self, isVisible):
        return self.flashObject.as_setArtyShotIndicatorFlag(isVisible) if self._isDAAPIInited() else None

    def as_togglePiercingPanelS(self):
        return self.flashObject.as_togglePiercingPanel() if self._isDAAPIInited() else None
