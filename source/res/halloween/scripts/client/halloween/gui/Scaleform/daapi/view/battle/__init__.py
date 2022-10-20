# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle import shared
from halloween.gui.Scaleform.daapi.view.battle.battle_loading import BattleLoading
from halloween.gui.Scaleform.daapi.view.battle.page import HalloweenPage
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, ConditionalViewSettings
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.bootcamp.BCPreBattleTimer import BCPreBattleTimer
from gui.Scaleform.daapi.view.bootcamp.BCVehicleMessages import BCVehicleMessages
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
__all__ = ('HalloweenPage',)

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from gui.Scaleform.daapi.view.battle.shared import damage_info_panel
    from gui.Scaleform.daapi.view.battle.shared import debug_panel
    from halloween.gui.Scaleform.daapi.view.battle import indicators as hw_indicators
    from gui.Scaleform.daapi.view.battle.shared import indicators
    from gui.Scaleform.daapi.view.battle.shared import ingame_help
    from gui.Scaleform.daapi.view.battle.shared import ingame_menu
    from halloween.gui.Scaleform.daapi.view.battle import messages as hw_messages
    from gui.Scaleform.daapi.view.battle.shared import radial_menu
    from halloween.gui.Scaleform.daapi.view.battle import damage_log_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_loading_minimap
    from gui.Scaleform.daapi.view.battle.shared.vehicles import dualgun_component
    from gui.Scaleform.daapi.view.battle.shared import callout_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_notifier
    from gui.Scaleform.daapi.view.battle.shared import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.classic import full_stats
    from halloween.gui.Scaleform.daapi.view.battle import players_panel
    from halloween.gui.Scaleform.daapi.view.battle import minimap
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from halloween.gui.Scaleform.daapi.view.battle import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    from halloween.gui.Scaleform.daapi.view.battle import consumables_panel
    from halloween.gui.Scaleform.daapi.view.battle import stats_exchange
    from halloween.gui.Scaleform.daapi.view.battle import postmortem_panel
    from halloween.gui.Scaleform.daapi.view.battle import battle_buff_hint
    from halloween.gui.Scaleform.daapi.view.battle import battle_pickup_hint
    from halloween.gui.Scaleform.daapi.view.battle import battle_base_hint
    from halloween.gui.Scaleform.daapi.view.battle import buffs_panel
    from halloween.gui.Scaleform.daapi.view.battle import game_messages_panel
    from halloween.gui.Scaleform.daapi.view.battle import event_bases_panel
    from halloween.gui.Scaleform.daapi.view.battle import damage_panel
    return (ViewSettings(VIEW_ALIAS.INGAME_MENU, ingame_menu.IngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, damage_log_panel.HalloweenDamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_HELP, ingame_help.IngameHelpWindow, 'ingameHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ViewSettings(VIEW_ALIAS.INGAME_DETAILS_HELP, ingame_help.IngameDetailsHelpWindow, 'ingameDetailsHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.HalloweenDamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEBUG_PANEL, debug_panel.DebugPanel, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BootcampComponentOverride(battle_timers.PreBattleTimer, BCPreBattleTimer), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, BootcampComponentOverride(hw_messages.HalloweenVehicleMessages, BCVehicleMessages), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, hw_messages.HalloweenVehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, hw_messages.HalloweenPlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RADIAL_MENU, radial_menu.RadialMenu, None, WindowLayer.UNDEFINED, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL, damage_info_panel.DamageInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, hw_indicators.HalloweenSixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINIMAP_ON_BATTLE_LOADING, battle_loading_minimap.BattleLoadingMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR, indicators.SiegeModeIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL, dualgun_component.DualGunComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CALLOUT_PANEL, callout_panel.CalloutPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_NOTIFIER, battle_notifier.BattleNotifier, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR, indicators.RocketAcceleratorIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.CLASSIC_BATTLE_PAGE, HalloweenPage, 'HWBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.EventStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.HWPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.HWMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.HWConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.HalloweenBattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.HWGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.HWPostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_BUFF_HINT, battle_buff_hint.BattleBuffHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_PICKUP_HINT, battle_pickup_hint.BattlePickupHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_BASE_HINT, battle_base_hint.BattleBaseHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL, buffs_panel.HWBuffsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BASE_PANEL, event_bases_panel.EventBasesPanel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.CLASSIC_BATTLE_PAGE),) + shared.getBusinessHandlers()
