# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/__init__.py
from gui.Scaleform.daapi.view.battle.event.festival_race.fest_race_full_stats import FestRaceFullStats
from gui.Scaleform.daapi.view.battle.event.festival_race.fest_race_ingame_menu import FestRaceIngameMenu
from gui.Scaleform.daapi.view.battle.event.page import FestivalRaceBattlePage
from gui.Scaleform.daapi.view.bootcamp.BCPreBattleTimer import BCPreBattleTimer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates, ConditionalViewSettings
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.app_loader import settings as app_settings
from gui.Scaleform.daapi.view.battle.event import battle_loading
from gui.shared import EVENT_BUS_SCOPE, events
__all__ = ('FestivalRaceBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.event import stats_exchange
    from gui.Scaleform.daapi.view.battle.event.team_bases_panel_helper import getFestivalSettingItem
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    team_bases_panel._getSettingItem = getFestivalSettingItem
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.event.event_consumables_panel import EventConsumablesPanel
    from gui.Scaleform.daapi.view.battle.event.event_speedometer_panel import EventSpeedometerPanel
    from gui.Scaleform.daapi.view.battle.event.festival_race.festival_race_player_health_bar import FestivalRacePlayerHealthBar
    from gui.Scaleform.daapi.view.battle.event.festival_race.festival_race_message import FestivalRaceMessageView
    from gui.Scaleform.daapi.view.battle.event.festival_race.minimap import FestivalRaceMinimapComponent
    from gui.Scaleform.daapi.view.battle.event.festival_race.fest_race_ingame_help import FestRaceIngameHelp
    from gui.Scaleform.daapi.view.battle.event.battle_timers import EventBattleTimer, FestRacePreBattleTimer
    return (ViewSettings(VIEW_ALIAS.EVENT_BATTLE_PAGE, FestivalRaceBattlePage, 'festivalRaceBattlePage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.EventBattleLoading, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.EventStatisticsDataController, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_FULL_STATS, FestRaceFullStats, 'festRaceFullStats.swf', ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, FestivalRaceMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.DestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, EventBattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, EventConsumablesPanel, 'festRaceConsPanel.swf', ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_PLAYER_HEALTH_BAR, FestivalRacePlayerHealthBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_MESSAGES, FestivalRaceMessageView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_SPEEDOMETER, EventSpeedometerPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_HELP, FestRaceIngameHelp, 'festRaceIngameHelp.swf', ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BootcampComponentOverride(FestRacePreBattleTimer, BCPreBattleTimer), None, ViewTypes.COMPONENT, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_MENU, FestRaceIngameMenu, 'ingameMenu.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False))


def getBusinessHandlers():
    return (_EventBattlePackageBusinessHandler(),)


class _EventBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_BATTLE_PAGE, self._loadPage), (events.GameEvent.ESC_PRESSED, self.__handleEscPressed))
        super(_EventBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(ViewTypes.DEFAULT, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return

    def __handleEscPressed(self, event):
        battlePage = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.EVENT_BATTLE_PAGE)
        if battlePage.isHelpShown():
            battlePage.hideIngameHelp(event)
            return
        else:
            window = self.findViewByAlias(ViewTypes.TOP_WINDOW, BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_MENU)
            if window is not None:
                window.destroy()
            else:
                self.loadViewWithDefName(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_MENU)
            return
