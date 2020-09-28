# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/status_notifications/panel.py
import logging
import BattleReplay
import BigWorld
from helpers import dependency
from ReplayEvents import g_replayEvents
from gui.Scaleform.daapi.view.battle.battle_royale.status_notifications import components
from gui.Scaleform.daapi.view.battle.battle_royale.status_notifications import replay_components
from gui.Scaleform.daapi.view.battle.event.status_notifications.sn_items import EventStunSN, EventLootPickUpSN
from gui.Scaleform.daapi.view.battle.battle_royale.status_notifications import sn_items as br_sn_items
from gui.Scaleform.daapi.view.meta.StatusNotificationsPanelMeta import StatusNotificationsPanelMeta
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.shared.items_parameters import isAutoReloadGun
from gui.shared.utils.MethodsRules import MethodsRules
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class _HighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_HighPriorityGroup, self).__init__((br_sn_items.FireSN,
         br_sn_items.OverturnedSN,
         br_sn_items.HalfOverturnedSN,
         br_sn_items.DrownSN), updateCallback)


class EventStatusNotificationsPanel(StatusNotificationsPanelMeta, MethodsRules):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE = 42

    def __init__(self):
        super(EventStatusNotificationsPanel, self).__init__()
        self.__container = None
        self.__viewID = None
        self.__vehicleID = None
        return

    def _populate(self):
        super(EventStatusNotificationsPanel, self)._populate()
        if self._sessionProvider.isReplayPlaying:
            containerClass = replay_components.ReplayStatusNotificationContainer
        else:
            containerClass = components.StatusNotificationContainer
        g_replayEvents.onPause += self.__onReplayPaused
        self.__container = containerClass([_HighPriorityGroup,
         EventStunSN,
         EventLootPickUpSN,
         br_sn_items.BerserkerSN,
         br_sn_items.HealingSN,
         br_sn_items.HealingCooldownSN,
         br_sn_items.RepairingSN,
         br_sn_items.RepairingCooldownSN], self.__onCollectionUpdated)
        crosshairCtrl = self._sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        self.as_setInitDataS({'settings': self._generateNotificationTimerSettings()})
        return

    def _dispose(self):
        self.__container.destroy()
        self.__container = None
        self.clear(reset=True)
        g_replayEvents.onPause -= self.__onReplayPaused
        crosshairCtrl = self._sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        super(EventStatusNotificationsPanel, self)._dispose()
        return

    def _generateNotificationTimerSettings(self):
        data = []
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.OVERTURNED_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HALF_OVERTURNED_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_DESTROY_TIMER_UI, noiseVisible=False, pulseVisible=False, iconOffsetY=-10)
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.EVENT_STUN_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, True, False, backport.text(R.strings.wt_event.event_stun.indicator()))
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.CAPTURE_BLOCK, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BLOCKED_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, backport.text(R.strings.epic_battle.progress_timers.blocked()))
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HEAL_POINT_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, True, backport.text(R.strings.battle_royale.equipment.healPoint.healed()))
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HEAL_POINT_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, backport.text(R.strings.battle_royale.equipment.healPoint.healed()))
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, backport.text(R.strings.battle_royale.equipment.repairPoint()))
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, backport.text(R.strings.battle_royale.equipment.repairPoint()))
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_TIMER_UI
        self._addNotificationTimerSetting(data, BATTLE_NOTIFICATIONS_TIMER_TYPES.LOOT_PICKUP, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ICON_CONTENT, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.BLUE, False, False)
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
