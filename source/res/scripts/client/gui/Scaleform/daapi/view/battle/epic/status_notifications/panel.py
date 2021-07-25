# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/status_notifications/panel.py
import logging
import BigWorld
from helpers import dependency
import BattleReplay
from ReplayEvents import g_replayEvents
from gui.Scaleform.daapi.view.battle.epic.status_notifications import components
from gui.Scaleform.daapi.view.battle.epic.status_notifications import replay_components
from gui.Scaleform.daapi.view.battle.epic.status_notifications import sn_items
from gui.Scaleform.daapi.view.meta.StatusNotificationsPanelMeta import StatusNotificationsPanelMeta
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.locale.BATTLE_ROYALE import BATTLE_ROYALE
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.shared.items_parameters import isAutoReloadGun
from gui.shared.utils.MethodsRules import MethodsRules
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class _EpicBattleHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_EpicBattleHighPriorityGroup, self).__init__((sn_items.DeathZoneDamagingSN,
         sn_items.DeathZoneDangerSN,
         sn_items.DeathZoneWarningSN,
         sn_items.SectorAirstrikeSN,
         sn_items.UnderFireSN,
         sn_items.FireSN,
         sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN), updateCallback)


class StatusNotificationTimerPanel(StatusNotificationsPanelMeta, MethodsRules):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE = 42

    def __init__(self):
        super(StatusNotificationTimerPanel, self).__init__()
        self.__container = None
        self.__viewID = None
        self.__vehicleID = None
        return

    def _populate(self):
        super(StatusNotificationTimerPanel, self)._populate()
        if self._sessionProvider.isReplayPlaying:
            containerClass = replay_components.ReplayStatusNotificationContainer
        else:
            containerClass = components.StatusNotificationContainer
        g_replayEvents.onPause += self.__onReplayPaused
        self.__container = containerClass([_EpicBattleHighPriorityGroup,
         sn_items.ResupplyTimerSN,
         sn_items.StunSN,
         sn_items.EnemySmokeSN,
         sn_items.SmokeSN,
         sn_items.StealthSN,
         sn_items.StealthInactiveSN,
         sn_items.InspireSN,
         sn_items.InspireCooldownSN,
         sn_items.InspireSourceSN,
         sn_items.InspireInactivationSourceSN,
         sn_items.HealingSN,
         sn_items.HealingCooldownSN,
         sn_items.RepairingSN,
         sn_items.RepairingCooldownSN,
         sn_items.RecoverySN,
         sn_items.CaptureBlockSN], self.__onCollectionUpdated)
        crosshairCtrl = self._sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        self.as_setInitDataS({'settings': self._generateNotificationTimerSettings()})
        return

    def _dispose(self):
        self.__container.destroy()
        self.__container = None
        if BattleReplay.isPlaying():
            self.__onCollectionUpdated([])
        g_replayEvents.onPause -= self.__onReplayPaused
        crosshairCtrl = self._sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        self.clear()
        super(StatusNotificationTimerPanel, self)._dispose()
        return

    def _generateNotificationTimerSettings(self):
        data = []
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.AIRSTRIKE_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.AIRSTRIKE_ICON, link, countdownVisible=False)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.OVERTURNED_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.OVERTURNED_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.UNDER_FIRE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.UNDER_FIRE_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.AIRSTRIKE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, countdownVisible=False)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ICON, link)
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.STUN_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, True, False, INGAME_GUI.STUN_INDICATOR)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.CAPTURE_BLOCK, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BLOCKED_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, EPIC_BATTLE.PROGRESS_TIMERS_BLOCKED)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.SMOKE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SMOKE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, EPIC_BATTLE.SMOKE_IN_SMOKE)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_SMOKE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.ENEMY_SMOKE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, EPIC_BATTLE.SMOKE_IN_SMOKE)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, True, EPIC_BATTLE.INSPIRE_INSPIRED)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, EPIC_BATTLE.INSPIRE_INSPIRED)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_SOURCE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_SOURCE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, True, EPIC_BATTLE.INSPIRE_INSPIRING)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_INACTIVATION_SOURCE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_SOURCE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, EPIC_BATTLE.INSPIRE_INSPIRING)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HEAL_ICON_FRONTLINE, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_HEALPOINT_HEALED)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HEAL_ICON_FRONTLINE, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_HEALPOINT_HEALED)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_REPAIRPOINT)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_REPAIRPOINT)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.STEALTH_RADAR, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.STEALTH_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, EPIC_BATTLE.STEALTHRADAR_ACTIVE)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.STEALTH_RADAR_INACTIVE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.STEALTH_INACTIVE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN_DISABLED, False, False, EPIC_BATTLE.STEALTHRADAR_INACTIVE)
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RESUPPLY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.RESUPPLY, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RESUPPLY_TIMER_UI, link)
        return data

    def _addNotificationTimerSetting(self, data, typeId, iconName, linkage, color='', noiseVisible=False, pulseVisible=False, text='', countdownVisible=True, iconOffsetY=0):
        data.append({'typeId': typeId,
         'iconName': iconName,
         'linkage': linkage,
         'color': color,
         'noiseVisible': noiseVisible,
         'pulseVisible': pulseVisible,
         'text': text,
         'countdownVisible': countdownVisible,
         'iconOffsetY': iconOffsetY})

    def __onReplayPaused(self, isPaused):
        self.as_setSpeedS(BattleReplay.g_replayCtrl.playbackSpeed)

    def __onCollectionUpdated(self, vOs):
        self.__logDataCollection(vOs)
        self.as_setDataS(vOs)
        gui_event_dispatcher.destroyTimersPanelShown(shown=len(vOs) > 0)

    @MethodsRules.delayable()
    def __onVehicleControlling(self, vehicle):
        self._sessionProvider.updateVehicleEffects()
        self.__vehicleID = vehicle.id
        self.__updatePanelPosition()

    @MethodsRules.delayable('__onVehicleControlling')
    def __onCrosshairViewChanged(self, viewID):
        self.__viewID = viewID
        self.__updatePanelPosition()

    def __updatePanelPosition(self):
        vehicle = BigWorld.entity(self.__vehicleID) if self.__vehicleID is not None else None
        if vehicle is None or vehicle.typeDescriptor is None:
            self.__setVerticalOffset(0)
            return
        else:
            verticalOffset = 0
            vTypeDescr = vehicle.typeDescriptor
            hasAutoloaderInterface = vTypeDescr.isDualgunVehicle or isAutoReloadGun(vTypeDescr.gun)
            if self.__viewID is CROSSHAIR_VIEW_ID.SNIPER and hasAutoloaderInterface:
                verticalOffset = self._VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE
            self.__setVerticalOffset(verticalOffset)
            return

    def __setVerticalOffset(self, verticalOffset):
        self.as_setVerticalOffsetS(verticalOffset)

    @classmethod
    def __logDataCollection(cls, vOs):
        lgr = _logger.debug
        lgr('Status Notifications data:')
        if not vOs:
            lgr('\n   []')
        else:
            for i, vO in enumerate(vOs):
                lgr('\n   %s: %r', i, vO)
