# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class HangarMeta(DAAPIModule):

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

    def as_setupAmmunitionPanelS(self, message, stateLevel, maintenanceEnabled, customizationEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_setupAmmunitionPanel(message, stateLevel, maintenanceEnabled, customizationEnabled)

    def as_setControlsVisibleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setControlsVisible(value)

    def as_showHelpLayoutS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_showHelpLayout()

    def as_closeHelpLayoutS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_closeHelpLayout()

    def as_setIsIGRS(self, value, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setIsIGR(value, text)

    def as_setServerStatsS(self, serverStats):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStats(serverStats)

    def as_setServerStatsInfoS(self, tooltipFullData):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStatsInfo(tooltipFullData)
