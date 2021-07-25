# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/__init__.py
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.detachment.mobilization.mob_recruit_panel import MobilizationRecruitPanel
from gui.Scaleform.daapi.view.lobby.detachment.mobilization.mob_select_vehicle_popover import MobilizationSelectVehiclePopover
from gui.Scaleform.framework import ViewSettings, ComponentSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.DETACHMENT_ALIASES import DETACHMENT_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.impl.lobby.detachment.context_menu.hangar_widget_context_menu import HangarWidgetContextMenu
from gui.impl.lobby.detachment.context_menu.recruit_card_context_menu import RecruitCardContextMenu
from gui.impl.lobby.detachment.context_menu.vehicle_slot_context_menu import VehicleSlotContextMenu
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.HANGAR_WIDGET, HangarWidgetContextMenu), (CONTEXT_MENU_HANDLER_TYPE.DETACHMENT_VEHICLE_SLOT, VehicleSlotContextMenu), (CONTEXT_MENU_HANDLER_TYPE.RECRUIT_CARD_CONTEXT_MENU, RecruitCardContextMenu))


def getViewSettings():
    from gui.Scaleform.framework import ScopeTemplates
    from gui.Scaleform.daapi.view.lobby.detachment.detachment_view import DetachmentView
    from gui.Scaleform.daapi.view.lobby.detachment.mobilization.mob_detachment_view import DetachmentMobilizationView
    from gui.Scaleform.daapi.view.lobby.detachment.detachment_view_veh_params import DetachmentViewVehicleParams
    from gui.Scaleform.daapi.view.lobby.detachment.detachment_view_adaptor import DetachmentViewAdaptor
    return (ViewSettings(VIEW_ALIAS.DETACHMENT_VIEW, DetachmentView, 'detachmentView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.DETACHMENT_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True, isModal=True),
     ViewSettings(VIEW_ALIAS.DETACHMENT_MOBILIZATION_VIEW, DetachmentMobilizationView, 'detachmentMobilizationView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.DETACHMENT_MOBILIZATION_VIEW, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(HANGAR_ALIASES.DETACHMENT_VIEW_INJECT, DetachmentViewAdaptor, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.DETACHMENT_VIEW_VEHICLE_PARAMS, DetachmentViewVehicleParams, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(DETACHMENT_ALIASES.MOBILIZATION_RECRUIT, MobilizationRecruitPanel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(DETACHMENT_ALIASES.MOBILIZATION_VEHICLE_SELECT_POPOVER, MobilizationSelectVehiclePopover, 'mobilizationVehicleSelectPopover.swf', WindowLayer.TOP_WINDOW, DETACHMENT_ALIASES.MOBILIZATION_VEHICLE_SELECT_POPOVER, DETACHMENT_ALIASES.MOBILIZATION_VEHICLE_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_DetachmentBusinessHandler(),)


class _DetachmentBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.DETACHMENT_VIEW, self.loadViewByCtxEvent), (VIEW_ALIAS.DETACHMENT_MOBILIZATION_VIEW, self.loadViewByCtxEvent), (DETACHMENT_ALIASES.MOBILIZATION_VEHICLE_SELECT_POPOVER, self.loadViewByCtxEvent))
        super(_DetachmentBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
