# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RibbonsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RibbonsPanelMeta(BaseDAAPIComponent):

    def onShow(self):
        self._printOverrideError('onShow')

    def onChange(self):
        self._printOverrideError('onChange')

    def onHide(self, ribbonId):
        self._printOverrideError('onHide')

    def as_setupS(self, items, isExtendedAnim, isVisible, isWithRibbonName, isWithVehName, bonusLabels):
        return self.flashObject.as_setup(items, isExtendedAnim, isVisible, isWithRibbonName, isWithVehName, bonusLabels) if self._isDAAPIInited() else None

    def as_resetS(self):
        return self.flashObject.as_reset() if self._isDAAPIInited() else None

    def as_addBattleEfficiencyEventS(self, ribbonType, ribbonId, leftFieldStr, vehName, vehType, rightFieldStr, bonusLabelIndex, role):
        return self.flashObject.as_addBattleEfficiencyEvent(ribbonType, ribbonId, leftFieldStr, vehName, vehType, rightFieldStr, bonusLabelIndex, role) if self._isDAAPIInited() else None

    def as_updateBattleEfficiencyEventS(self, ribbonType, ribbonId, leftFieldStr, vehName, vehType, rightFieldStr, bonusLabelIndex, role):
        return self.flashObject.as_updateBattleEfficiencyEvent(ribbonType, ribbonId, leftFieldStr, vehName, vehType, rightFieldStr, bonusLabelIndex, role) if self._isDAAPIInited() else None

    def as_setSettingsS(self, isVisible, isExtendedAnim, isWithRibbonName, isWithVehName):
        return self.flashObject.as_setSettings(isVisible, isExtendedAnim, isWithRibbonName, isWithVehName) if self._isDAAPIInited() else None
