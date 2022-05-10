# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.epic.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, GroupedViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
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
    from gui.Scaleform.daapi.view.battle.epic import consumables_panel
    from gui.Scaleform.daapi.view.common.filter_popover import BattleTankCarouselFilterPopover
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.epic import ingame_rank_panel
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject, respawn_ammunition_panel_inject
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    return (ViewSettings(VIEW_ALIAS.EPIC_BATTLE_PAGE, page.EpicBattlePage, 'epicBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.EpicBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL, battle_carousel.BattleTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, BattleTankCarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.TOP_WINDOW, BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, SETTINGS_WINDOW_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_REINFORCEMENT_PANEL, reinforcement_panel.EpicReinforcementPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_SCORE_PANEL, score_panel.EpicScorePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL, missions_panel.EpicMissionsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timer.EpicBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW, respawn.EpicBattleRespawn, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.EpicMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_DEPLOYMENT_MAP, deployment_map.EpicDeploymentMapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN, overviewmap_screen.OverviewMapScreen, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.EpicMessagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, StatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.EpicFullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.EpicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_SPECTATOR_VIEW, spectator_view.EpicSpectatorView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RECOVERY_PANEL, recovery_panel.RecoveryPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SUPER_PLATOON_PANEL, super_platoon_panel.SuperPlatoonPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.EpicBattleConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_INGAME_RANK, ingame_rank_panel.InGameRankPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EPIC_RESPAWN_AMMUNITION_PANEL, respawn_ammunition_panel_inject.EpicRespawnAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE))


class EpicBattlePageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        super(EpicBattlePageBusinessHandler, self).__init__(((BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),), APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.EPIC_BATTLE_PAGE), EpicBattlePageBusinessHandler())
