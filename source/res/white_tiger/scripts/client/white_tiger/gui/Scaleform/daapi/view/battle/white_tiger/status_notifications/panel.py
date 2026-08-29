# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/status_notifications/panel.py
import logging
from constants import IS_DEVELOPMENT
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications import sn_items as wt_sn_items
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_LINKAGES import WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _WT_LINKS
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES import WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES as _WT_TYPES
_logger = logging.getLogger(__name__)

class _WhiteTigerHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_WhiteTigerHighPriorityGroup, self).__init__((wt_sn_items.WhiteTigerHyperionChargingSN,
         wt_sn_items.WhiteTigerHyperion2025ChargingSN,
         wt_sn_items.WhiteTigerAnomalySN,
         sn_items.FireSN,
         sn_items.DrownSN,
         sn_items.HalfOverturnedSN,
         wt_sn_items.WhiteTigerOverturnedSN), updateCallback)


class _WhiteTigerNormalPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_WhiteTigerNormalPriorityGroup, self).__init__((wt_sn_items.WhiteTigerStunAreaSN,
         wt_sn_items.WhiteTigerSilenceSN,
         sn_items.StunSN,
         wt_sn_items.WhiteTigerExplosiveDamageShieldSN,
         wt_sn_items.WhiteTigerDomeSN,
         wt_sn_items.WTSmokeSN,
         wt_sn_items.WTSmokeEnemySN,
         wt_sn_items.WhiteTigerBossInvisibilitySN), updateCallback)


class WhiteTigerStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_WhiteTigerHighPriorityGroup, _WhiteTigerNormalPriorityGroup]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(WhiteTigerStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, _LINKS.OVERTURNED_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, _LINKS.HALF_OVERTURNED_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_HYPERION_WARNING_CHARGING, _WT_LINKS.WT_HYPERION_WARNING_ICON, link, _COLORS.ORANGE, countdownVisible=True)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_HYPERION_2025_WARNING_CHARGING, _WT_LINKS.WT_HYPERION_WARNING_2025_ICON, link, _COLORS.ORANGE, countdownVisible=True)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_ANOMALY, _WT_LINKS.WT_ANOMALY_ICON, link, _COLORS.RED, countdownVisible=False)
        link = _WT_LINKS.WT_COUNTER_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _WT_LINKS.WT_STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True, text=INGAME_GUI.STUN_INDICATOR)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_STUN_AREA, _WT_LINKS.WT_STUN_AREA_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_SILENCE, _LINKS.BLOCKED_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _TYPES.SMOKE, _LINKS.SMOKE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.DAMAGING_SMOKE, _WT_LINKS.WT_ENEMY_SMOKE_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_ENERGY_SHIELD, _WT_LINKS.WT_ENERGY_SHIELD_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_BOSS_INVISIBILITY, _WT_LINKS.WT_SCOUT_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _WT_TYPES.WT_STATIC_SHIELD, _WT_LINKS.WT_STATIC_SHIELD_ICON, link, _COLORS.GREEN)
        return data

    def _getComponentClass(self):
        return WhiteTigerStatusNotificationTimerContainer


class WhiteTigerStatusNotificationTimerContainer(components.StatusNotificationContainer):
    _MAX_HIGH_PRIORITY_CNT = 1
    _MAX_NORMAL_PRIORITY_CNT = 5
    _MAX_TOTAL_CNT = 5
    _MAX_CNT_FOR_PRIORITY_CONTAINER = (_MAX_HIGH_PRIORITY_CNT, _MAX_NORMAL_PRIORITY_CNT)

    def getItemsData(self):
        if IS_DEVELOPMENT:
            for i in range(len(self._MAX_CNT_FOR_PRIORITY_CONTAINER)):
                items = self._items[i].getVisibleItemsInGroup() if self._items[i] else []
                _logger.debug('WhiteTigerStatusNotificationTimerContainer::getItemsData all items %r, %r, %r', i, len(items), items)

        result = []
        for i in range(len(self._MAX_CNT_FOR_PRIORITY_CONTAINER)):
            if len(result) >= self._MAX_TOTAL_CNT:
                break
            result.extend(self._items[i].getVisibleItemsInGroup(maxReturnedCount=min(self._MAX_CNT_FOR_PRIORITY_CONTAINER[i], self._MAX_TOTAL_CNT - len(result))))

        return result
