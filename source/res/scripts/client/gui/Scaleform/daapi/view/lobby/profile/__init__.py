# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/__init__.py
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.profile import profile_cm_handlers
    return ((CONTEXT_MENU_HANDLER_TYPE.PROFILE_VEHICLE, profile_cm_handlers.ProfileVehicleCMHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.profile.ProfileAwards import ProfileAwards
    from gui.Scaleform.daapi.view.lobby.profile.ProfilePage import ProfilePage
    from gui.Scaleform.daapi.view.lobby.profile.ProfileStatistics import ProfileStatistics
    from gui.Scaleform.daapi.view.lobby.profile.ProfileSummaryPage import ProfileSummaryPage
    from gui.Scaleform.daapi.view.lobby.profile.ProfileSummaryWindow import ProfileSummaryWindow
    from gui.Scaleform.daapi.view.lobby.profile.ProfileTabNavigator import ProfileTabNavigator
    from gui.Scaleform.daapi.view.lobby.profile.ProfileTechniquePage import ProfileTechniquePage
    from gui.Scaleform.daapi.view.lobby.profile.ProfileTechniqueWindow import ProfileTechniqueWindow
    from gui.Scaleform.daapi.view.lobby.profile.ProfileWindow import ProfileWindow
    from gui.Scaleform.daapi.view.lobby.profile.ProfileHof import ProfileHof
    return (ViewSettings(VIEW_ALIAS.LOBBY_PROFILE, ProfilePage, 'profile.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_PROFILE, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PROFILE_WINDOW, ProfileWindow, 'profileWindow.swf', ViewTypes.WINDOW, 'profileWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_AWARDS, ProfileAwards, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_STATISTICS, ProfileStatistics, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_SUMMARY_PAGE, ProfileSummaryPage, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_SUMMARY_WINDOW, ProfileSummaryWindow, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_TAB_NAVIGATOR, ProfileTabNavigator, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE, ProfileTechniquePage, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_TECHNIQUE_WINDOW, ProfileTechniqueWindow, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.PROFILE_HOF, ProfileHof, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (ProfilePackageBusinessHandler(),)


class ProfilePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_PROFILE, self.loadViewByCtxEvent), (VIEW_ALIAS.PROFILE_WINDOW, self.loadViewByCtxEvent))
        super(ProfilePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
