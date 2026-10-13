# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, getSwfExtensionUrl
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from portal.gui.portal_gui_constants import VIEW_ALIAS
from portal.gui.Scaleform.daapi.view.battle.page import PortalBattlePage
from portal.gui.Scaleform.genConsts.PORTAL_BATTLE_VIEW_ALIASES import PORTAL_BATTLE_VIEW_ALIASES
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
__all__ = ('PortalBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import map_info_tip
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    from gui.Scaleform.daapi.view.battle.shared import perks_panel
    from portal.gui.Scaleform.daapi.view.battle.battle_loading import PortalBattleLoading
    from portal.gui.Scaleform.daapi.view.battle.consumables_panel import PortalConsumablesPanel
    from portal.gui.Scaleform.daapi.view.battle.ribbons_panel import PortalRibbonsPanel
    from portal.gui.Scaleform.daapi.view.battle.shared.messages.player_messages import PortalPlayerMessages
    from portal.gui.Scaleform.daapi.view.battle import portal_hud_widget
    from portal.gui.Scaleform.daapi.view.battle import portal_players_data_panel
    from portal.gui.Scaleform.daapi.view.battle import portal_enemies_data_panel
    from portal.gui.Scaleform.daapi.view.battle.portal_minimap import PortalMinimapComponent
    from portal.gui.Scaleform.daapi.view.battle.portal_full_stats import PortalFullStatsComponent
    from portal.gui.Scaleform.daapi.view.battle.portal_camp_capture_progress_bar import PortalCampCamptureProgressBar
    from portal.gui.Scaleform.daapi.view.battle import portal_game_messages_panel
    from portal.gui.Scaleform.daapi.view.battle.portal_postmortem_panel import PortalPostmortemPanel
    from portal.gui.Scaleform.daapi.view.battle import status_timer_panel
    from portal.gui.Scaleform.daapi.view.battle import portal_battle_timers
    from portal.gui.Scaleform.daapi.view.battle import guided_missile_widget
    from portal.gui.Scaleform.daapi.view.battle import interception_widget
    return (ViewSettings(VIEW_ALIAS.PORTAL_BATTLE_PAGE, PortalBattlePage, getSwfExtensionUrl('portal', 'portalBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, PortalBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, PortalFullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, PortalMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, status_timer_panel.PortalStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, portal_battle_timers.PortalBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, PortalConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PERKS_PANEL, perks_panel.PerksPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, portal_game_messages_panel.PortalMessagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, PortalRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, PortalPlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, PortalPostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, portal_battle_timers.PortalPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MAP_INFO_TIP, map_info_tip.MapInfoTip, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PORTAL_BATTLE_VIEW_ALIASES.PORTAL_HUD_WIDGET_VIEW, portal_hud_widget.PortalHudWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PORTAL_BATTLE_VIEW_ALIASES.PLAYERS_DATA_PANEL, portal_players_data_panel.PortalPlayersDataPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL, portal_enemies_data_panel.PortalEnemiesDataPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PORTAL_BATTLE_VIEW_ALIASES.PORTAL_CAMP_CAPTURABLE_PROGRESS_BAR, PortalCampCamptureProgressBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PORTAL_BATTLE_VIEW_ALIASES.GUIDED_MISSILE_WIDGET, guided_missile_widget.GuidedMissileWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PORTAL_BATTLE_VIEW_ALIASES.INTERCEPTION_WIDGET, interception_widget.InterceptionWidget, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.PORTAL_BATTLE_PAGE), _PortalBattlePackageBusinessHandler())


class _PortalBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_LOADING, self.loadViewByCtxEvent), (VIEW_ALIAS.PORTAL_BATTLE_PAGE, self._loadPage))
        super(_PortalBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            if not self.__sessionProvider.isReplayPlaying:
                page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
