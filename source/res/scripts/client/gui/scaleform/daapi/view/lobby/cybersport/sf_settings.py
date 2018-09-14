# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/sf_settings.py
from gui.Scaleform.daapi.view.lobby.cyberSport.StaticFormationUnitView import StaticFormationUnitView
from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportRespawnForm import CyberSportRespawnForm
from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportRespawnView import CyberSportRespawnView
from gui.Scaleform.daapi.view.lobby.cyberSport.RosterSlotSettingsWindow import RosterSlotSettingsWindow
from gui.Scaleform.daapi.view.lobby.cyberSport.StaticFormationInvitesAndRequestsWindow import StaticFormationInvitesAndRequestsWindow
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubProfileWindow
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubStaffView import ClubStaffView
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubSummaryView import ClubSummaryView
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubStatsView import ClubStatsView
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubLadderView import ClubLadderView
from gui.Scaleform.daapi.view.lobby.cyberSport.VehicleSelectorPopup import VehicleSelectorPopup
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ViewSettings, ScopeTemplates
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportMainWindow import CyberSportMainWindow
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportIntroView import CyberSportIntroView
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportUnitsListView import CyberSportUnitsListView
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportClubsListView import CyberSportClubsListView
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportUnitView import CyberSportUnitView
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportSendInvitesWindow import CyberSportSendInvitesWindow
    from gui.Scaleform.daapi.view.dialogs.CyberSportDialog import CyberSportDialog
    return [GroupedViewSettings(VIEW_ALIAS.CYBER_SPORT_SEND_INVITES_WINDOW, CyberSportSendInvitesWindow, 'prbSendInvitesWindow.swf', ViewTypes.WINDOW, '', VIEW_ALIAS.CYBER_SPORT_SEND_INVITES_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, CyberSportMainWindow, CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_UI, ViewTypes.WINDOW, '', CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY, RosterSlotSettingsWindow, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY, VehicleSelectorPopup, CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.CYBER_SPORT_DIALOG_PY, CyberSportDialog, CYBER_SPORT_ALIASES.CYBER_SPORT_DIALOG_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.CYBER_SPORT_STATIC_PROFILE_PY, ClubProfileWindow, CYBER_SPORT_ALIASES.CYBER_SPORT_STATIC_PROFILE_UI, ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.STATIC_FORMATION_INVITES_AND_REQUESTS_PY, StaticFormationInvitesAndRequestsWindow, CYBER_SPORT_ALIASES.STATIC_FORMATION_INVITES_AND_REQUESTS_UI, ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     ViewSettings(CYBER_SPORT_ALIASES.CS_RESPAWN_PY, CyberSportRespawnView, CYBER_SPORT_ALIASES.CS_RESPAWN_UI, ViewTypes.LOBBY_SUB, CYBER_SPORT_ALIASES.CS_RESPAWN_PY, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.CS_RESPAWN_FORM, CyberSportRespawnForm, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.INTRO_VIEW_PY, CyberSportIntroView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.UNITS_LIST_VIEW_PY, CyberSportUnitsListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.UNITS_STATICS_LIST_VIEW_PY, CyberSportClubsListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.UNIT_VIEW_PY, CyberSportUnitView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.STATIC_FORMATION_UNIT_VIEW_PY, StaticFormationUnitView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_PY, ClubStaffView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_PY, ClubLadderView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_PY, ClubSummaryView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_PY, ClubStatsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [CyberSportBusinessHandler(), CyberSportDialogsHandler()]


class CyberSportBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(VIEW_ALIAS.CYBER_SPORT_SEND_INVITES_WINDOW, self.__showSimpleWindow),
         (CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, self.__showSimpleWindow),
         (CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY, self.__showSimpleWindow),
         (CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY, self.__showSimpleWindow),
         (CYBER_SPORT_ALIASES.CYBER_SPORT_STATIC_PROFILE_PY, self.__showSimpleWindow),
         (CYBER_SPORT_ALIASES.STATIC_FORMATION_INVITES_AND_REQUESTS_PY, self.__showSimpleWindow),
         (CYBER_SPORT_ALIASES.CS_RESPAWN_PY, self.__showSimpleWindow)]
        super(CyberSportBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __showSimpleWindow(self, event):
        self.app.loadView(event.eventType, event.name, event.ctx)


class CyberSportDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        super(CyberSportDialogsHandler, self).__init__([(ShowDialogEvent.SHOW_CYBER_SPORT_DIALOG, self.__showCyberSportDialog)], EVENT_BUS_SCOPE.DEFAULT)

    def __showCyberSportDialog(self, event):
        self._loadView(CYBER_SPORT_ALIASES.CYBER_SPORT_DIALOG_PY, event.meta, event.handler)
