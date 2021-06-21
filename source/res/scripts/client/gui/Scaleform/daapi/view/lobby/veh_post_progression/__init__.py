# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_view_adaptor import VehiclePostProgressionViewAdaptor
from gui.Scaleform.framework import ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_cm_handlers import PostProgressionContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.POST_PROGRESSION_VEHICLE, PostProgressionContextMenuHandler),)


def getViewSettings():
    from gui.Scaleform.framework import ScopeTemplates
    from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_view import VehiclePostProgressionView, VehPostProgressionVehicleParams
    return (ViewSettings(VIEW_ALIAS.VEH_POST_PROGRESSION, VehiclePostProgressionView, 'vehPostProgressionView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEH_POST_PROGRESSION, ScopeTemplates.LOBBY_SUB_SCOPE), ComponentSettings(HANGAR_ALIASES.POST_PROGRESSION_INJECT, VehiclePostProgressionViewAdaptor, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_ALIASES.POST_PROGRESSION_VEHICLE_PARAMS, VehPostProgressionVehicleParams, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_VehPostProgressionBusinessHandler(),)


class _VehPostProgressionBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.VEH_POST_PROGRESSION, self.loadViewByCtxEvent),)
        super(_VehPostProgressionBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
