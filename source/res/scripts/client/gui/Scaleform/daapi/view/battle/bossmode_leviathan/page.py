# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/page.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from debug_utils import LOG_DEBUG_DEV
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
import BigWorld
from PlayerEvents import g_playerEvents
from gui.battle_control import event_dispatcher as gui_event_dispatcher
_VEHICLE_MARKER_DISTANCE_UPDATE_INTERVAL = 0.1
_VIEWS_TO_HIDE_ON_ARENA_END = {BATTLE_VIEW_ALIASES.FULL_STATS,
 BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
 BATTLE_VIEW_ALIASES.MINIMAP,
 BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
 BATTLE_VIEW_ALIASES.RIBBONS_PANEL,
 BATTLE_VIEW_ALIASES.BRIEFING_BANNER,
 BATTLE_VIEW_ALIASES.LEVIATHAN_PROGRESS_BAR,
 BATTLE_VIEW_ALIASES.LEVIATHAN_GATE_CAPTURE_BAR,
 BATTLE_VIEW_ALIASES.EVIL_EYE,
 BATTLE_VIEW_ALIASES.PVE_GOAL_PANEL,
 BATTLE_VIEW_ALIASES.MINION_GOAL_PANEL,
 BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
 BATTLE_VIEW_ALIASES.TICKER,
 BATTLE_VIEW_ALIASES.SIXTH_SENSE,
 BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL,
 BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES,
 BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
 BATTLE_VIEW_ALIASES.FULL_STATS,
 BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL,
 BATTLE_VIEW_ALIASES.MULTI_TURRET_HINT_PANEL,
 BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL,
 BATTLE_VIEW_ALIASES.PVE_BOSS_LOCATION_MARKER,
 BATTLE_VIEW_ALIASES.BATTLE_MESSENGER}
_LEVIATHAN_COMPONENTS_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BRIEFING_BANNER,)),))

class BossModeLeviathanBattlePage(ClassicPage, Notifiable):

    def __init__(self):
        super(BossModeLeviathanBattlePage, self).__init__()
        self.__leviathanID = 0

    def _populate(self):
        super(BossModeLeviathanBattlePage, self)._populate()
        self.addNotificators(PeriodicNotifier(lambda : _VEHICLE_MARKER_DISTANCE_UPDATE_INTERVAL, self.__onUpdateDistancesTick))
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        LOG_DEBUG_DEV('BossMode_Leviathan battle page is created.')

    def _dispose(self):
        super(BossModeLeviathanBattlePage, self)._dispose()
        self.clearNotification()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        LOG_DEBUG_DEV('BossMode_Leviathan battle page is destroyed.')

    def _getDefaultComponentsConfig(self):
        defaultConfig = super(BossModeLeviathanBattlePage, self)._getDefaultComponentsConfig()
        return defaultConfig + _LEVIATHAN_COMPONENTS_CONFIG

    def _onBattleLoadingFinish(self):
        super(BossModeLeviathanBattlePage, self)._onBattleLoadingFinish()
        self.__leviathanID = 0
        self.startNotification()

    def __onUpdateDistancesTick(self):
        ctrl = self.sessionProvider.shared.feedback
        arenaDP = self.sessionProvider.getArenaDP()
        if self.__leviathanID == 0:
            for vInfo in arenaDP.getVehiclesInfoIterator():
                vTypeInfoVO = vInfo.vehicleType
                if vTypeInfoVO.isLeviathan:
                    self.__leviathanID = vInfo.vehicleID

        if ctrl is not None and self.__leviathanID is not 0:
            ctrl.onVehicleMarkerUpdateDistance(self.__leviathanID)
        return

    def __onRoundFinished(self, winnerTeam, reason):
        gui_event_dispatcher.toggleCrosshairVisibility()
        self._setComponentsVisibility(hidden=_VIEWS_TO_HIDE_ON_ARENA_END)
        self.as_setPostmortemTipsVisibleS(False)
