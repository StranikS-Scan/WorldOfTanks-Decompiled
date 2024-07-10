# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/status_notifications/panel.py
import logging
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
_logger = logging.getLogger(__name__)

class _PveHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_PveHighPriorityGroup, self).__init__((sn_items.DrownSN,
         sn_items.FireSN,
         sn_items.StaticDeathZoneSN,
         sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN), updateCallback)


class PveStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_PveHighPriorityGroup, sn_items.StunSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(PveStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.STATUS_NOTIFICATION_TIMER
        self._addNotificationTimerSetting(data, _TYPES.SECTOR_AIRSTRIKE, _LINKS.AIRSTRIKE_ICON, link, iconSmallName='secondaryAirStrikeUI', color=_COLORS.YELLOW, descriptionFontSize=24, descriptionOffsetY=10)
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        player = BigWorld.player()
        liftOverEnabled = player.hasBonusCap(ARENA_BONUS_TYPE_CAPS.LIFT_OVER) if player else False
        if liftOverEnabled:
            overturnedIcon = _LINKS.OVERTURNED_GREEN_ICON
            overturnedColor = _COLORS.GREEN
            iconOffsetY = 1
        else:
            overturnedIcon = _LINKS.OVERTURNED_ICON
            overturnedColor = _COLORS.ORANGE
            iconOffsetY = 0
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link)
        return data
