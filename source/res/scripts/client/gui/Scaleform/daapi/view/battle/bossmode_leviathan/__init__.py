# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/__init__.py
"""
Change contents for specific BossMode Battle.
By default, use Classic battle page
"""
from debug_utils import LOG_DEBUG_DEV
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.bossmode_leviathan.leviathan_briefing_banner import HalloweenBriefingBanner
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.classic import full_stats
    from gui.Scaleform.daapi.view.battle.classic import players_panel
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_loading
    from gui.Scaleform.daapi.view.battle.shared import consumables_panel
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import minimap
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import page
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import leviathan_progress_panel
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import leviathan_gate_capture_bar
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import evil_eye
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import pve_goal_panel
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import minion_death_panel
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import pve_win_lose_panel
    from gui.Scaleform.daapi.view.battle.bossmode_leviathan import boss_location_marker
    LOG_DEBUG_DEV('[BOSS_MODE_LEVIATHAN BATTLE PAGE] - Call BossMode_Leviathan getViewSettings')
    return (ViewSettings(VIEW_ALIAS.BOSS_MODE_BATTLE_PAGE, page.BossModeLeviathanBattlePage, 'bossModeBattlePage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PlayersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.BossModeLeviathanMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.DestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.ConsumablesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BRIEFING_BANNER, HalloweenBriefingBanner, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.LEVIATHAN_PROGRESS_BAR, leviathan_progress_panel.LeviathanProgressPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.LEVIATHAN_GATE_CAPTURE_BAR, leviathan_gate_capture_bar.LeviathanGateCaptureBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVIL_EYE, evil_eye.EvilEye, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PVE_GOAL_PANEL, pve_goal_panel.PvEGoalPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINION_GOAL_PANEL, minion_death_panel.MinionDeathPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PVE_WINLOSE_PANEL, pve_win_lose_panel.PvEWinLosePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PVE_BOSS_LOCATION_MARKER, boss_location_marker.BossLocationMarker, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.BOSS_MODE_BATTLE_PAGE),)


class _EventBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.BOSS_MODE_BATTLE_PAGE, self.loadViewBySharedEvent),)
        super(_EventBattlePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)
