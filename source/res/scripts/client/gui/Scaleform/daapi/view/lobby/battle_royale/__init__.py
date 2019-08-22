# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/__init__.py
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_page import BattleRoyaleMainPage
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_progress_final import BattleRoyaleProgressFinal
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_rewards import BattleRoyaleAwardsWrapper
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_intro import BattleRoyaleIntro
from gui.Scaleform.daapi.view.meta.BattleRoyaleInfoMeta import BattleRoyaleInfoMeta
from gui.Scaleform.daapi.view.lobby.battle_royale.commander_cmp import CommanderComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.tech_parameters_cmp import TechParametersComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_bottom_panel_cmp import HangarBottomPanelComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_event_info import EventInfoComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_prime_time import BattleRoyalePrimeTimeView
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_progress_view import BattleRoyaleProgressView
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_battle_royale_results import HangarBattleRoyaleResults
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_vehicle_info_view import HangarVehicleModulesConfigurator
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_vehicle_info_view import HangarVehicleInfo
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_score_view import BattleRoyaleScoreComponent
from gui.Scaleform.daapi.view.lobby.hangar.battle_royale_widget import BattleRoyaleResultsWidget
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_summary_results import BattleRoyaleSummaryResultsComponent

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, BattleRoyalePrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, ViewTypes.LOBBY_SUB, BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(BATTLEROYALE_ALIASES.VEH_MODULES_CONFIGURATOR_CMP, HangarVehicleModulesConfigurator, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, HangarVehicleInfo, 'battleRoyaleVehInfo.swf', ViewTypes.LOBBY_SUB, BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_INTRO_ALIAS, BattleRoyaleIntro, 'battleRoyaleIntro.swf', ViewTypes.LOBBY_SUB, BATTLEROYALE_ALIASES.BATTLE_ROYALE_INTRO_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.EVENT_INFO_COMPONENT, EventInfoComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.COMMANDER_COMPONENT, CommanderComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.TECH_PARAMETERS_COMPONENT, TechParametersComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BOTTOM_PANEL_COMPONENT, HangarBottomPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_MAIN_PAGE_ALIAS, BattleRoyaleMainPage, 'battleRoyaleMainPage.swf', ViewTypes.LOBBY_SUB, BATTLEROYALE_ALIASES.BATTLE_ROYALE_MAIN_PAGE_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PROGRESS_UI, BattleRoyaleProgressView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PROGRESS_FINAL_UI, BattleRoyaleProgressFinal, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_AWARDS_UI, BattleRoyaleAwardsWrapper, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_INFO_UI, BattleRoyaleInfoMeta, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.HANGAR_BATTLE_ROYALE_RESULTS, HangarBattleRoyaleResults, 'battleRoyaleResults.swf', ViewTypes.LOBBY_SUB, BATTLEROYALE_ALIASES.HANGAR_BATTLE_ROYALE_RESULTS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_SUMMARY_RESULTS_CMP, BattleRoyaleSummaryResultsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_SCORE_RESULTS_CMP, BattleRoyaleScoreComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_RESULTS_WIDGET, BattleRoyaleResultsWidget, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattleRoyalePackageBusinessHandler(),)


class BattleRoyalePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.BATTLE_ROYALE_MAIN_PAGE_ALIAS, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.BATTLE_ROYALE_INTRO_ALIAS, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.HANGAR_BATTLE_ROYALE_RESULTS, self.loadViewByCtxEvent))
        super(BattleRoyalePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
