# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WhiteTigerCrosshairPanelContainerMeta.py
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer

class WhiteTigerCrosshairPanelContainerMeta(CrosshairPanelContainer):

    def as_showPlasmaIndicatorS(self, plasmaValue, isPlasmaChanged, plasmaMultiplicatorText):
        return self.flashObject.as_showPlasmaIndicator(plasmaValue, isPlasmaChanged, plasmaMultiplicatorText) if self._isDAAPIInited() else None

    def as_showExplosiveShotIndicatorS(self, isActive):
        return self.flashObject.as_showExplosiveShotIndicator(isActive) if self._isDAAPIInited() else None
