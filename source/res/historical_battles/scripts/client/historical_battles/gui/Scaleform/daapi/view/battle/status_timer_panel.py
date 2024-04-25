# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/status_timer_panel.py
import logging
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components, sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.daapi.view.battle.shared.status_notifications.sn_items import _DestroyTimerSN
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.HBBATTLE_NOTIFICATIONS_TIMER_LINKAGES import HBBATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DeathZoneTimerViewState, TIMER_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class _DeathZoneSN(_DestroyTimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DEATHZONE_TIMER

    def _getDescription(self, value):
        return backport.text(R.strings.hb_battle.timersPanel.deathZoneWarning())

    def _canBeShown(self, value):
        return self._getSupportedLevel() == value.level

    def _update(self, value):
        if self._canBeShown(value):
            self._isVisible = True
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._sendUpdate()
            return
        self._setVisible(False)


class HBDamagingZoneSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(HBDamagingZoneSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.hb_battle.timersPanel.deathZoneWarning())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DEATHZONE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_ZONE

    def _canBeShown(self, value):
        if super(HBDamagingZoneSN, self)._canBeShown(value):
            vehicle = self._sessionProvider.shared.vehicleState.getControllingVehicle()
            isAlive = vehicle is not None and vehicle.isAlive()
            return value.isCausingDamage and isAlive
        else:
            return False

    def _getSupportedLevel(self):
        return None


class HBStaticDeathZoneSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(HBStaticDeathZoneSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.hb_battle.timersPanel.deathZoneWarning())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DEATHZONE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(HBStaticDeathZoneSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        return TIMER_VIEW_STATE.WARNING


class HBPersonalDeathZoneSN(_DeathZoneSN):
    notifierDeltaTime = 2

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PERSONAL_DEATHZONE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE

    def _update(self, value):
        if self._canBeShown(value):
            self._isVisible = True
            self._updateTimeParams(value.totalTime, value.finishTime)
            if value.totalTime > self.notifierDeltaTime:
                self._setCallback(value.totalTime - self.notifierDeltaTime, self._sendUpdate)
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._sendUpdate()
            return
        self._stopCallback()
        self._setVisible(False)

    def getVO(self):
        vo = super(HBPersonalDeathZoneSN, self).getVO()
        vo['description'] = ''
        if vo['totalTime'] - vo['currentTime'] <= self.notifierDeltaTime:
            vo['description'] = backport.text(R.strings.hb_battle.timersPanel.deathZoneWarning())
        return vo

    def _canBeShown(self, value):
        return value.needToShow() if super(HBPersonalDeathZoneSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        return TIMER_VIEW_STATE.WARNING


class _HBHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_HBHighPriorityGroup, self).__init__((HBDamagingZoneSN,
         HBStaticDeathZoneSN,
         sn_items.FireSN,
         sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN), updateCallback)


class HBStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_HBHighPriorityGroup,
         sn_items.InspireSN,
         sn_items.InspireCooldownSN,
         HBPersonalDeathZoneSN,
         sn_items.StunSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = []
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.OVERTURNED_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HALF_OVERTURNED_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_DESTROY_TIMER_UI, noiseVisible=False, pulseVisible=False, iconOffsetY=-10)
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HB_SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.STUN_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, True, False, INGAME_GUI.STUN_INDICATOR)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, True, EPIC_BATTLE.STATUSNOTIFICATIONTIMERS_INSPIRE_INSPIRED)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, EPIC_BATTLE.STATUSNOTIFICATIONTIMERS_INSPIRE_INSPIRED)
        link = HBBATTLE_NOTIFICATIONS_TIMER_LINKAGES.HB_DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE, HBBATTLE_NOTIFICATIONS_TIMER_LINKAGES.AIR_STRIKE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, iconOffsetY=-4, descriptionFontSize=24, descriptionOffsetY=10)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.AIR_STRIKE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, countdownVisible=False, descriptionFontSize=24, descriptionOffsetY=10)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE, HBBATTLE_NOTIFICATIONS_TIMER_LINKAGES.AIR_STRIKE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, iconOffsetY=-4, descriptionFontSize=24, descriptionOffsetY=10)
        return data
