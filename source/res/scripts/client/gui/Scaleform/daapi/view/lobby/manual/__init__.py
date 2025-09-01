# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/manual/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared import EVENT_BUS_SCOPE
from gui.app_loader import settings as app_settings

def getStateMachineRegistrators():
    from gui.Scaleform.daapi.view.lobby.manual.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.manual.manual_main_view import ManualMainView
    from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
    from gui.Scaleform.daapi.view.lobby.manual.manual_chapter_view import ManualChapterView
    return (ViewSettings(VIEW_ALIAS.WIKI_VIEW, ManualMainView, 'manual.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.WIKI_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.MANUAL_BROWSER_VIEW, WebView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.MANUAL_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ManualChapterView, 'manualChapterView.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True))


def getBusinessHandlers():
    return (ManualPackageBusinessHandler(),)


class ManualPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.WIKI_VIEW, self.loadViewByCtxEvent), (VIEW_ALIAS.MANUAL_CHAPTER_VIEW, self.loadViewByCtxEvent), (VIEW_ALIAS.MANUAL_BROWSER_VIEW, self.loadViewByCtxEvent))
        super(ManualPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
