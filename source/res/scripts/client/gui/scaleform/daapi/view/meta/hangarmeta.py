# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarMeta.py
from gui.Scaleform.framework.entities.View import View

class HangarMeta(View):

    def onEscape(self):
        self._printOverrideError('onEscape')

    def checkMoney(self):
        self._printOverrideError('checkMoney')

    def showHelpLayout(self):
        self._printOverrideError('showHelpLayout')

    def closeHelpLayout(self):
        self._printOverrideError('closeHelpLayout')

    def toggleGUIEditor(self):
        self._printOverrideError('toggleGUIEditor')

    def as_setCrewEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCrewEnabled(value)

    def as_setCarouselEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCarouselEnabled(value)

    def as_setupAmmunitionPanelS(self, maintenanceEnabled, maintenanceTooltip, customizationEnabled, customizationTooltip):
        if self._isDAAPIInited():
            return self.flashObject.as_setupAmmunitionPanel(maintenanceEnabled, maintenanceTooltip, customizationEnabled, customizationTooltip)

    def as_setControlsVisibleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setControlsVisible(value)

    def as_setVisibleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setVisible(value)

    def as_showHelpLayoutS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_showHelpLayout()

    def as_closeHelpLayoutS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_closeHelpLayout()

    def as_setIsIGRS(self, value, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setIsIGR(value, text)

    def as_setServerStatsS(self, stats, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStats(stats, tooltipType)

    def as_setServerStatsInfoS(self, tooltipFullData):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStatsInfo(tooltipFullData)

    def as_setVehicleIGRS(self, actionIgrDaysLeft):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleIGR(actionIgrDaysLeft)

    def as_showMiniClientInfoS(self, description, hyperlink):
        if self._isDAAPIInited():
            return self.flashObject.as_showMiniClientInfo(description, hyperlink)

    def as_show3DSceneTooltipS(self, id, args):
        if self._isDAAPIInited():
            return self.flashObject.as_show3DSceneTooltip(id, args)

    def as_hide3DSceneTooltipS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_hide3DSceneTooltip()
