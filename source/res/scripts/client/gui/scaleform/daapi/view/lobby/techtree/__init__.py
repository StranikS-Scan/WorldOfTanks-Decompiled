# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE, g_eventBus

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.techtree.research_cm_handlers import ResearchVehicleContextMenuHandler, ResearchItemContextMenuHandler, BlueprintVehicleContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.RESEARCH_VEHICLE, ResearchVehicleContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.RESEARCH_ITEM, ResearchItemContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.BLUEPRINT_VEHICLE, BlueprintVehicleContextMenuHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.techtree.research_page import Research
    from gui.Scaleform.daapi.view.lobby.techtree.techtree_page import TechTree
    return (ViewSettings(VIEW_ALIAS.LOBBY_TECHTREE, TechTree, 'techtree.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_TECHTREE, ScopeTemplates.LOBBY_SUB_SCOPE, True), ViewSettings(VIEW_ALIAS.LOBBY_RESEARCH, Research, 'research.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_RESEARCH, ScopeTemplates.LOBBY_SUB_SCOPE, True))


def getBusinessHandlers():
    return (_TechTreePackageBusinessHandler(),)


class _TechTreePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_TECHTREE, self.__loadTechTree), (VIEW_ALIAS.LOBBY_RESEARCH, self.__loadResearch), (VIEW_ALIAS.EXIT_FROM_RESEARCH, self.__exitFromResearch))
        super(_TechTreePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
        self.__exitEvent = None
        return

    def __loadTechTree(self, event):
        self.loadViewWithDefName(VIEW_ALIAS.LOBBY_TECHTREE, ctx=event.ctx)

    def __loadResearch(self, event):
        ctx = event.ctx
        self.__exitEvent = ctx.get('exit')
        self.loadViewWithDefName(VIEW_ALIAS.LOBBY_RESEARCH, ctx=ctx)

    def __exitFromResearch(self, _):
        if self.__exitEvent is not None:
            g_eventBus.handleEvent(self.__exitEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        return
