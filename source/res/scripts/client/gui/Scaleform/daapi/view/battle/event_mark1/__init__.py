# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/__init__.py
from gui.Scaleform.daapi.view.battle.event_mark1.page import EventMark1Page
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.shared import EVENT_BUS_SCOPE
__all__ = ('EventMark1Page',)

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.classic import full_stats
    from gui.Scaleform.daapi.view.battle.classic import players_panel
    from gui.Scaleform.daapi.view.battle.event_mark1 import stats_exchange
    from gui.Scaleform.daapi.view.battle.event_mark1 import consumables_panel
    from gui.Scaleform.daapi.view.battle.event_mark1 import vehicle_messages
    from gui.Scaleform.daapi.view.battle.event_mark1 import minimap
    from gui.Scaleform.daapi.view.battle.event_mark1 import flag_nots
    from gui.Scaleform.daapi.view.battle.event_mark1 import event_nots
    from gui.Scaleform.daapi.view.battle.event_mark1 import progress_bar
    from gui.Scaleform.daapi.view.battle.event_mark1 import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.event_mark1 import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import destroy_timers_panel
    return (ViewSettings(VIEW_ALIAS.EVENT_BATTLE_PAGE, EventMark1Page, 'eventBattlePage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.Mark1EventStatisticsDataController, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_CONSUMABLES_PANEL, consumables_panel.Mark1ConsumablesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_VEHICLE_MESSAGES, vehicle_messages.Mark1VehicleMessages, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PlayersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FLAG_NOTIFICATION, flag_nots.EventMark1FlagNotification, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.Mark1MinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.DestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.Mark1BattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_NOTIFICATION_PANEL, event_nots.Mark1EventNotification, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.EVENT_PROGRESS_PANEL, progress_bar.Mark1ProgressBarPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.Mark1BattleEndWarningPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_EventPackageBusinessHandler(),)


class _EventPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_BATTLE_PAGE, self.loadViewBySharedEvent),)
        super(_EventPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)
