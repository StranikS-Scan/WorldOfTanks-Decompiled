# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/status_notifications/panel.py
from __future__ import absolute_import
import logging
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from halloween.gui.scaleform.genConsts.HW_BATTLE_NOTIFICATIONS_TIMER_TYPES import HW_BATTLE_NOTIFICATIONS_TIMER_TYPES as _HWTYPES
from halloween.gui.scaleform.genConsts.HW_NOTIFICATION_TIMER_ALIASES import HW_NOTIFICATION_TIMER_ALIASES as _HWLINKS
from halloween.gui.scaleform.genConsts.HW_NOTIFICATIONS_TIMER_COLORS import HW_NOTIFICATIONS_TIMER_COLORS as _HWCOLORS
from halloween.gui.scaleform.daapi.view.battle.status_notifications import sn_items as _HW_SW_ITEMS
_logger = logging.getLogger(__name__)

class _HalloweenHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_HalloweenHighPriorityGroup, self).__init__((_HW_SW_ITEMS.HWStaticDeathZoneSN,
         sn_items.FireSN,
         _HW_SW_ITEMS.HWDrainedSoulsSN,
         _HW_SW_ITEMS.HWDrainedLifeSN,
         sn_items.DrownSN), updateCallback)


class HWStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_HalloweenHighPriorityGroup,
         _HW_SW_ITEMS.HWPersonalDeathZoneSN,
         _HW_SW_ITEMS.HWPersonalDeathZoneIgniteSN,
         _HW_SW_ITEMS.HWPersonalDeathZoneStunSN,
         _HW_SW_ITEMS.HWPersonalDeathZoneIntervalSN,
         _HW_SW_ITEMS.FullCollectorSN,
         _HW_SW_ITEMS.PhaseFinishSN,
         _HW_SW_ITEMS.HWLootPickUpSN,
         _HW_SW_ITEMS.HWHalfOverturnedSN,
         sn_items.StunSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(HWStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _HWTYPES.HW_DEATH_ZONE, _HWLINKS.HW_DEATH_ZONE, link, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _HWTYPES.HW_DRAIN_SOULS, _LINKS.EVENTWARNING_ICON, link, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _HWTYPES.HW_DRAIN_LIFE, _LINKS.FIRE_ICON, link, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True)
        self._addNotificationTimerSetting(data, _HWTYPES.MAGNUS_WAIT, _HWLINKS.ICON_VOLOT_READY, _HWLINKS.WAIT_TIMER_UI, iconSmallName=_HWLINKS.ICON_VOLOT_READY_SMALL, color=_HWCOLORS.VIOLET)
        self._addNotificationTimerSetting(data, _HWTYPES.MAGNUS_GOTO, _HWLINKS.ICON_VOLOT_GOTO, _HWLINKS.GOTO_TIMER_UI, iconSmallName=_HWLINKS.ICON_VOLOT_GOTO_SMALL, color=_HWCOLORS.ORANGE, iconOffsetY=-4, descriptionOffsetY=-1)
        link = _LINKS.STATUS_NOTIFICATION_TIMER
        self._addNotificationTimerSetting(data, _HWTYPES.HW_PERSONAL_DEATH_ZONE, _HWLINKS.HW_PERSONAL_DEATH_ZONE, link, iconOffsetY=-8, iconSmallName=_HWLINKS.HW_PERSONAL_DEATH_ZONE_SMALL, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _HWTYPES.HW_PERSONAL_DEATH_ZONE_IGNITE, _HWLINKS.HW_PERSONAL_DEATH_ZONE_IGNITE, link, iconOffsetY=-8, iconSmallName=_HWLINKS.HW_PERSONAL_DEATH_ZONE_IGNITE_SMALL, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _HWTYPES.HW_PERSONAL_DEATH_ZONE_STUN, _HWLINKS.HW_PERSONAL_DEATH_ZONE_STUN, link, iconOffsetY=-8, iconSmallName=_HWLINKS.HW_PERSONAL_DEATH_ZONE_STUN_SMALL, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _HWTYPES.HW_PERSONAL_DEATH_ZONE_DAMAGE_OVERTIME, _HWLINKS.HW_PERSONAL_DEATH_ZONE_DAMAGE_OVERTIME, link, iconOffsetY=-8, iconSmallName=_HWLINKS.HW_PERSONAL_DEATH_ZONE_DAMAGE_OVERTIME_SMALL, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, _LINKS.HALF_OVERTURNED_ICON, link, iconOffsetY=-8, iconSmallName=_HWLINKS.HW_HALF_OVERTURN_SMALL, color=_COLORS.GREEN, descriptionFontSize=16, descriptionOffsetY=-2)
        link = _HWLINKS.HW_DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.LOOT_PICKUP, _HWLINKS.HW_LOOT_ICON_CONTENT, link, _COLORS.ORANGE_WARNING, noiseVisible=False)
        return data
