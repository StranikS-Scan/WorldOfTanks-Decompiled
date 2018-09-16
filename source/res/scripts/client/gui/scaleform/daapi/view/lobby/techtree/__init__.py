# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ConditionalViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LoadEvent
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.techtree.research_cm_handlers import ResearchVehicleContextMenuHandler, ResearchItemContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCResearchVehicleContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCResearchItemContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.RESEARCH_VEHICLE, BootcampComponentOverride(ResearchVehicleContextMenuHandler, BCResearchVehicleContextMenuHandler)), (CONTEXT_MENU_HANDLER_TYPE.RESEARCH_ITEM, BootcampComponentOverride(ResearchItemContextMenuHandler, BCResearchItemContextMenuHandler)))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.techtree.research_page import Research
    from gui.Scaleform.daapi.view.lobby.techtree.techtree_page import TechTree
    from gui.Scaleform.daapi.view.bootcamp.BCTechTree import BCTechTree
    from gui.Scaleform.daapi.view.bootcamp.BCResearch import BCResearch
    return (ConditionalViewSettings(VIEW_ALIAS.LOBBY_TECHTREE, BootcampComponentOverride(TechTree, BCTechTree), 'techtree.swf', ViewTypes.LOBBY_SUB, None, VIEW_ALIAS.LOBBY_TECHTREE, ScopeTemplates.DEFAULT_SCOPE, True), ConditionalViewSettings(VIEW_ALIAS.LOBBY_RESEARCH, BootcampComponentOverride(Research, BCResearch), 'research.swf', ViewTypes.LOBBY_SUB, None, VIEW_ALIAS.LOBBY_RESEARCH, ScopeTemplates.DEFAULT_SCOPE, True))


def getBusinessHandlers():
    return (_TechTreePackageBusinessHandler(),)


class _TechTreePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_TECHTREE, self.__loadTechTree), (VIEW_ALIAS.LOBBY_RESEARCH, self.__loadResearch), (LoadEvent.EXIT_FROM_RESEARCH, self.__exitFromResearch))
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
