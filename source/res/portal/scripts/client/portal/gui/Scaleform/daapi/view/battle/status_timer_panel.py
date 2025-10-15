# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/status_timer_panel.py
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components, sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.daapi.view.battle.shared.status_notifications.sn_items import DeathZoneWarningSN, TimerSN, DestroyMiscTimerSN
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DeathZoneTimerViewState, TIMER_VIEW_STATE
from portal.gui.Scaleform.genConsts.PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES import PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES

class PortalPersonalDeathZoneSN(DeathZoneWarningSN):
    _EQUIPMENT_NAME = 'super_boss_aoe_portal'
    _DEFAULT_ZONE_ID = 1

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PERSONAL_DEATHZONE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE

    def _getDescription(self, value):
        return backport.text(R.strings.portal_battle.timers_panel.death_zone())

    def _update(self, value):
        value = self.__makeDeathZoneTimerViewState(value)
        return super(PortalPersonalDeathZoneSN, self)._update(value)

    def __makeDeathZoneTimerViewState(self, value):
        enable, time = value
        return DeathZoneTimerViewState(self._DEFAULT_ZONE_ID, False, max(time - BigWorld.serverTime(), 0), TIMER_VIEW_STATE.WARNING if enable else None, 0)


class PortalTeleportSN(TimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PORTAL_TELEPORT

    def getViewTypeID(self):
        return PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES.TELEPORT

    def _getDescription(self, value):
        return backport.text(R.strings.portal_battle.timers_panel.teleport())

    def _update(self, value):
        self._vo['iconName'] = self.__getIconNameByFrontier(value['frontier'])
        self._updateTimeParams(value['duration'], value['finishTime'])
        self._setVisible(value['isVisible'])

    def __getIconNameByFrontier(self, frontier):
        icons = {'Tsarev': _LINKS.PORTAL_TELEPORT_HORSE_ICON,
         'Yaginskaya': _LINKS.PORTAL_TELEPORT_HOOK_ICON,
         'Vasilieva': _LINKS.PORTAL_TELEPORT_SATELLITE_ICON,
         'Koshcheeva': _LINKS.PORTAL_TELEPORT_LOGO_ICON}
        return icons.get(frontier, self.NOT_CHANGE_DEFAULT_ICON)


class _PortalAuraZoneSN(DestroyMiscTimerSN):
    _DESCRIPTION_RESOURCE = None

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return self.getItemID()

    def _getDescription(self, value):
        return backport.text(self._DESCRIPTION_RESOURCE()) if self._DESCRIPTION_RESOURCE else ''


class PortalAnomalySN(_PortalAuraZoneSN):
    _DESCRIPTION_RESOURCE = R.strings.portal_battle.timers_panel.anomaly

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PORTAL_ANOMALY

    def getViewTypeID(self):
        return PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES.ANOMALY


class PortalRatteAuraSN(_PortalAuraZoneSN):
    _DESCRIPTION_RESOURCE = R.strings.portal_battle.timers_panel.ratte_aura

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PORTAL_RATTE_AURA

    def getViewTypeID(self):
        return PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES.RATTE_AURA


class _PortalHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_PortalHighPriorityGroup, self).__init__((sn_items.FireSN,
         sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN), updateCallback)


class PortalStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_PortalHighPriorityGroup,
         PortalPersonalDeathZoneSN,
         PortalAnomalySN,
         PortalRatteAuraSN,
         PortalTeleportSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = []
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED, _LINKS.OVERTURNED_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED, _LINKS.HALF_OVERTURNED_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, _LINKS.FIRE_ICON, link)
        link = _LINKS.STATUS_NOTIFICATION_TIMER
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE, _LINKS.PORTAL_DEATH_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.DARK_RED, iconOffsetY=-10, descriptionFontSize=24, descriptionOffsetY=10)
        self._addNotificationTimerSetting(data, PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES.ANOMALY, _LINKS.DANGER_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE)
        self._addNotificationTimerSetting(data, PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES.TELEPORT, _LINKS.PORTAL_TELEPORT_HOOK_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.BLUE, iconOffsetY=-4, descriptionFontSize=24, descriptionOffsetY=10)
        self._addNotificationTimerSetting(data, PORTAL_BATTLE_NOTIFICATIONS_TIMER_TYPES.RATTE_AURA, _LINKS.PORTAL_RATTE_AURA_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.DARK_RED, iconSmallName=_LINKS.PORTAL_RATTE_AURA_SMALL_ICON, iconOffsetY=-4, descriptionFontSize=24, descriptionOffsetY=10)
        return data
