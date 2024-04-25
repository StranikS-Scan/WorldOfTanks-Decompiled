# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/status_notifications/panel.py
import logging
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import IS_CHINA
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from battle_royale.gui.Scaleform.daapi.view.battle.status_notifications import sn_items as br_sn_items
_logger = logging.getLogger(__name__)

class _BattleRoyaleHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_BattleRoyaleHighPriorityGroup, self).__init__((sn_items.OverturnedSN,
         br_sn_items.BRHalfOverturnedSN,
         sn_items.DrownSN,
         br_sn_items.BRDeathZoneDamagingSN,
         br_sn_items.BRDeathZoneDangerSN,
         sn_items.FireSN), updateCallback)


class BRStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_BattleRoyaleHighPriorityGroup,
         sn_items.StunSN,
         sn_items.StunFlameSN,
         br_sn_items.BRDeathZoneWarningSN,
         br_sn_items.BerserkerSN,
         br_sn_items.ShotPassionSN,
         br_sn_items.BRInspireSN,
         br_sn_items.LootPickUpSN,
         br_sn_items.ThunderStrikeSN,
         br_sn_items.FireCircleSN,
         br_sn_items.BRDamagingSmokeSN,
         br_sn_items.DamagingCorrodingShotSN,
         br_sn_items.AdaptationHealthRestoreSN,
         br_sn_items.BRHealingSN,
         br_sn_items.BRHealingCooldownSN,
         br_sn_items.BRRepairingSN,
         br_sn_items.BRRepairingCooldownSN,
         br_sn_items.BRSmokeSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(BRStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        if IS_CHINA:
            deathZoneIcon = _LINKS.DEATHZONE_ICON_CN
            damaginDeathZoneIcon = _LINKS.DAMAGING_DEATHZONE_ICON_CN
        else:
            deathZoneIcon = _LINKS.DEATHZONE_ICON
            damaginDeathZoneIcon = _LINKS.DAMAGING_DEATHZONE_ICON
        self._addNotificationTimerSetting(data, _TYPES.DEATH_ZONE, deathZoneIcon, link, _COLORS.RED)
        self._addNotificationTimerSetting(data, _TYPES.DAMAGING_ZONE, damaginDeathZoneIcon, _LINKS.BATTLE_ROYALE_TIMER_UI, _COLORS.RED, countdownVisible=False)
        liftOverEnabled = ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arenaBonusType, ARENA_BONUS_TYPE_CAPS.LIFT_OVER)
        if liftOverEnabled:
            overturnedIcon = _LINKS.OVERTURNED_GREEN_ICON
            overturnedColor = _COLORS.GREEN
            iconOffsetY = 1
        else:
            overturnedIcon = _LINKS.OVERTURNED_ICON
            overturnedColor = _COLORS.ORANGE
            iconOffsetY = 0
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, overturnedIcon, link, noiseVisible=False, iconOffsetY=iconOffsetY, color=overturnedColor)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.ORANGE_ZONE, _LINKS.DESTROY_TIMER_DANGER_ZONE, _LINKS.STATUS_NOTIFICATION_TIMER, _COLORS.YELLOW, iconOffsetY=-11, iconSmallName=_LINKS.DESTROY_TIMER_DANGER_ZONE_SMALL)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True)
        self._addNotificationTimerSetting(data, _TYPES.STUN_FLAME, _LINKS.STUN_FLAME_ICON, link, _COLORS.ORANGE, noiseVisible=True)
        self._addNotificationTimerSetting(data, _TYPES.CAPTURE_BLOCK, _LINKS.BLOCKED_ICON, link, _COLORS.ORANGE, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.SMOKE, _LINKS.SMOKE_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.DAMAGING_SMOKE, _LINKS.DAMAGING_SMOKE_ICON, link, _COLORS.RED, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.CORRODING_SHOT, _LINKS.CORRODING_SHOT_ICON, link, _COLORS.RED, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.FIRE_CIRCLE, _LINKS.FIRE_CIRCLE_ICON, link, _COLORS.RED, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.THUNDER_STRIKE, _LINKS.THUNDER_STRIKE_ICON, link, _COLORS.ORANGE, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.INSPIRE, _LINKS.INSPIRE_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.INSPIRE_CD, _LINKS.INSPIRE_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.HEALING, _LINKS.HEAL_POINT_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.HEALING_CD, _LINKS.HEAL_POINT_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.BERSERKER, _LINKS.BERSERKER_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.REPAIRING, _LINKS.RECOVERY_ZONE_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.REPAIRING_CD, _LINKS.RECOVERY_ZONE_ICON, link, _COLORS.GREEN, noiseVisible=False)
        link = _LINKS.BATTLE_ROYALE_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.LOOT_PICKUP, _LINKS.RECOVERY_ICON_CONTENT, link, _COLORS.GREEN, noiseVisible=False)
        link = _LINKS.BATTLE_ROYALE_COUNTER_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.SHOT_PASSION, _LINKS.SHOT_PASSION_ICON, link, _COLORS.GREEN, noiseVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.HP_RESTORE_ON_DAMAGE, _LINKS.HP_RESTORE_ON_DAMAGE_ICON, link, _COLORS.GREEN, noiseVisible=False)
        return data
