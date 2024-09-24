# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from story_mode.gui.impl.lobby.web_view import StoryModeWebViewTransparent
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS

def getContextMenuHandlers():
    pass


def getViewSettings():
    from story_mode.gui.scaleform.daapi.view.lobby.story_mode_event_entry_point_view import StoryModeEventEntryPointView
    from story_mode.gui.scaleform.daapi.view.lobby.story_mode_newbie_entry_point_view import StoryModeNewbieEntryPointView
    return (ViewSettings(VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, StoryModeWebViewTransparent, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, ScopeTemplates.LOBBY_SUB_SCOPE), ComponentSettings(VIEW_ALIAS.STORY_MODE_EVENT_ENTRY_POINT, StoryModeEventEntryPointView, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(VIEW_ALIAS.STORY_MODE_NEWBIE_ENTRY_POINT, StoryModeNewbieEntryPointView, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (StoryModePackageBusinessHandler(),)


class StoryModePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, self.loadViewByCtxEvent),)
        super(StoryModePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
