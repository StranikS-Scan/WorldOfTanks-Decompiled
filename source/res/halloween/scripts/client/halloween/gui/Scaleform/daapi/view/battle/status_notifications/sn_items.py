# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/status_notifications/sn_items.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class HWVehicleFrozenArrowSN(sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HW_VEHICLE_FROZEN_ARROW

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HW_VEHICLE_FROZEN_ARROW

    def _getTitle(self, value):
        return backport.text(R.strings.hw_battle.statusNotificationTimers.frozenArrowDebuff())

    def _update(self, data):
        duration = data.get('duration', 0)
        if duration > 0.0:
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)


class HWVehicleHealingArrowSN(sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HW_VEHICLE_HEALING_ARROW

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HW_VEHICLE_HEALING_ARROW

    def _getTitle(self, value):
        return backport.text(R.strings.hw_battle.statusNotificationTimers.healingArrowDebuff())

    def _update(self, data):
        duration = data.get('duration', 0)
        if duration > 0.0:
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)


class HWVehicleLaughArrow(sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HW_VEHICLE_LAUGH_ARROW

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HW_VEHICLE_LAUGH_ARROW

    def _getTitle(self, value):
        return backport.text(R.strings.hw_battle.statusNotificationTimers.hwVehicleLaughArrowDebuff())

    def _update(self, data):
        duration = data.get('duration', 0)
        if duration > 0.0:
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)


class HWVehicleFrozenMantleSN(sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HW_VEHICLE_FROZEN_MANTLE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HW_VEHICLE_FROZEN_MANTLE

    def _getTitle(self, value):
        return backport.text(R.strings.hw_battle.statusNotificationTimers.frozenMantleDebuff())

    def _update(self, visible):
        self._setVisible(visible)
