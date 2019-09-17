# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_consumables_panel.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class EventConsumablesPanel(ConsumablesPanel):

    def __init__(self):
        super(EventConsumablesPanel, self).__init__()
        self.__lastUpdateIndex = -1
        self.__lastCurrentTime = -1
        self.__lastMaxTime = -1
        self.__lastStage = -1
        self.__callbackId = None
        return

    def _removeAmmoSubscription(self):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunSettingsSet -= self._onGunSettingsSet
        return

    def _addAmmoSubscription(self):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunSettingsSet += self._onGunSettingsSet
        return

    def _updateConsumableDataOnUI(self, idx, quantity, currentTime, maxTime, stage):
        self.__lastUpdateIndex = idx
        self.__lastCurrentTime = currentTime
        self.__lastMaxTime = maxTime
        self.__lastStage = stage
        if self.__callbackId is None:
            self.__callbackId = BigWorld.callback(0.01, self.__updateUI)
        return

    def _addEquipmentSlot(self, intCD, idx, item):
        super(EventConsumablesPanel, self)._addEquipmentSlot(intCD, idx, item)
        self._updateConsumableDataOnUI(idx, 0, 0, item.getTotalTime(), item.getStage())

    def __updateUI(self):
        self.__callbackId = None
        self.as_updateFestivalConsumableS(self.__lastUpdateIndex, self.__lastCurrentTime, self.__lastMaxTime, self.__lastStage)
        return
