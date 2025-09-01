# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/__init__.py
from last_stand.gui.ls_gui_constants import VIEW_ALIAS
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.Scaleform.framework import getSwfExtensionUrl, ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from last_stand.gui.scaleform.genConsts.LS_BATTLE_VIEW_ALIASES import LS_BATTLE_VIEW_ALIASES

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from last_stand.gui.scaleform.daapi.view.battle.page import LastStandBattlePage
    from gui.Scaleform.daapi.view.battle.shared import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from gui.Scaleform.daapi.view.battle.shared import indicators
    from last_stand.gui.scaleform.daapi.view.battle.phase_indicator import LSPhaseIndicator
    from last_stand.gui.scaleform.daapi.view.battle.status_notifications.panel import LSStatusNotificationTimerPanel
    from last_stand.gui.scaleform.daapi.view.battle import damage_log_panel
    from last_stand.gui.scaleform.daapi.view.battle import ribbons_panel
    from last_stand.gui.scaleform.daapi.view.battle.souls_counter_panel import LSSoulsCounter
    from last_stand.gui.scaleform.daapi.view.battle import event_timer
    from last_stand.gui.scaleform.daapi.view.battle import postmortem_panel
    from last_stand.gui.scaleform.daapi.view.battle.minimap.minimap import LSMinimapComponent
    from last_stand.gui.scaleform.daapi.view.battle import consumables_panel
    from last_stand.gui.scaleform.daapi.view.battle import messages as ls_messages
    from last_stand.gui.scaleform.daapi.view.battle import indicators as ls_indicators
    from last_stand.gui.scaleform.daapi.view.battle import battle_hint
    from last_stand.gui.scaleform.daapi.view.battle.players_panel import LSPlayersPanel
    from last_stand.gui.scaleform.daapi.view.battle import game_messages_panel
    from last_stand.gui.scaleform.daapi.view.battle import battle_timers
    from last_stand.gui.scaleform.daapi.view.battle import stats_exchange
    from last_stand.gui.scaleform.daapi.view.battle.hint_panel.component import LSBattleHintPanel
    from gui.Scaleform.daapi.view.battle.shared import situation_indicators
    return (ViewSettings(VIEW_ALIAS.LAST_STAND_BATTLE_PAGE, LastStandBattlePage, getSwfExtensionUrl('last_stand', 'LastStandBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, ls_messages.LSVehicleMessages, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, damage_log_panel.LSDamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.LSStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(LS_BATTLE_VIEW_ALIASES.LS_PLAYERS_PANEL, LSPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, LSMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.LSConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.LSBattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.LSGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, LSBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, ls_messages.LSVehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, ls_messages.LSPlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.PreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(LS_BATTLE_VIEW_ALIASES.PHASE_INDICATOR, LSPhaseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, LSStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(LS_BATTLE_VIEW_ALIASES.POINT_COUNTER, LSSoulsCounter, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_TIMER, event_timer.EventTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.LSPostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, ls_indicators.LSSixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TARGET_DESIGNATOR_UNSPOTTED_MARKER, indicators.TargetDesignatorUnspottedIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(LS_BATTLE_VIEW_ALIASES.PINNABLE_BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(LS_BATTLE_VIEW_ALIASES.PROGRESS_BAR_BATTLE_HINT, battle_hint.DefenceProgressBarBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(LS_BATTLE_VIEW_ALIASES.CONVOY_BATTLE_HINT, battle_hint.ConvoyProgressBarBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SITUATION_INDICATORS, situation_indicators.SituationIndicators, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_LastStandPackageBusinessHandler(),)


class _LastStandPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.LAST_STAND_BATTLE_PAGE, self._loadPage),)
        super(_LastStandPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
