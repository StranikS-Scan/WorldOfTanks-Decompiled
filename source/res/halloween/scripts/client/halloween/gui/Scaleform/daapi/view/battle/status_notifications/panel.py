# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/status_notifications/panel.py
import logging
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from halloween.gui.Scaleform.daapi.view.battle.status_notifications import sn_items as hw_sn_items
_logger = logging.getLogger(__name__)

class _HalloweenHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_HalloweenHighPriorityGroup, self).__init__((sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN,
         sn_items.UnderFireSN,
         sn_items.FireSN), updateCallback)


class HWStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_HalloweenHighPriorityGroup,
         sn_items.StunSN,
         sn_items.StunFlameSN,
         hw_sn_items.HWVehicleFrozenArrowSN,
         hw_sn_items.HWVehicleHealingArrowSN,
         hw_sn_items.HWVehicleLaughArrow,
         hw_sn_items.HWVehicleFrozenMantleSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(HWStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        liftOverEnabled = ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arenaBonusType, ARENA_BONUS_TYPE_CAPS.LIFT_OVER)
        if liftOverEnabled:
            overturnedIcon = _LINKS.OVERTURNED_GREEN_ICON
            overturnedColor = _COLORS.GREEN
            iconOffsetY = 1
        else:
            overturnedIcon = _LINKS.OVERTURNED_ICON
            overturnedColor = _COLORS.ORANGE
            iconOffsetY = 0
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, overturnedIcon, link, overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, overturnedIcon, link, overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.UNDER_FIRE, _LINKS.UNDER_FIRE_ICON, link)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.HW_VEHICLE_FROZEN_ARROW, _LINKS.HW_VEHICLE_FROZEN_ARROW_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _TYPES.HW_VEHICLE_HEALING_ARROW, _LINKS.HW_VEHICLE_HEALING_ARROW_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _TYPES.HW_VEHICLE_LAUGH_ARROW, _LINKS.HW_VEHICLE_LAUGH_ARROW_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _TYPES.HW_VEHICLE_FROZEN_MANTLE, _LINKS.HW_VEHICLE_FROZEN_MANTLE_ICON, link, _COLORS.BLUE, countdownVisible=False, descriptionOffsetY=10)
        return data
