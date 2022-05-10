# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCVehicleContextMenuHandler
from hangar.carousel.handlers import BRVehicleContextMenuHandler
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.battle_result.context_menu import BRBattleResultContextMenu

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.BATTLE_ROYALE_VEHICLE, BootcampComponentOverride(BRVehicleContextMenuHandler, BCVehicleContextMenuHandler)), (CONTEXT_MENU_HANDLER_TYPE.BR_BATTLE_RESULT_CONTEXT_MENU, BRBattleResultContextMenu))


def getViewSettings():
    from commander_cmp import CommanderComponent
    from tech_parameters_cmp import TechParametersComponent
    from hangar_bottom_panel_cmp import HangarBottomPanelComponent
    from proxy_currency_panel import ProxyCurrencyComponentInject
    from hangar_vehicle_info_view import HangarVehicleModulesConfigurator
    from hangar_vehicle_info_view import HangarVehicleInfo
    from level_up_view import BattleRoyaleLevelUpView
    from battle_royale_prime_time import BattleRoyalePrimeTimeView
    from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.carousel.tank import RoyaleTankCarousel
    return (ViewSettings(BATTLEROYALE_ALIASES.LEVEL_UP, BattleRoyaleLevelUpView, BATTLEROYALE_ALIASES.LEVEL_UP_UI, WindowLayer.OVERLAY, BATTLEROYALE_ALIASES.LEVEL_UP, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, HangarVehicleInfo, 'battleRoyaleVehInfo.swf', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, BattleRoyalePrimeTimeView, HANGAR_ALIASES.EPIC_PRIME_TIME, WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ComponentSettings(BATTLEROYALE_ALIASES.VEH_MODULES_CONFIGURATOR_CMP, HangarVehicleModulesConfigurator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.COMMANDER_COMPONENT, CommanderComponent, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.TECH_PARAMETERS_COMPONENT, TechParametersComponent, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.BOTTOM_PANEL_COMPONENT, HangarBottomPanelComponent, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.PROXY_CURRENCY_PANEL_COMPONENT, ProxyCurrencyComponentInject, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HANGAR_ALIASES.ROYALE_TANK_CAROUSEL, RoyaleTankCarousel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattleRoyalePackageBusinessHandler(),)


class BattleRoyalePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, self.loadViewByCtxEvent), (BATTLEROYALE_ALIASES.LEVEL_UP, self.loadViewByCtxEvent), (BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, self.loadViewByCtxEvent))
        super(BattleRoyalePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
