# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_missions/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.user_missions.user_missions_hub_container_view import UserMissionsHubContainerView
from gui.Scaleform.daapi.view.lobby.user_missions.user_missions_hub_content_inject import UserMissionsHubContentInject
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.USERMISSSIONS_ALIASES import USERMISSSIONS_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getStateMachineRegistrators():
    from gui.Scaleform.daapi.view.lobby.user_missions.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(VIEW_ALIAS.USER_MISSIONS_HUB_CONTAINER, UserMissionsHubContainerView, 'userMissionsHubContainer.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.USER_MISSIONS_HUB_CONTAINER, ScopeTemplates.LOBBY_SUB_SCOPE), ComponentSettings(USERMISSSIONS_ALIASES.USER_MISSIONS_HUB_CONTENT_INJECT, UserMissionsHubContentInject, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (UserMissionsHubPackageBusinessHandler(),)


class UserMissionsHubPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.USER_MISSIONS_HUB_CONTAINER, self.loadViewByCtxEvent),)
        super(UserMissionsHubPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
