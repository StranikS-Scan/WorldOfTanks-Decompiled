# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConsumablesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ConsumablesPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onClickedToSlot(self, keyCode):
        self._printOverrideError('onClickedToSlot')

    def onPopUpClosed(self):
        self._printOverrideError('onPopUpClosed')

    def as_setKeysToSlotsS(self, slots):
        return self.flashObject.as_setKeysToSlots(slots) if self._isDAAPIInited() else None

    def as_setItemQuantityInSlotS(self, idx, quantity):
        return self.flashObject.as_setItemQuantityInSlot(idx, quantity) if self._isDAAPIInited() else None

    def as_setItemTimeQuantityInSlotS(self, idx, quantity, timeRemaining, maxTime):
        return self.flashObject.as_setItemTimeQuantityInSlot(idx, quantity, timeRemaining, maxTime) if self._isDAAPIInited() else None

    def as_setCoolDownTimeS(self, idx, duration, baseTime, startTime, isReloading):
        return self.flashObject.as_setCoolDownTime(idx, duration, baseTime, startTime, isReloading) if self._isDAAPIInited() else None

    def as_setCoolDownPosAsPercentS(self, idx, percent):
        return self.flashObject.as_setCoolDownPosAsPercent(idx, percent) if self._isDAAPIInited() else None

    def as_addShellSlotS(self, idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText):
        return self.flashObject.as_addShellSlot(idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText) if self._isDAAPIInited() else None

    def as_setNextShellS(self, idx):
        return self.flashObject.as_setNextShell(idx) if self._isDAAPIInited() else None

    def as_setCurrentShellS(self, idx):
        return self.flashObject.as_setCurrentShell(idx) if self._isDAAPIInited() else None

    def as_addEquipmentSlotS(self, idx, keyCode, sfKeyCode, tag, quantity, timeRemaining, iconPath, tooltipText):
        return self.flashObject.as_addEquipmentSlot(idx, keyCode, sfKeyCode, tag, quantity, timeRemaining, iconPath, tooltipText) if self._isDAAPIInited() else None

    def as_showEquipmentSlotsS(self, show):
        return self.flashObject.as_showEquipmentSlots(show) if self._isDAAPIInited() else None

    def as_expandEquipmentSlotS(self, idx, slots):
        return self.flashObject.as_expandEquipmentSlot(idx, slots) if self._isDAAPIInited() else None

    def as_collapseEquipmentSlotS(self):
        return self.flashObject.as_collapseEquipmentSlot() if self._isDAAPIInited() else None

    def as_addOptionalDeviceSlotS(self, idx, timeRemaining, iconPath, tooltipText):
        return self.flashObject.as_addOptionalDeviceSlot(idx, timeRemaining, iconPath, tooltipText) if self._isDAAPIInited() else None

    def as_addOrderSlotS(self, idx, keyCode, sfKeyCode, quantity, iconPath, tooltipText, available, quantityVisible, timeRemaining, maxTime):
        return self.flashObject.as_addOrderSlot(idx, keyCode, sfKeyCode, quantity, iconPath, tooltipText, available, quantityVisible, timeRemaining, maxTime) if self._isDAAPIInited() else None

    def as_setOrderAvailableS(self, idx, available):
        return self.flashObject.as_setOrderAvailable(idx, available) if self._isDAAPIInited() else None

    def as_setOrderActivatedS(self, idx):
        return self.flashObject.as_setOrderActivated(idx) if self._isDAAPIInited() else None

    def as_showOrdersSlotsS(self, show):
        return self.flashObject.as_showOrdersSlots(show) if self._isDAAPIInited() else None

    def as_isVisibleS(self):
        return self.flashObject.as_isVisible() if self._isDAAPIInited() else None

    def as_resetS(self):
        return self.flashObject.as_reset() if self._isDAAPIInited() else None

    def as_switchToPosmortemS(self):
        return self.flashObject.as_switchToPosmortem() if self._isDAAPIInited() else None

    def as_updateEntityStateS(self, entityName, entityState):
        return self.flashObject.as_updateEntityState(entityName, entityState) if self._isDAAPIInited() else None
