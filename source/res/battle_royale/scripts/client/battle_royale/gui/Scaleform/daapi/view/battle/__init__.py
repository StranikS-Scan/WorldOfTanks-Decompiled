# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from battle_royale.gui.Scaleform.daapi.view.battle.page import BattleRoyalePage
from battle_royale.gui.Scaleform.daapi.view.battle.radar import RadarButton
from battle_royale.gui.Scaleform.daapi.view.battle.status_notifications.panel import BRStatusNotificationTimerPanel
from battle_royale.gui.Scaleform.daapi.view.battle.player_stats_in_battle import BattleRoyalePlayerStats
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    return tuple()


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from battle_royale.gui.Scaleform.daapi.view.battle.minimap.component import BattleRoyaleMinimapComponent
    from battle_royale.gui.Scaleform.daapi.view.battle.consumables_panel import BattleRoyaleConsumablesPanel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from battle_royale.gui.Scaleform.daapi.view.battle import battle_loading
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import perks_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from battle_royale.gui.Scaleform.daapi.view.battle import veh_configurator
    from battle_royale.gui.Scaleform.daapi.view.battle.battle_level_panel import BattleLevelPanel
    import battle_royale.gui.Scaleform.daapi.view.battle.players_panel as battle_royale_players_panel
    from battle_royale.gui.Scaleform.daapi.view.battle.battle_upgrade_panel import BattleUpgradePanel
    from battle_royale.gui.Scaleform.daapi.view.battle.frag_panel import FragPanel
    from battle_royale.gui.Scaleform.daapi.view.battle.full_stats import FullStatsComponent
    from battle_royale.gui.Scaleform.daapi.view.battle.select_respawn import SelectRespawnComponent
    import battle_royale.gui.Scaleform.daapi.view.battle.observer_players_panel as observer_players_panel
    from battle_royale.gui.Scaleform.daapi.view.battle.abilities.corroding_shot_indicator import CorrodingShotIndicator
    from battle_royale.gui.Scaleform.daapi.view.battle.postmortem_panel import BattleRoyalePostmortemPanel
    from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RespawnMessagePanel
    from battle_royale.gui.Scaleform.daapi.view.battle.timers_panel import TimersPanelPanel
    from battle_royale.gui.Scaleform.daapi.view.battle.shared.messages.player_messages import SHPlayerMessages
    return (ViewSettings(VIEW_ALIAS.BATTLE_ROYALE_PAGE, BattleRoyalePage, 'battleRoyalePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, FullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, BattleRoyaleMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, BRStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BattleRoyaleConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PERKS_PANEL, perks_panel.PerksPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_CONFIGURATOR, veh_configurator.BattleVehicleConfigurator, 'battleVehicleConfigurator.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_VEH_MODULES_CONFIGURATOR_CMP, veh_configurator.BattleVehicleConfiguratorCmp, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RADAR_BUTTON, RadarButton, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.UPGRADE_PANEL, BattleUpgradePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_PANEL, FragPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LEVEL_PANEL, BattleLevelPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL, battle_royale_players_panel.PlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN, SelectRespawnComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BR_RESPAWN_MESSAGE_PANEL, RespawnMessagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BR_PLAYER_STATS_IN_BATTLE, BattleRoyalePlayerStats, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BR_TIMERS_PANEL, TimersPanelPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CORRODING_SHOT_INDICATOR, CorrodingShotIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, observer_players_panel.ObserverPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, BattleRoyalePostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.PreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, SHPlayerMessages, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.BATTLE_ROYALE_PAGE), _BattleRoyaleBusinessHandler())


class _BattleRoyaleBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        super(_BattleRoyaleBusinessHandler, self).__init__(((BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_CONFIGURATOR, self.__handleVehConfiguratorEvent),), app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def __handleVehConfiguratorEvent(self, event):
        window = self.findViewByAlias(WindowLayer.TOP_WINDOW, BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_CONFIGURATOR)
        if window is not None:
            window.destroy()
        else:
            self.loadViewByCtxEvent(event)
        return
