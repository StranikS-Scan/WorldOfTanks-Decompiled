# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, getSwfExtensionUrl
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.page import WhiteTigerBattlePage
__all__ = ('WhiteTigerBattlePage',)

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared.base_stats import StatsBase
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import perks_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.event.event_loading_page import EventLoadingPage
    from gui.Scaleform.daapi.view.battle.event import event_point_counter
    from gui.Scaleform.daapi.view.battle.event import event_buffs_panel
    from gui.Scaleform.daapi.view.battle.event import event_objectives
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from gui.Scaleform.daapi.view.battle.shared import messages
    from gui.Scaleform.daapi.view.battle.shared import ingame_help
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.team_bases_panel import WhiteTigerTeamBasesPanel
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications import panel as sn_panel
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import consumables_panel
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import battle_timer
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import boss_teleport
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import hunter_respawn
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import boss_widget
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import game_messages_panel
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import minimap
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import stats_exchange
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import white_tiger_players_panel
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import battle_hint
    return (ViewSettings(VIEW_ALIAS.EVENT_BATTLE_PAGE, WhiteTigerBattlePage, getSwfExtensionUrl('white_tiger', 'WTBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_DETAILS_HELP, ingame_help.IngameDetailsHelpWindow, getSwfExtensionUrl('white_tiger', 'WTIngameDetailsHelpWindow.swf'), WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, WhiteTigerTeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PERKS_PANEL, perks_panel.PerksPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_POINT_COUNTER, event_point_counter.EventPointCounter, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_LOADING, EventLoadingPage, getSwfExtensionUrl('white_tiger', 'WTBattleLoading.swf'), WindowLayer.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_STATS, StatsBase, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL, event_buffs_panel.EventBuffsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_OBJECTIVES, event_objectives.EventObjectivesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.PreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, white_tiger_players_panel.WhiteTigerPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.WhiteTigerStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.WhiteTigerMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.WhiteTigerGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BOSS_WIDGET, boss_widget.WhiteTigerBossWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_HUNTER_RESPAWN, hunter_respawn.WhiteTigerHunterRespawnView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BOSS_TELEPORT, boss_teleport.WhiteTigerBossTeleportView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timer.WhiteTigerBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, sn_panel.WhiteTigerStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.WhiteTigerConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_WhiteTigerBattlePackageBusinessHandler(),)


class _WhiteTigerBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_LOADING, self.loadViewByCtxEvent), (VIEW_ALIAS.EVENT_BATTLE_PAGE, self._loadPage))
        super(_WhiteTigerBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
