# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/__init__.py
from gui.Scaleform.daapi.view.battle.event.page import EventBattlePage
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import event_deserter_dialog
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE, events
__all__ = ('EventBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.event import minimap
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.shared import consumables_panel
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from gui.Scaleform.daapi.view.battle.event import players_panel as event_players_panel
    from gui.Scaleform.daapi.view.battle.event import player_lives
    from gui.Scaleform.daapi.view.battle.event.event_loading_page import EventLoadingPage
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.event import event_battle_timer
    from gui.Scaleform.daapi.view.battle.event import stats
    from gui.Scaleform.daapi.view.battle.event import event_destroy_timers_panel
    return (ViewSettings(VIEW_ALIAS.EVENT_BATTLE_PAGE, EventBattlePage, 'eventBattlePage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.EventMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_DESTROY_TIMERS_PANEL, event_destroy_timers_panel.EventDestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.DestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.ConsumablesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, event_players_panel.EventPlayersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_PLAYER_LIVES, player_lives.EventPlayerLives, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_LOADING, EventLoadingPage, 'eventLoading.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_TIMER, event_battle_timer.EventBattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_TIMER_TAB, event_battle_timer.EventBattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_STATS, stats.EventStats, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_FULL_MAP, minimap.EventFullMapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_INGAME_DESERTER, event_deserter_dialog.EventIngameDeserterDialog, 'eventDeserterDialog.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False))


def getBusinessHandlers():
    return (_EventBattlePackageBusinessHandler(), EventBattleDialogHandler())


class _EventBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_LOADING, self.loadViewByCtxEvent), (VIEW_ALIAS.EVENT_BATTLE_PAGE, self._loadPage))
        super(_EventBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(ViewTypes.DEFAULT, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return


class EventBattleDialogHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((events.ShowDialogEvent.SHOW_EVENT_DESERTER_DLG, self.__showEventDeserterDialog),)
        super(EventBattleDialogHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.GLOBAL)

    def __showEventDeserterDialog(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.EVENT_INGAME_DESERTER, event.meta, event.handler)
