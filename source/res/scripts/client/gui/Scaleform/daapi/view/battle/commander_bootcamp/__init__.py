# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander_bootcamp/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.commander.indicators import RTSSixthSenseIndicator
from gui.Scaleform.daapi.view.battle.commander.page import CommanderBattlePage
from gui.Scaleform.daapi.view.battle.commander_bootcamp.page import BCCommanderBattlePage
from gui.Scaleform.framework import ComponentSettings, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
__all__ = ('CommanderBattlePage',)

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    from gui.Scaleform.daapi.view.battle.commander import vehicles_panel
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler), (BATTLE_CONTEXT_MENU_HANDLER_TYPE.COMMANDER_VEHICLES_PANEL, vehicles_panel.VehiclesPanelContextMenuHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.commander import battle_timer
    from gui.Scaleform.daapi.view.battle.commander import commander_help
    from gui.Scaleform.daapi.view.battle.commander import full_stats
    from gui.Scaleform.daapi.view.battle.commander import vehicles_panel
    from gui.Scaleform.daapi.view.battle.commander import vehicle_selection
    from gui.Scaleform.daapi.view.battle.commander import players_panel
    from gui.Scaleform.daapi.view.battle.commander import stats_exchange
    from gui.Scaleform.daapi.view.battle.commander import battle_loading
    from gui.Scaleform.daapi.view.battle.commander.minimap import component as minimap_component
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.commander import timers_panel
    from gui.Scaleform.daapi.view.battle.shared import consumables_panel
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component as hint_component
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from gui.Scaleform.daapi.view.bootcamp.BCSecondaryHint import BCSecondaryHint
    from gui.Scaleform.daapi.view.bootcamp.BCBattleTopHint import BCBattleTopHint
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    from gui.Scaleform.daapi.view.battle.commander_bootcamp import spawn_menu
    return (ViewSettings(VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE, BCCommanderBattlePage, 'BCCommanderBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU, spawn_menu.BCSpawnMenu, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMMANDER_SUPPLY_PANEL, BaseDAAPIComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BOOTCAMP_SECONDARY_HINT, BCSecondaryHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BOOTCAMP_BATTLE_TOP_HINT, BCBattleTopHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMMANDER_VEHICLES_PANEL, vehicles_panel.VehiclesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMMANDER_HELP, commander_help.CommanderHelp, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.RTSStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.RTSFullStats, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.RTSPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap_component.CommanderMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.CommanderTimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timer.R4BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.ConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, hint_component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMMANDER_VEHICLE_SELECTION, vehicle_selection.VehicleSelection, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, RTSSixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_RTSBootcamBattlePackageBusinessHandler(),)


class _RTSBootcamBattlePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        self.__hideHints = False
        listeners = ((VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE, self._loadPage),
         (VIEW_ALIAS.BOOTCAMP_HINT_COMPLETE, self.__onComplete),
         (VIEW_ALIAS.BOOTCAMP_HINT_HIDE, self.__onHide),
         (VIEW_ALIAS.BOOTCAMP_HINT_CLOSE, self.__onCloseHint),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_TOP_HINT, self.__onShowHint))
        super(_RTSBootcamBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return

    def __onComplete(self, _):
        battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE)
        if battleView is not None:
            battleView.topHint.complete()
        return

    def __onHide(self, _):
        battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE)
        if battleView is not None:
            battleView.topHint.hideHint()
        return

    def __onCloseHint(self, _):
        battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE)
        if battleView is not None and battleView.topHint is not None:
            battleView.topHint.closeHint()
        return

    def __onShowHint(self, event):
        if not self.__hideHints:
            battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.COMMANDER_BOOTCAMP_BATTLE_PAGE)
            if battleView is not None:
                battleView.topHint.showHint(event.ctx)
        return
