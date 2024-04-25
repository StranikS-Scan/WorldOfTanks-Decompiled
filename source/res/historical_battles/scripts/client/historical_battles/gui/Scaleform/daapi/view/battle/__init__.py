# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from historical_battles.gui.Scaleform.daapi.view.battle.shared.messages.player_messages import HistoricalBattlePlayerMessages
from historical_battles.gui.Scaleform.daapi.view.battle.shared.messages.vehicle_messages import HistoricalBattleVehicleMessages
from historical_battles.gui.Scaleform.daapi.view.battle.shared.messages.vehicle_errors import HistoricalBattlesVehicleErrorMessages

def getHBContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.HB_PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getHBViewSettings():
    from historical_battles.gui.Scaleform.daapi.view.battle.status_timer_panel import HBStatusNotificationTimerPanel
    from historical_battles.gui.impl.battle.event_stats import EventStatsInjected
    from historical_battles.gui.Scaleform.daapi.view.battle.player_lives import HistoricalBattlesPlayerLives
    from historical_battles.gui.Scaleform.daapi.view.battle.phase_indicator import HistoricalBattlesPhaseIndicator
    from historical_battles.gui.Scaleform.daapi.view.battle.players_panel import HistoricalBattlesPlayersPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.battle_loading import HistoricalBattleLoading
    from historical_battles.gui.Scaleform.daapi.view.battle.consumables_panel import HistoricalBattlesConsumablesPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.ribbons_panel import HistoricalBattlesRibbonsPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.timer import HistoricalBattlesTimer
    from historical_battles.gui.Scaleform.daapi.view.battle.battle_hint import BattleHint
    from historical_battles.gui.Scaleform.daapi.view.battle.radial_menu import HistoricalRadialMenu
    from historical_battles.gui.Scaleform.daapi.view.battle.minimap import HistoricalFullMapComponent, HistoricalMinimapComponent
    from historical_battles.gui.Scaleform.daapi.view.battle.damage_log_panel import HistoricalBattlesDamageLogPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.battle_messenger import HBBattleMessenger
    from historical_battles.gui.Scaleform.daapi.view.battle.postmortem_panel import HBPostmortemPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.battle_timers import HistoricalBattlesPreBattleTimer
    from historical_battles.gui.Scaleform.daapi.view.battle.game_messages_panel import HistoricalBattlesGameMessagesPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.team_bases_panel import HBTeamBasesPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.shared.event_battle_hint_panel import EventBattleHintPanel
    from historical_battles.gui.Scaleform.daapi.view.battle.role_notification import HBRoleNotification
    return (ViewSettings(VIEW_ALIAS.HISTORICAL_BATTLE_LOADING, HistoricalBattleLoading, 'HBLoading.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYER_LIVES, HistoricalBattlesPlayerLives, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL, HistoricalBattlesPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PHASE_INDICATOR, HistoricalBattlesPhaseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, HistoricalBattlesConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, HistoricalBattlesRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP, HistoricalFullMapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, HBStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, HistoricalMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_TIMER, HistoricalBattlesTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_BASE_HINT, BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, EventBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_STATS_WIDGET, EventStatsInjected, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, HistoricalBattlesDamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, HistoricalBattlesPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER, HBBattleMessenger, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RADIAL_MENU, HistoricalRadialMenu, None, WindowLayer.UNDEFINED, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, HistoricalBattlesGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, HBPostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, HistoricalBattlePlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, HBTeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_ROLE_NOTIFICATION, HBRoleNotification, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, HistoricalBattleVehicleMessages, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, HistoricalBattlesVehicleErrorMessages, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE))


def getHBBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.HISTORICAL_BATTLES), HistoricalBattlesBusinessHandler())


class HistoricalBattlesBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.HISTORICAL_BATTLE_LOADING, self.loadViewByCtxEvent),)
        super(HistoricalBattlesBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)
