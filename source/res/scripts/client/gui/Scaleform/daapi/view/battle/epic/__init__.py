# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates, GroupedViewSettings
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
SETTINGS_WINDOW_SCOPE = ScopeTemplates.SimpleScope(VIEW_ALIAS.SETTINGS_WINDOW, ScopeTemplates.DEFAULT_SCOPE)

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.shared import shop_cm_handlers
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((CONTEXT_MENU_HANDLER_TYPE.SHOP, shop_cm_handlers.ShopCMHandler), (BATTLE_CONTEXT_MENU_HANDLER_TYPE.EPIC_FULL_STATS, player_menu_handler.PlayerMenuHandler), (BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.epic import page
    from gui.Scaleform.daapi.view.battle.epic import score_panel
    from gui.Scaleform.daapi.view.battle.epic import battle_timer
    from gui.Scaleform.daapi.view.battle.epic import respawn
    from gui.Scaleform.daapi.view.battle.epic import minimap
    from gui.Scaleform.daapi.view.battle.epic import deployment_map
    from gui.Scaleform.daapi.view.battle.epic import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.epic import game_messages_panel
    from gui.Scaleform.daapi.view.battle.epic import full_stats
    from gui.Scaleform.daapi.view.battle.epic import overviewmap_screen
    from gui.Scaleform.daapi.view.battle.epic import stats_exchange
    from gui.Scaleform.daapi.view.battle.epic import missions_panel
    from gui.Scaleform.daapi.view.battle.epic import spectator_view
    from gui.Scaleform.daapi.view.battle.epic import reinforcement_panel
    from gui.Scaleform.daapi.view.battle.epic import battle_loading
    from gui.Scaleform.daapi.view.battle.epic import recovery_panel
    from gui.Scaleform.daapi.view.battle.epic import battle_carousel
    from gui.Scaleform.daapi.view.battle.epic import super_platoon_panel
    from gui.Scaleform.daapi.view.battle.shared import consumables_panel
    from gui.Scaleform.daapi.view.common.filter_popover import BattleTankCarouselFilterPopover
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.epic import ingame_rank_panel
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    return (ViewSettings(VIEW_ALIAS.EPIC_BATTLE_PAGE, page.EpicBattlePage, 'epicBattlePage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.EpicBattleLoading, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL, battle_carousel.BattleTankCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, BattleTankCarouselFilterPopover, 'filtersPopoverView.swf', ViewTypes.TOP_WINDOW, BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, SETTINGS_WINDOW_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_REINFORCEMENT_PANEL, reinforcement_panel.EpicReinforcementPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_SCORE_PANEL, score_panel.EpicScorePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL, missions_panel.EpicMissionsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timer.EpicBattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW, respawn.EpicBattleRespawn, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.EpicMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_DEPLOYMENT_MAP, deployment_map.EpicDeploymentMapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN, overviewmap_screen.OverviewMapScreen, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.EpicMessagePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.EpicDestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.EpicFullStatsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.EpicStatisticsDataController, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_SPECTATOR_VIEW, spectator_view.EpicSpectatorView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RECOVERY_PANEL, recovery_panel.RecoveryPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.SUPER_PLATOON_PANEL, super_platoon_panel.SuperPlatoonPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.ConsumablesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EPIC_INGAME_RANK, ingame_rank_panel.InGameRankPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


class EpicBattlePageBusinessHandler(BattlePageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = [(VIEW_ALIAS.EPIC_BATTLE_PAGE, self._loadPage), (BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent)]
        super(BattlePageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)


def getBusinessHandlers():
    return (EpicBattlePageBusinessHandler(),)
