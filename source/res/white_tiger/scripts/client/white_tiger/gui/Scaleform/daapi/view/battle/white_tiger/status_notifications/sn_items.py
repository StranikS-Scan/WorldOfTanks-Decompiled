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
