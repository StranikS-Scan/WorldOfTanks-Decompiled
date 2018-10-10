# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/linked_set/__init__.py
from gui.Scaleform.daapi.view.lobby.missions.linked_set.linkedset_vehicle_list_popup import LinkedSetVehicleListPopup
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.LINKEDSET_ALIASES import LINKEDSET_ALIASES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.missions.linked_set.linkedset_details_container_view import LinkedSetDetailsView
    from gui.Scaleform.daapi.view.lobby.missions.linked_set.linkedset_details_overlay import LinkedSetDetailsOverlay
    from gui.Scaleform.daapi.view.lobby.missions.linked_set.linkedset_hints import LinkedSetHintsView
    return (ViewSettings(LINKEDSET_ALIASES.LINKED_SET_DETAILS_CONTAINER_VIEW, LinkedSetDetailsView, 'linkedSetDetails.swf', ViewTypes.LOBBY_TOP_SUB, LINKEDSET_ALIASES.LINKED_SET_DETAILS_CONTAINER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(LINKEDSET_ALIASES.LINKED_SET_DETAILS_VIEW_ALIAS, LinkedSetDetailsOverlay, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LINKEDSET_HINTS, LinkedSetHintsView, 'linkedSetHints.swf', ViewTypes.OVERLAY, VIEW_ALIAS.LINKEDSET_HINTS, ScopeTemplates.OVERLAY_SCOPE, True),
     GroupedViewSettings(LINKEDSET_ALIASES.LINKED_SET_VEHICLE_LIST_POPUP_PY, LinkedSetVehicleListPopup, LINKEDSET_ALIASES.LINKED_SET_VEHICLE_LIST_POPUP_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True, isModal=True))


def getBusinessHandlers():
    return (LinkedsetBusinessHandler(),)


class LinkedsetBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((LINKEDSET_ALIASES.LINKED_SET_DETAILS_CONTAINER_VIEW, self.loadViewByCtxEvent), (VIEW_ALIAS.LINKEDSET_HINTS, self.loadViewByCtxEvent), (LINKEDSET_ALIASES.LINKED_SET_VEHICLE_LIST_POPUP_PY, self.loadViewByCtxEvent))
        super(LinkedsetBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
