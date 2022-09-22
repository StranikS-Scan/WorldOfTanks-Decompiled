# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/status_notifications/panel.py
import CommandMapping
from battle_royale.gui.Scaleform.daapi.view.battle.status_notifications.panel import StatusNotificationTimerPanel
from battle_royale.gui.Scaleform.daapi.view.battle.status_notifications import sn_items, components
from gui.Scaleform.daapi.view.battle.event.status_notifications import sn_items as event_sn_items
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_STATES
from gui.Scaleform.locale.EVENT import EVENT
from gui.shared.utils.key_mapping import getScaleformKey

class _EventHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_EventHighPriorityGroup, self).__init__((sn_items.DeathZoneDamagingSN,
         sn_items.DeathZoneDangerSN,
         sn_items.FireSN,
         event_sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN), updateCallback)


class EventStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        return [_EventHighPriorityGroup,
         event_sn_items.BombCaptureSN,
         event_sn_items.BombCarrySN,
         event_sn_items.BombDeploySN,
         event_sn_items.BombAbsorbSN,
         sn_items.StunSN,
         sn_items.DeathZoneWarningSN,
         sn_items.InspireSN,
         sn_items.LootPickUpSN,
         sn_items.BerserkerSN,
         sn_items.DamagingSmokeSN,
         sn_items.HealingSN,
         sn_items.HealingCooldownSN,
         sn_items.RepairingSN,
         sn_items.RepairingCooldownSN,
         sn_items.SmokeSN]

    def _generateNotificationTimerSettings(self):
        data = super(EventStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TIMER_STATES.STUN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WT_STUN_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, True, False, EVENT.STUN_INDICATOR, replace=True)
        self._addNotificationTimerSetting(data, _TIMER_STATES.OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HALF_OVERTURNED_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_DESTROY_TIMER_UI, noiseVisible=False, pulseVisible=False, iconOffsetY=-10)
        bwKey, _ = CommandMapping.g_instance.getCommandKeys(CommandMapping.CMD_BOMB_DROP)
        sfKey = getScaleformKey(bwKey)
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WT_TIMER_UI
        self._addNotificationTimerSetting(data, _TIMER_STATES.WT_BOMB_CARRY, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WT_BOMB_CARRY, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, True, False, iconOffsetY=11, tipKeyCode=sfKey)
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_TIMER_UI
        self._addNotificationTimerSetting(data, _TIMER_STATES.WT_BOMB_CAPTURE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WT_BOMB_CAPTURE, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.BLUE, True, False)
        self._addNotificationTimerSetting(data, _TIMER_STATES.WT_BOMB_DEPLOY, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WT_BOMB_DEPLOY, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.BLUE, True, False)
        self._addNotificationTimerSetting(data, _TIMER_STATES.WT_BOMB_ABSORB, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.WT_BOMB_ABSORB, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.BLUE, True, False)
        return data

    def _addNotificationTimerSetting(self, data, typeId, iconName, linkage, color='', noiseVisible=False, pulseVisible=False, text='', countdownVisible=True, iconOffsetY=0, replace=False, tipKeyCode=None):
        if replace:
            for item in data:
                if item['typeId'] == typeId:
                    data.remove(item)

        data.append({'typeId': typeId,
         'iconName': iconName,
         'linkage': linkage,
         'color': color,
         'noiseVisible': noiseVisible,
         'pulseVisible': pulseVisible,
         'text': text,
         'countdownVisible': countdownVisible,
         'iconOffsetY': iconOffsetY,
         'tipKeyCode': tipKeyCode})
