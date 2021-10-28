# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event import event_consumables_panel, event_phase_indicator
from gui.Scaleform.daapi.view.battle.event.event_ingame_help import HWIngameHelpWindow
from gui.Scaleform.daapi.view.battle.event.nearby_vehicle_indicator import NearByVehicleIndicator
from gui.Scaleform.daapi.view.battle.event.page import EventBattlePage
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
__all__ = ('EventBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.event import minimap
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.event import event_ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_loading
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from gui.Scaleform.daapi.view.battle.event import players_panel as event_players_panel
    from gui.Scaleform.daapi.view.battle.event.event_loading_page import EventLoadingPage
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.event import game_messages_panel
    from gui.Scaleform.daapi.view.battle.event import event_point_counter
    from gui.Scaleform.daapi.view.battle.event import event_timer
    from gui.Scaleform.daapi.view.battle.event import nearby_vehicle_indicator
    from gui.Scaleform.daapi.view.battle.event import stats
    from gui.Scaleform.daapi.view.battle.event import event_destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.event import event_buffs_panel
    from gui.Scaleform.daapi.view.battle.event import event_buff_notification_panel
    from gui.Scaleform.daapi.view.battle.event import event_objectives
    from gui.Scaleform.daapi.view.battle.event import event_boss_hp_bar
    return (ViewSettings(VIEW_ALIAS.EVENT_BATTLE_PAGE, EventBattlePage, 'eventBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_DESTROY_TIMERS_PANEL, event_destroy_timers_panel.EventDestroyTimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, event_consumables_panel.EventConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, event_ribbons_panel.EventRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, event_players_panel.EventPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.EventMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_POINT_COUNTER, event_point_counter.EventPointCounter, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_LOADING, EventLoadingPage, 'eventLoading.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_TIMER, event_timer.EventTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BOSS_INDICATOR_PROGRESS, nearby_vehicle_indicator.NearByVehicleIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_STATS, stats.EventStats, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL, event_buffs_panel.EventBuffsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BUFF_NOTIFICATION_SYSTEM, event_buff_notification_panel.EventBuffsNotificationSystem, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_OBJECTIVES, event_objectives.EventObjectivesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_PHASE_INDICATOR, event_phase_indicator.EventPhaseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BOSS_HPBAR, event_boss_hp_bar.EventBossHPBar, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_INGAME_HELP, HWIngameHelpWindow, 'HWIngameHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True))


def getBusinessHandlers():
    return (_EventBattlePackageBusinessHandler(),)


class _EventBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_LOADING, self.loadViewByCtxEvent), (VIEW_ALIAS.EVENT_BATTLE_PAGE, self._loadPage), (VIEW_ALIAS.EVENT_INGAME_HELP, self.__handleHelpEvent))
        super(_EventBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return

    def __handleHelpEvent(self, _):
        window = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.EVENT_INGAME_HELP)
        if window is not None:
            window.destroy()
        elif self._app is None or not self._app.isModalViewShown():
            self.loadViewWithDefName(VIEW_ALIAS.EVENT_INGAME_HELP)
        return
