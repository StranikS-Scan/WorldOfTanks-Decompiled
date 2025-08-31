# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/status_notifications/sn_items.py
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R

class WhiteTigerOverturnedSN(sn_items.OverturnedSN):

    def _getDescription(self, value=None):
        return backport.text(R.strings.battle_royale.statusNotificationTimers.halfOverturned())


class WhiteTigerHyperionChargingSN(sn_items.DeathZoneDangerSN):

    def _getDescription(self, value=None):
        pass

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_HYPERION_WARNING_CHARGING

    def _canBeShown(self, value):
        return value.visible


class WhiteTigerHyperion2025ChargingSN(sn_items.DeathZoneDangerSN):

    def _getDescription(self, value=None):
        pass

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_HYPERION_2025_WARNING_CHARGING

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_HYPERION_2025_WARNING_CHARGING

    def _canBeShown(self, value):
        return value.visible


class WhiteTigerStunAreaSN(sn_items.TimerSN):

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.stunArea())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_STUN_AREA

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_STUN_AREA

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class StunAreaTimerViewState(object):
    __slots__ = ('visible', 'totalTime', 'finishTime')

    def __init__(self, visible, totalTime, finishTime):
        self.visible = visible
        self.totalTime = totalTime
        self.finishTime = finishTime
