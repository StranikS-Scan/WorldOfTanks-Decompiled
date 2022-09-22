# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConsumablesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ConsumablesPanelMeta(BaseDAAPIComponent):

    def onClickedToSlot(self, keyCode, idx):
        self._printOverrideError('onClickedToSlot')

    def onPopUpClosed(self):
        self._printOverrideError('onPopUpClosed')

    def onPanelShown(self):
        self._printOverrideError('onPanelShown')

    def onPanelHidden(self):
        self._printOverrideError('onPanelHidden')

    def as_setKeysToSlotsS(self, slots):
        return self.flashObject.as_setKeysToSlots(slots) if self._isDAAPIInited() else None

    def as_setItemQuantityInSlotS(self, idx, quantity):
        return self.flashObject.as_setItemQuantityInSlot(idx, quantity) if self._isDAAPIInited() else None

    def as_setItemTimeQuantityInSlotS(self, idx, quantity, timeRemaining, maxTime, animation, stage):
        return self.flashObject.as_setItemTimeQuantityInSlot(idx, quantity, timeRemaining, maxTime, animation, stage) if self._isDAAPIInited() else None

    def as_setCoolDownTimeS(self, idx, duration, baseTime, startTime):
        return self.flashObject.as_setCoolDownTime(idx, duration, baseTime, startTime) if self._isDAAPIInited() else None

    def as_setCoolDownPosAsPercentS(self, idx, percent):
        return self.flashObject.as_setCoolDownPosAsPercent(idx, percent) if self._isDAAPIInited() else None

    def as_setCoolDownTimeSnapshotS(self, idx, time, isBaseTime, isFlash):
        return self.flashObject.as_setCoolDownTimeSnapshot(idx, time, isBaseTime, isFlash) if self._isDAAPIInited() else None

    def as_addShellSlotS(self, idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText):
        return self.flashObject.as_addShellSlot(idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText) if self._isDAAPIInited() else None

    def as_setNextShellS(self, idx):
        return self.flashObject.as_setNextShell(idx) if self._isDAAPIInited() else None

    def as_setCurrentShellS(self, idx):
        return self.flashObject.as_setCurrentShell(idx) if self._isDAAPIInited() else None

    def as_addEquipmentSlotS(self, idx, keyCode, sfKeyCode, tag, quantity, timeRemaining, reloadingTime, iconPath, tooltipText, animation, stage):
        return self.flashObject.as_addEquipmentSlot(idx, keyCode, sfKeyCode, tag, quantity, timeRemaining, reloadingTime, iconPath, tooltipText, animation, stage) if self._isDAAPIInited() else None

    def as_showEquipmentSlotsS(self, show):
        return self.flashObject.as_showEquipmentSlots(show) if self._isDAAPIInited() else None

    def as_expandEquipmentSlotS(self, idx, slots):
        return self.flashObject.as_expandEquipmentSlot(idx, slots) if self._isDAAPIInited() else None

    def as_collapseEquipmentSlotS(self):
        return self.flashObject.as_collapseEquipmentSlot() if self._isDAAPIInited() else None

    def as_updateLockedInformationS(self, idx, lockedID, tooltipStr):
        return self.flashObject.as_updateLockedInformation(idx, lockedID, tooltipStr) if self._isDAAPIInited() else None

    def as_updateLevelInformationS(self, idx, level):
        return self.flashObject.as_updateLevelInformation(idx, level) if self._isDAAPIInited() else None

    def as_addOptionalDeviceSlotS(self, idx, timeRemaining, iconPath, tooltipText, isTooltipSpecial, intCD, isUsed):
        return self.flashObject.as_addOptionalDeviceSlot(idx, timeRemaining, iconPath, tooltipText, isTooltipSpecial, intCD, isUsed) if self._isDAAPIInited() else None

    def as_setOptionalDeviceUsedS(self, idx, isUsed):
        return self.flashObject.as_setOptionalDeviceUsed(idx, isUsed) if self._isDAAPIInited() else None

    def as_setGlowS(self, idx, glowID):
        return self.flashObject.as_setGlow(idx, glowID) if self._isDAAPIInited() else None

    def as_hideGlowS(self, idx):
        return self.flashObject.as_hideGlow(idx) if self._isDAAPIInited() else None

    def as_setEquipmentActivatedS(self, idx, isActivated):
        return self.flashObject.as_setEquipmentActivated(idx, isActivated) if self._isDAAPIInited() else None

    def as_handleAsReplayS(self):
        return self.flashObject.as_handleAsReplay() if self._isDAAPIInited() else None

    def as_isVisibleS(self):
        return self.flashObject.as_isVisible() if self._isDAAPIInited() else None

    def as_resetS(self, slots=None):
        return self.flashObject.as_reset(slots) if self._isDAAPIInited() else None

    def as_updateEntityStateS(self, entityName, entityState):
        return self.flashObject.as_updateEntityState(entityName, entityState) if self._isDAAPIInited() else None

    def as_setPanelSettingsS(self, settingsId):
        return self.flashObject.as_setPanelSettings(settingsId) if self._isDAAPIInited() else None

    def as_setSPGShotResultS(self, shellIdx, shotResult):
        return self.flashObject.as_setSPGShotResult(shellIdx, shotResult) if self._isDAAPIInited() else None
