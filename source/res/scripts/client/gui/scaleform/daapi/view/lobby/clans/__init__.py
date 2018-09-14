# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/__init__.py
from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileFortificationInfoView import ClanProfileFortificationInfoView
from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileFortificationPromoView import ClanProfileFortificationPromoView
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.clans.invites.ClanPersonalInvitesView import ClanPersonalInvitesView
    from gui.Scaleform.daapi.view.lobby.clans.invites.ClanPersonalInvitesWindow import ClanPersonalInvitesWindow
    from gui.Scaleform.daapi.view.lobby.clans.invites.ClanSendInvitesWindow import ClanSendInvitesWindow
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileGlobalMapInfoView import ClanProfileGlobalMapInfoView
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileGlobalMapPromoView import ClanProfileGlobalMapPromoView
    from gui.Scaleform.daapi.view.lobby.clans.search.ClanSearchInfo import ClanSearchInfo
    from gui.Scaleform.daapi.view.lobby.clans.search.ClanSearchWindow import ClanSearchWindow
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileFortificationView import ClanProfileFortificationView
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileGlobalMapView import ClanProfileGlobalMapView
    from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesView import ClanInvitesView
    from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesWindow import ClanInvitesWindow
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileMainWindow import ClanProfileMainWindow
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfilePersonnelView import ClanProfilePersonnelView
    from gui.Scaleform.daapi.view.lobby.clans.invites.ClanRequestsView import ClanRequestsView
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileSummaryView import ClanProfileSummaryView
    from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileTableStatisticsView import ClanProfileTableStatisticsView
    return (GroupedViewSettings(CLANS_ALIASES.CLAN_PROFILE_MAIN_WINDOW_PY, ClanProfileMainWindow, CLANS_ALIASES.CLAN_PROFILE_MAIN_WINDOW_UI, ViewTypes.WINDOW, '', CLANS_ALIASES.CLAN_PROFILE_MAIN_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CLANS_ALIASES.CLAN_PROFILE_INVITES_WINDOW_PY, ClanInvitesWindow, 'clanInvitesWindow.swf', ViewTypes.WINDOW, CLANS_ALIASES.CLAN_PROFILE_INVITES_WINDOW_PY, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(CLANS_ALIASES.CLAN_PROFILE_SEND_INVITES_WINDOW_PY, ClanSendInvitesWindow, 'sendInvitesWindow.swf', ViewTypes.WINDOW, '', CLANS_ALIASES.CLAN_PROFILE_SEND_INVITES_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_PY, ClanPersonalInvitesWindow, CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_UI, ViewTypes.WINDOW, CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_PY, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_SUMMARY_VIEW_ALIAS, ClanProfileSummaryView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_PERSONNEL_VIEW_ALIAS, ClanProfilePersonnelView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_FORTIFICATION_VIEW_ALIAS, ClanProfileFortificationView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_GLOBALMAP_VIEW_ALIAS, ClanProfileGlobalMapView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_GLOBALMAP_PROMO_VIEW_ALIAS, ClanProfileGlobalMapPromoView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_GLOBALMAP_INFO_VIEW_ALIAS, ClanProfileGlobalMapInfoView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_FORT_PROMO_VIEW_ALIAS, ClanProfileFortificationPromoView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_FORT_INFO_VIEW_ALIAS, ClanProfileFortificationInfoView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, ClanRequestsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, ClanInvitesView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PROFILE_TABLE_STATISTICS_VIEW_ALIAS, ClanProfileTableStatisticsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_PERSONAL_INVITES_VIEW_ALIAS, ClanPersonalInvitesView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(CLANS_ALIASES.CLAN_SEARCH_WINDOW_PY, ClanSearchWindow, 'clanSearchWindow.swf', ViewTypes.WINDOW, CLANS_ALIASES.CLAN_SEARCH_WINDOW_PY, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(CLANS_ALIASES.CLAN_SEARCH_INFO_PY, ClanSearchInfo, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_ClanProfileBusinessHandler(),)


class _ClanProfileBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((CLANS_ALIASES.CLAN_PROFILE_MAIN_WINDOW_PY, self.loadViewByCtxEvent),
         (CLANS_ALIASES.CLAN_PROFILE_INVITES_WINDOW_PY, self.loadViewByCtxEvent),
         (CLANS_ALIASES.CLAN_PROFILE_SEND_INVITES_WINDOW_PY, self.loadViewByCtxEvent),
         (CLANS_ALIASES.CLAN_SEARCH_WINDOW_PY, self.loadViewByCtxEvent),
         (CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_PY, self.loadViewByCtxEvent))
        super(_ClanProfileBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
