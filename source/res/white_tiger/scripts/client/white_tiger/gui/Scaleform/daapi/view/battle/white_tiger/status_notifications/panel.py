# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/status_notifications/panel.py
import logging
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications import sn_items as wt_sn_items
_logger = logging.getLogger(__name__)

class _WhiteTigerHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_WhiteTigerHighPriorityGroup, self).__init__((wt_sn_items.WhiteTigerHyperionChargingSN,
         sn_items.FireSN,
         sn_items.DrownSN,
         wt_sn_items.WhiteTigerOverturnedSN,
         sn_items.HalfOverturnedSN), updateCallback)


class WhiteTigerStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_WhiteTigerHighPriorityGroup, sn_items.StunSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(WhiteTigerStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, _LINKS.OVERTURNED_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, _LINKS.HALF_OVERTURNED_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.WT_HYPERION_WARNING_CHARGING, _LINKS.WT_HYPERION_WARNING_ICON, link, _COLORS.ORANGE, countdownVisible=True)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.WT_STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True, text=INGAME_GUI.STUN_INDICATOR)
        return data
