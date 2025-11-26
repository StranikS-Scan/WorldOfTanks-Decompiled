# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/__init__.py
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.impl.lobby.pet_system.event_view import EventViewWindow
from gui.impl.lobby.pet_system.fullscreen_event_view import FullscreenEventViewWindow
from gui.impl.lobby.pet_system.pet_storage_view import PetStorageViewWindow
from gui.shared import EVENT_BUS_SCOPE

def getStateMachineRegistrators():
    from gui.impl.lobby.pet_system.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    return (ViewSettings(VIEW_ALIAS.PET_STORAGE, PetStorageViewWindow, '', WindowLayer.SUB_VIEW, VIEW_ALIAS.PET_STORAGE, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.PET_EVENT, EventViewWindow, '', WindowLayer.WINDOW, VIEW_ALIAS.PET_EVENT, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.PET_EVENT_FULLSCREEN, FullscreenEventViewWindow, '', WindowLayer.SUB_VIEW, VIEW_ALIAS.PET_EVENT_FULLSCREEN, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (PetSystemBusinessHandler(),)


class PetSystemBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.PET_STORAGE, self.loadViewByCtxEvent), (VIEW_ALIAS.PET_EVENT, self.loadViewByCtxEvent), (VIEW_ALIAS.PET_EVENT_FULLSCREEN, self.loadViewByCtxEvent))
        super(PetSystemBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


def getContextMenuHandlers():
    pass
