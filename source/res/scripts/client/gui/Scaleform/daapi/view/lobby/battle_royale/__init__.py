# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.battle_royale.commander_cmp import CommanderComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.tech_parameters_cmp import TechParametersComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_bottom_panel_cmp import HangarBottomPanelComponent
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_vehicle_info_view import HangarVehicleModulesConfigurator
from gui.Scaleform.daapi.view.lobby.battle_royale.hangar_vehicle_info_view import HangarVehicleInfo
from gui.Scaleform.daapi.view.lobby.battle_royale.level_up_view import BattleRoyaleLevelUpView
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(BATTLEROYALE_ALIASES.LEVEL_UP, BattleRoyaleLevelUpView, BATTLEROYALE_ALIASES.LEVEL_UP_UI, WindowLayer.OVERLAY, BATTLEROYALE_ALIASES.LEVEL_UP, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.VEH_MODULES_CONFIGURATOR_CMP, HangarVehicleModulesConfigurator, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, HangarVehicleInfo, 'battleRoyaleVehInfo.swf', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.COMMANDER_COMPONENT, CommanderComponent, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.TECH_PARAMETERS_COMPONENT, TechParametersComponent, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.BOTTOM_PANEL_COMPONENT, HangarBottomPanelComponent, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (BattleRoyalePackageBusinessHandler(),)


class BattleRoyalePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, self.loadViewByCtxEvent), (BATTLEROYALE_ALIASES.LEVEL_UP, self.loadViewByCtxEvent))
        super(BattleRoyalePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
