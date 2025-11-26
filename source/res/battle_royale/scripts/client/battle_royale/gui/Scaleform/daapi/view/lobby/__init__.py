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
from hangar.carousel.handlers import BRVehicleContextMenuHandler
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.battle_result.context_menu import BRBattleResultContextMenu

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.BATTLE_ROYALE_VEHICLE, BRVehicleContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.BR_BATTLE_RESULT_CONTEXT_MENU, BRBattleResultContextMenu))


def getViewSettings():
    from hangar_vehicle_info_view import HangarVehicleModulesConfigurator
    from hangar_vehicle_info_view import HangarVehicleInfo
    from battle_royale_prime_time import BattleRoyalePrimeTimeView
    from battle_royale_browser_view import BattleRoyaleBrowserView
    from battle_royale.gui.impl.lobby.views.battle_result_view.battle_result_view import BattleRoyaleBattleResultsWindow
    from battle_royale.gui.impl.lobby.views.battle_royale_hangar_view import BattleRoyaleHangarWindow
    from battle_royale.gui.impl.lobby.views.pre_battle import BattleRoyalePreBattleWindow
    from battle_royale_progression.gui.impl.lobby.views.progression_main_view import BattleRoyaleProgressionWindow
    return (ViewSettings(BATTLEROYALE_ALIASES.BR_HANGAR_VIEW, BattleRoyaleHangarWindow, '', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.BR_HANGAR_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BR_TOURNAMENT_BATTLE_QUEUE, BattleRoyalePreBattleWindow, '', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.BR_TOURNAMENT_BATTLE_QUEUE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BR_PROGRESSION, BattleRoyaleProgressionWindow, '', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.BR_PROGRESSION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BR_BATTLE_RESULTS, BattleRoyaleBattleResultsWindow, '', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.BR_BATTLE_RESULTS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, HangarVehicleInfo, 'battleRoyaleVehInfo.swf', WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, BattleRoyalePrimeTimeView, HANGAR_ALIASES.EPIC_PRIME_TIME, WindowLayer.SUB_VIEW, BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(BATTLEROYALE_ALIASES.BATTLE_ROYALE_BROWSER_VIEW, BattleRoyaleBrowserView, 'browserScreen.swf', WindowLayer.TOP_WINDOW, BATTLEROYALE_ALIASES.BATTLE_ROYALE_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(BATTLEROYALE_ALIASES.VEH_MODULES_CONFIGURATOR_CMP, HangarVehicleModulesConfigurator, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattleRoyalePackageBusinessHandler(),)


class BattleRoyalePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.BATTLE_ROYALE_BROWSER_VIEW, self.loadViewByCtxEvent),
         (BATTLEROYALE_ALIASES.BR_HANGAR_VIEW, self.loadView),
         (BATTLEROYALE_ALIASES.BR_TOURNAMENT_BATTLE_QUEUE, self.loadView),
         (BATTLEROYALE_ALIASES.BR_PROGRESSION, self.loadView),
         (BATTLEROYALE_ALIASES.BR_BATTLE_RESULTS, self.loadView))
        super(BattleRoyalePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
