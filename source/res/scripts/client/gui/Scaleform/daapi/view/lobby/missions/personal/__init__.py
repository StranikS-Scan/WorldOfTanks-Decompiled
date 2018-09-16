# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/__init__.py
from operator import methodcaller
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_award_congratulation_view import PersonalMissionAwardCongratulationView
from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_first_entry_award_view import PersonalMissionFirstEntryAwardView
from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_first_entry_view import PersonalMissionFirstEntryView
from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_operations_page import PersonalMissionOperationsPage
from gui.Scaleform.daapi.view.lobby.missions.personal.tank_girls_popover import TankgirlsPopover
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.app_loader import settings as app_settings
from gui.server_events.pm_constants import FIRST_ENTRY_STATE as _FES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from helpers import dependency
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_map_view import PersonalMissionsMapView
    from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_page import PersonalMissionsPage
    from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_awards_view import PersonalMissionsAwardsView
    from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_details_container_view import PersonalMissionDetailsContainerView
    from gui.Scaleform.daapi.view.lobby.missions.personal.free_sheet_popover import FreeSheetPopover
    return (ViewSettings(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS, PersonalMissionOperationsPage, 'personalMissionOperationsPage.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, PersonalMissionsPage, 'personalMissionsPage.swf', ViewTypes.LOBBY_SUB, PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_MAP_VIEW_ALIAS, PersonalMissionsMapView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS, PersonalMissionsAwardsView, 'personalMissionsAwardsView.swf', ViewTypes.LOBBY_SUB, PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS, PersonalMissionFirstEntryView, 'personalMissionFirstEntryView.swf', ViewTypes.LOBBY_SUB, PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS, PersonalMissionDetailsContainerView, 'personalMissionDetails.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_AWARD_VIEW_ALIAS, PersonalMissionFirstEntryAwardView, 'personalMissionFirstEntryAwardView.swf', ViewTypes.LOBBY_SUB, PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_AWARD_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_AWARD_CONGRATULATION_VIEW_ALIAS, PersonalMissionAwardCongratulationView, 'personalMissionAwardCongratulationView.swf', ViewTypes.OVERLAY, PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_AWARD_CONGRATULATION_VIEW_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE),
     GroupedViewSettings(PERSONAL_MISSIONS_ALIASES.FREE_SHEET_POPOVER, FreeSheetPopover, 'freeSheetPopoverView.swf', ViewTypes.WINDOW, PERSONAL_MISSIONS_ALIASES.FREE_SHEET_POPOVER, PERSONAL_MISSIONS_ALIASES.FREE_SHEET_POPOVER, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(PERSONAL_MISSIONS_ALIASES.TANK_GIRLS_POPOVER, TankgirlsPopover, 'tankgirlsPopoverView.swf', ViewTypes.WINDOW, PERSONAL_MISSIONS_ALIASES.TANK_GIRLS_POPOVER, PERSONAL_MISSIONS_ALIASES.TANK_GIRLS_POPOVER, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (PersonalMissionsPackageBusinessHandler(),)


class PersonalMissionsPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS, self.loadPersonalMissionsView),
         (VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS, self.loadViewByCtxEvent),
         (PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, self.loadPersonalMissionsView),
         (PERSONAL_MISSIONS_ALIASES.FREE_SHEET_POPOVER, self.loadViewByCtxEvent),
         (PERSONAL_MISSIONS_ALIASES.TANK_GIRLS_POPOVER, self.loadViewByCtxEvent),
         (PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS, self.loadAwardsView),
         (PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS, self.loadViewByCtxEvent),
         (PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_AWARD_VIEW_ALIAS, self.loadViewByCtxEvent),
         (PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_AWARD_CONGRATULATION_VIEW_ALIAS, self.loadViewByCtxEvent))
        super(PersonalMissionsPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def loadAwardsView(self, event):
        preloadOperationsPage = event.ctx.get('isBackEvent')
        if preloadOperationsPage:
            Waiting.show('loadPage')
            self.loadViewByCtxEvent(LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS, ctx=event.ctx))
        self.loadViewByCtxEvent(event)
        if preloadOperationsPage:
            Waiting.hide('loadPage')

    def loadPersonalMissionsView(self, event):
        settingsCore = dependency.instance(ISettingsCore)
        eventsCache = dependency.instance(IEventsCache)
        firstEntryState = settingsCore.serverSettings.getPersonalMissionsFirstEntryState()
        goByDefault = True
        if firstEntryState == _FES.NOT_VISITED:
            self.loadViewByCtxEvent(LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS, ctx=event.ctx))
            goByDefault = False
        elif firstEntryState == _FES.TUTORIAL_WAS_SHOWN:
            if findFirst(methodcaller('isAwardAchieved'), eventsCache.personalMissions.getOperations().values()):
                self.loadViewByCtxEvent(LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_AWARD_VIEW_ALIAS, ctx=event.ctx))
                goByDefault = False
            else:
                settingsCore.serverSettings.setPersonalMissionsFirstEntryState(_FES.AWARDS_WAS_SHOWN)
        if goByDefault:
            self.loadViewByCtxEvent(event)
