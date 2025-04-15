# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from frontline.gui.Scaleform.genConsts.FRONTLINE_BATTLE_VIEW_ALIASES import FRONTLINE_BATTLE_VIEW_ALIASES
from frontline.gui.gui_constants import ViewAlias
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ComponentSettings, getSwfExtensionUrl, ViewSettings, GroupedViewSettings
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
SETTINGS_WINDOW_SCOPE = ScopeTemplates.SimpleScope(VIEW_ALIAS.SETTINGS_WINDOW, ScopeTemplates.DEFAULT_SCOPE)

def getFLSwfExtensionUrl(swfName):
    return getSwfExtensionUrl('frontline', swfName)


def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.shared import shop_cm_handlers
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((CONTEXT_MENU_HANDLER_TYPE.SHOP, shop_cm_handlers.ShopCMHandler), (BATTLE_CONTEXT_MENU_HANDLER_TYPE.EPIC_FULL_STATS, player_menu_handler.PlayerMenuHandler), (BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler))


def getViewSettings():
    from frontline.gui.Scaleform.daapi.view.battle.frontline_pre_battle_timer import FrontlinePreBattleTimer
    from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_page import FrontlineBattlePage
    from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_upgrade_panel import FrontlineBattleUpgradePanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_modification_panel import FrontlineBattleModificationPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_carousel import BattleTankCarousel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_filter_popover import FrontlineBattleTankCarouselFilterPopover
    from frontline.gui.Scaleform.daapi.view.battle.frontline_respawn_view import FrontlineRespawnView
    from frontline.gui.Scaleform.daapi.view.battle.frontline_reinforcement_panel import FrontlineReinforcementPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_score_panel import FrontlineScorePanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_missions_panel import FrontlineMissionsPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_timer import FrontlineBattleTimer
    from frontline.gui.Scaleform.daapi.view.battle.frontline_minimap import FrontlineMinimapComponent
    from frontline.gui.Scaleform.daapi.view.battle.frontline_damage_pannel import FrontlineDamagePanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_deployment_map import FrontlineDeploymentMapComponent
    from frontline.gui.Scaleform.daapi.view.battle.frontline_overviewmap_screen import OverviewMapScreen
    from frontline.gui.Scaleform.daapi.view.battle.frontline_game_messages_panel import FrontlineMessagePanel
    from frontline.gui.Scaleform.daapi.view.battle.status_notifications.panel import FrontlineStatusNotificationTimerPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_full_stats import FrontlineFullStatsComponent
    from frontline.gui.Scaleform.daapi.view.battle.frontline_stats_exchange import FrontlineStatisticsDataController
    from frontline.gui.Scaleform.daapi.view.battle.frontline_recovery_panel import FrontlineRecoveryPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_platoon_panel import FrontlinePlatoonPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_ingame_rank_panel import FrontlineInGameRankPanel
    from frontline.gui.Scaleform.daapi.view.battle.frontline_consumables_panel import FrontlineBattleConsumablesPanel
    from frontline.gui.impl.battle.battle_page.respawn_ammunition_panel_inject import FrontlineRespawnAmmunitionPanelInject
    from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_loading import FrontlineEpicBattleLoading
    from gui.Scaleform.daapi.view.battle.classic.team_bases_panel import TeamBasesPanel
    from gui.Scaleform.daapi.view.battle.shared.situation_indicators import SituationIndicators
    from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel.component import BattleHintPanel
    from gui.Scaleform.daapi.view.battle.shared.messages import PlayerMessages
    from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_inject import PrebattleAmmunitionPanelInject
    from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel
    return (ViewSettings(ViewAlias.EPIC_BATTLE_PAGE, FrontlineBattlePage, getFLSwfExtensionUrl('frontlineBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, FrontlineEpicBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_BATTLE_TANK_CAROUSEL, BattleTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_CAROUSEL_FILTER_POPOVER, FrontlineBattleTankCarouselFilterPopover, getFLSwfExtensionUrl('frontlineCarouselFilterPopover.swf'), WindowLayer.TOP_WINDOW, FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_CAROUSEL_FILTER_POPOVER, FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_CAROUSEL_FILTER_POPOVER, SETTINGS_WINDOW_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL, FrontlineReinforcementPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_SCORE_PANEL, FrontlineScorePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MISSIONS_PANEL, FrontlineMissionsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SITUATION_INDICATORS, SituationIndicators, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, FrontlineBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_VIEW, FrontlineRespawnView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, FrontlineMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, FrontlineDamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_DEPLOYMENT_MAP, FrontlineDeploymentMapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN, OverviewMapScreen, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, FrontlineMessagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, FrontlineStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, FrontlineFullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, FrontlineStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RECOVERY_PANEL, FrontlineRecoveryPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL, FrontlinePlatoonPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_INGAME_RANK, FrontlineInGameRankPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_AMMUNITION_PANEL, FrontlineRespawnAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_UPGRADE_PANEL, FrontlineBattleUpgradePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MODIFICATION_PANEL, FrontlineBattleModificationPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, FrontlinePreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, FrontlineBattleConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE))


class FrontlineBattlePageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        super(FrontlineBattlePageBusinessHandler, self).__init__(((FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),), APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)


def getBusinessHandlers():
    return (BattlePageBusinessHandler(ViewAlias.EPIC_BATTLE_PAGE), FrontlineBattlePageBusinessHandler())
