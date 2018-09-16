# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarMeta.py
from gui.Scaleform.framework.entities.View import View

class HangarMeta(View):

    def onEscape(self):
        self._printOverrideError('onEscape')

    def showHelpLayout(self):
        self._printOverrideError('showHelpLayout')

    def closeHelpLayout(self):
        self._printOverrideError('closeHelpLayout')

    def as_setCrewEnabledS(self, value):
        return self.flashObject.as_setCrewEnabled(value) if self._isDAAPIInited() else None

    def as_setCarouselEnabledS(self, value):
        return self.flashObject.as_setCarouselEnabled(value) if self._isDAAPIInited() else None

    def as_setupAmmunitionPanelS(self, maintenanceEnabled, maintenanceTooltip, customizationEnabled, customizationTooltip):
        return self.flashObject.as_setupAmmunitionPanel(maintenanceEnabled, maintenanceTooltip, customizationEnabled, customizationTooltip) if self._isDAAPIInited() else None

    def as_setControlsVisibleS(self, value):
        return self.flashObject.as_setControlsVisible(value) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_showHelpLayoutS(self):
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None

    def as_show3DSceneTooltipS(self, id, args):
        return self.flashObject.as_show3DSceneTooltip(id, args) if self._isDAAPIInited() else None

    def as_hide3DSceneTooltipS(self):
        return self.flashObject.as_hide3DSceneTooltip() if self._isDAAPIInited() else None

    def as_setCarouselS(self, linkage, alias):
        return self.flashObject.as_setCarousel(linkage, alias) if self._isDAAPIInited() else None

    def as_setDefaultHeaderS(self, isDefault):
        return self.flashObject.as_setDefaultHeader(isDefault) if self._isDAAPIInited() else None

    def as_setAlertMessageBlockVisibleS(self, isVisible):
        return self.flashObject.as_setAlertMessageBlockVisible(isVisible) if self._isDAAPIInited() else None
