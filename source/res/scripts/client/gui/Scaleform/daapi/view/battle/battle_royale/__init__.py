# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.battle_royale.page import BattleRoyalePage
from gui.Scaleform.daapi.view.battle.battle_royale.radar import RadarButton
from gui.Scaleform.daapi.view.battle.battle_royale.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.daapi.view.battle.battle_royale.player_stats_in_battle import BattleRoyalePlayerStats
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator
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
    from gui.Scaleform.daapi.view.battle.battle_royale.minimap.component import BattleRoyaleMinimapComponent
    from gui.Scaleform.daapi.view.battle.battle_royale.consumables_panel import BattleRoyaleConsumablesPanel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.battle_royale import battle_loading
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.battle_royale import veh_configurator
    from gui.Scaleform.daapi.view.battle.battle_royale.battle_level_panel import BattleLevelPanel
    from gui.Scaleform.daapi.view.battle.battle_royale import players_panel as battle_royale_players_panel
    from gui.Scaleform.daapi.view.battle.battle_royale.battle_upgrade_panel import BattleUpgradePanel
    from gui.Scaleform.daapi.view.battle.battle_royale.frag_panel import FragPanel
    from gui.Scaleform.daapi.view.battle.battle_royale.full_stats import FullStatsComponent
    from gui.Scaleform.daapi.view.battle.battle_royale.select_respawn import SelectRespawnComponent
    from gui.Scaleform.daapi.view.battle.battle_royale import observer_players_panel
    return (ViewSettings(VIEW_ALIAS.BATTLE_ROYALE_PAGE, BattleRoyalePage, 'battleRoyalePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, FullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, BattleRoyaleMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, StatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BattleRoyaleConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
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
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, SixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BR_PLAYER_STATS_IN_BATTLE, BattleRoyalePlayerStats, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, observer_players_panel.ObserverPlayersPanel, ScopeTemplates.DEFAULT_SCOPE))


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
