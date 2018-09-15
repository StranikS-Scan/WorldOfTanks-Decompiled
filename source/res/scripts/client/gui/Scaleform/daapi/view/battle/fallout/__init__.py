# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.fallout import consumables_panel
    from gui.Scaleform.daapi.view.battle.fallout import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.fallout import full_stats
    from gui.Scaleform.daapi.view.battle.fallout import respawn
    from gui.Scaleform.daapi.view.battle.fallout import page
    from gui.Scaleform.daapi.view.battle.fallout import score_panel
    from gui.Scaleform.daapi.view.battle.fallout import stats_exchange
    from gui.Scaleform.daapi.view.battle.fallout import minimap
    from gui.Scaleform.daapi.view.battle.fallout import battle_timer
    from gui.Scaleform.daapi.view.battle.fallout import fallout_battle_loading
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    return (ViewSettings(VIEW_ALIAS.FALLOUT_CLASSIC_PAGE, page.FalloutClassicPage, 'falloutClassicPage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.FALLOUT_MULTITEAM_PAGE, page.FalloutMultiteamPage, 'falloutMultiteamPage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, fallout_battle_loading.FalloutMultiTeamBattleLoading, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.FalloutStatisticsDataController, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FALLOUT_CLASSIC_STATS, full_stats.FalloutClassicFullStats, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FALLOUT_MULTITEAM_STATS, full_stats.FalloutMultiTeamFullStats, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FALLOUT_CONSUMABLES_PANEL, consumables_panel.FalloutConsumablesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FALLOUT_DESTROY_TIMERS_PANEL, destroy_timers_panel.FalloutDestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FALLOUT_RESPAWN_VIEW, respawn.FalloutRespawn, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.FalloutMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FALLOUT_SCORE_PANEL, score_panel.FalloutScorePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timer.FalloutBattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.FALLOUT_CLASSIC_PAGE, VIEW_ALIAS.FALLOUT_MULTITEAM_PAGE),)
