# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.techtree.research_cm_handlers import ResearchVehicleContextMenuHandler, ResearchItemContextMenuHandler, BlueprintVehicleContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.RESEARCH_VEHICLE, ResearchVehicleContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.RESEARCH_ITEM, ResearchItemContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.BLUEPRINT_VEHICLE, BlueprintVehicleContextMenuHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.techtree.research_page import Research
    from gui.impl.lobby.tech_tree.tech_tree_view import TechTreeWindow
    return (ViewSettings(VIEW_ALIAS.LOBBY_TECHTREE, TechTreeWindow, '', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_TECHTREE, ScopeTemplates.LOBBY_SUB_SCOPE, True), ViewSettings(VIEW_ALIAS.LOBBY_RESEARCH, Research, 'research.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_RESEARCH, ScopeTemplates.LOBBY_SUB_SCOPE, True))


def getBusinessHandlers():
    return (_TechTreePackageBusinessHandler(),)


def getStateMachineRegistrators():
    from gui.Scaleform.daapi.view.lobby.techtree.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


class _TechTreePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_TECHTREE, self.loadViewByCtxEvent), (VIEW_ALIAS.LOBBY_RESEARCH, self.loadViewByCtxEvent))
        super(_TechTreePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
