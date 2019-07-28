# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.event_hangar.event_hangar_page import EventHangarPage
    from gui.Scaleform.daapi.view.lobby.manual.event_manual_chapter_view import EventManualChapterView
    from gui.Scaleform.daapi.view.lobby.event_hangar.event_general_progress_page import EventGeneralProgressPage
    from gui.Scaleform.daapi.view.lobby.event_hangar.event_general_dialog import EventGeneralDialog
    return (ViewSettings(VIEW_ALIAS.EVENT_HANGAR_PAGE, EventHangarPage, 'eventPage.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.EVENT_HANGAR_PAGE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_MANUAL_PAGE, EventManualChapterView, 'eventManualView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.EVENT_MANUAL_PAGE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_GENERAL_PROGRESS_PAGE, EventGeneralProgressPage, 'eventGeneralProgress.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.EVENT_GENERAL_PROGRESS_PAGE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_GENERAL_DIALOG, EventGeneralDialog, 'eventGeneralDialog.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.EVENT_GENERAL_DIALOG, ScopeTemplates.LOBBY_SUB_SCOPE))


def getEventHangarSoundsConfig(manager):
    from skeletons.gui.event_hangar_sound_controller import IEventHangarSoundController
    from gui.Scaleform.daapi.view.lobby.event_hangar.event_sound_controller import EventHangarSoundController
    instance = EventHangarSoundController()
    manager.addInstance(IEventHangarSoundController, instance, finalizer='fini')


def getBusinessHandlers():
    return (EventHangarPackageBusinessHandler(),)


class EventHangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENT_HANGAR_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_MANUAL_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_GENERAL_PROGRESS_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_GENERAL_DIALOG, self.loadViewByCtxEvent))
        super(EventHangarPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
