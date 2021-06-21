# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle.epic_random.page import EpicRandomPage
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
__all__ = ('EpicRandomPage',)

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import full_stats
    from gui.Scaleform.daapi.view.battle.epic_random import players_panel
    from gui.Scaleform.daapi.view.battle.epic_random import stats_exchange
    from gui.Scaleform.daapi.view.battle.shared import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.epic_random import minimap_component
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.epic_random import battle_loading
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.shared import consumables_panel
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    return (ViewSettings(VIEW_ALIAS.EPIC_RANDOM_PAGE, EpicRandomPage, 'epicRandomPage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.EpicRandomBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.EpicRandomStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.EpicRandomPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap_component.EpicRandomMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.ConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.EPIC_RANDOM_PAGE),)
