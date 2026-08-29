# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WTCrosshairPanelContainerMeta.py
from gui.Scaleform.daapi.view.battle.shared.crosshair.container import CrosshairPanelContainer

class WTCrosshairPanelContainerMeta(CrosshairPanelContainer):

    def as_showPlasmaIndicatorS(self, plasmaValue, oldPlasmaValue, plasmaMultiplicatorText):
        return self.flashObject.as_showPlasmaIndicator(plasmaValue, oldPlasmaValue, plasmaMultiplicatorText) if self._isDAAPIInited() else None

    def as_setPlasmaSavedS(self, plasmaValue):
        return self.flashObject.as_setPlasmaSaved(plasmaValue) if self._isDAAPIInited() else None

    def as_showExplosiveShotIndicatorS(self, isActive):
        return self.flashObject.as_showExplosiveShotIndicator(isActive) if self._isDAAPIInited() else None

    def as_showBarrierS(self, isVisible, bindKey):
        return self.flashObject.as_showBarrier(isVisible, bindKey) if self._isDAAPIInited() else None

    def as_showIncreaseDamageS(self, useAnim=True):
        return self.flashObject.as_showIncreaseDamage(useAnim) if self._isDAAPIInited() else None

    def as_hideIncreaseDamageS(self, useAnim=True):
        return self.flashObject.as_hideIncreaseDamage(useAnim) if self._isDAAPIInited() else None

    def as_updateIncreaseDamageS(self, progress, isFail=False, useAnim=True):
        return self.flashObject.as_updateIncreaseDamage(progress, isFail, useAnim) if self._isDAAPIInited() else None

    def as_showReloadBoostS(self, useAnim=False):
        return self.flashObject.as_showReloadBoost(useAnim) if self._isDAAPIInited() else None

    def as_hideReloadBoostS(self, useAnim=False):
        return self.flashObject.as_hideReloadBoost(useAnim) if self._isDAAPIInited() else None

    def as_updateReloadBoostS(self, progress, isFail=False, useAnim=False):
        return self.flashObject.as_updateReloadBoost(progress, isFail, useAnim) if self._isDAAPIInited() else None

    def as_showS(self, useAnim=False):
        return self.flashObject.as_show(useAnim) if self._isDAAPIInited() else None

    def as_hideS(self, useAnim=False):
        return self.flashObject.as_hide(useAnim) if self._isDAAPIInited() else None
