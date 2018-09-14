# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfilePage.py
import BigWorld
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ProfileMeta import ProfileMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers.i18n import makeString

class ProfilePage(LobbySubView, ProfileMeta):

    def __init__(self, ctx = None):
        self.__ctx = ctx
        LobbySubView.__init__(self)
        self.__tabNavigator = None
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == VIEW_ALIAS.PROFILE_TAB_NAVIGATOR:
            player = BigWorld.player()
            selectedAlias = VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE if self.__ctx.get('itemCD') else VIEW_ALIAS.PROFILE_SUMMARY_PAGE
            super(ProfilePage, self).registerFlashComponent(component, alias, player.name, None, player.databaseID, {'sectionsData': [self.__getSectionDataObject(PROFILE.SECTION_SUMMARY_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_SUMMARY, VIEW_ALIAS.PROFILE_SUMMARY_PAGE),
                              self.__getSectionDataObject(PROFILE.SECTION_AWARDS_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_AWARDS, VIEW_ALIAS.PROFILE_AWARDS),
                              self.__getSectionDataObject(PROFILE.SECTION_STATISTICS_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_STATISTICS, VIEW_ALIAS.PROFILE_STATISTICS),
                              self.__getSectionDataObject(PROFILE.SECTION_TECHNIQUE_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_TECHNIQUE, VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE)],
             'selectedAlias': selectedAlias}, self.__ctx)
        else:
            super(ProfilePage, self).registerFlashComponent(component, alias)
        return

    def __dossierUpdateCallBack(self, dif):
        self.__tabNavigator.invokeUpdate()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ProfilePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.PROFILE_TAB_NAVIGATOR:
            self.__tabNavigator = viewPy
            g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})

    def __getSectionDataObject(self, label, tooltip, alias):
        return {'label': makeString(label),
         'alias': alias,
         'tooltip': tooltip}

    def onCloseProfile(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__tabNavigator = None
        super(ProfilePage, self)._dispose()
        return
