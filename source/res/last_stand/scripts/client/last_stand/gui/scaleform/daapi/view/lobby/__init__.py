# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings
from last_stand.gui.impl.lobby.hangar_view import HangarWindow
from last_stand.gui.impl.lobby.reward_path_view import RewardPathWindow
from last_stand.gui.scaleform.daapi.view.lobby.hangar.extension_browser import ExtensionBrowser
from gui.Scaleform.framework import GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from last_stand.gui.scaleform.genConsts.LS_CM_HANDLER_TYPE import LS_CM_HANDLER_TYPE
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby import user_cm_handlers
    return ((LS_CM_HANDLER_TYPE.LS_BATTLE_RESULTS, user_cm_handlers.AppealCMHandler),)


def getViewSettings():
    from last_stand.gui.scaleform.daapi.view.lobby.hangar.ls_module_info import LSModuleInfoWindow
    from last_stand.gui.scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import LSVehiclePreview
    return (GroupedViewSettings(LAST_STAND_HANGAR_ALIASES.LS_MODULE_INFO, LSModuleInfoWindow, 'moduleInfo.swf', WindowLayer.WINDOW, LAST_STAND_HANGAR_ALIASES.LS_MODULE_INFO, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(LAST_STAND_HANGAR_ALIASES.LS_BROWSER, ExtensionBrowser, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, LAST_STAND_HANGAR_ALIASES.LS_BROWSER, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW, LSVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(LAST_STAND_HANGAR_ALIASES.LS_HERO_PREVIEW, LSVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, LAST_STAND_HANGAR_ALIASES.LS_HERO_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(LAST_STAND_HANGAR_ALIASES.LS_HANGAR, HangarWindow, '', WindowLayer.SUB_VIEW, LAST_STAND_HANGAR_ALIASES.LS_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH, RewardPathWindow, '', WindowLayer.SUB_VIEW, LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (LobbyPackageBusinessHandler(),)


class LobbyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((LAST_STAND_HANGAR_ALIASES.LS_MODULE_INFO, self.__moduleWindowHandler),
         (LAST_STAND_HANGAR_ALIASES.LS_BROWSER, self.loadViewByCtxEvent),
         (LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (LAST_STAND_HANGAR_ALIASES.LS_HERO_PREVIEW, self.loadViewByCtxEvent),
         (LAST_STAND_HANGAR_ALIASES.LS_HANGAR, self.loadViewByCtxEvent),
         (LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH, self.loadViewByCtxEvent))
        super(LobbyPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __moduleWindowHandler(self, event):
        name = event.loadParams.viewKey.name
        window = self.findViewByName(WindowLayer.WINDOW, name)
        if window is not None:
            self.bringViewToFront(name)
        else:
            self.loadViewByCtxEvent(event)
        return
