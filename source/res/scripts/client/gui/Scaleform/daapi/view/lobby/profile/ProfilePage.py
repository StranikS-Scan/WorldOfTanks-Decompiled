# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfilePage.py
import BigWorld
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofTabCounter, isHofButtonNew, showDisabledDialog
from gui.Scaleform.daapi.view.meta.ProfileMeta import ProfileMeta
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.sounds.ambients import LobbySubViewEnv
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.daapi.view.lobby.profile.sound_constants import ACHIEVEMENTS_SOUND_SPACE

class ProfilePage(LobbySubView, ProfileMeta):
    __sound_env__ = LobbySubViewEnv
    lobbyContext = dependency.descriptor(ILobbyContext)
    _COMMON_SOUND_SPACE = ACHIEVEMENTS_SOUND_SPACE

    def __init__(self, ctx=None):
        self.__ctx = ctx
        LobbySubView.__init__(self)
        self.__tabNavigator = None
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == VIEW_ALIAS.PROFILE_TAB_NAVIGATOR:
            player = BigWorld.player()
            super(ProfilePage, self).registerFlashComponent(component, alias, player.name, None, player.databaseID, self.__getSectionsData(), self.__ctx)
        else:
            super(ProfilePage, self).registerFlashComponent(component, alias)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ProfilePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.PROFILE_TAB_NAVIGATOR:
            self.__tabNavigator = viewPy
            g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
            self.__updateTabCounters()

    def onCloseProfile(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(ProfilePage, self)._populate()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__tabNavigator = None
        super(ProfilePage, self)._dispose()
        return

    def __dossierUpdateCallBack(self, _):
        self.__tabNavigator.invokeUpdate()

    def __getSectionsData(self):
        isHofEnabled = self.__isHofEnabled
        if self.__tabNavigator:
            selectedAlias = self.__tabNavigator.tabId
        else:
            selectedAlias = self.__ctx.get('selectedAlias')
        if selectedAlias is None or selectedAlias == VIEW_ALIAS.PROFILE_HOF and not isHofEnabled:
            itemCD = self.__ctx.get('itemCD')
            selectedAlias = VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE if itemCD else VIEW_ALIAS.PROFILE_SUMMARY_PAGE
        sectionsData = [(PROFILE.SECTION_SUMMARY_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_SUMMARY,
          VIEW_ALIAS.PROFILE_SUMMARY_PAGE,
          True),
         (PROFILE.SECTION_AWARDS_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_AWARDS,
          VIEW_ALIAS.PROFILE_AWARDS,
          True),
         (PROFILE.SECTION_STATISTICS_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_STATISTICS,
          VIEW_ALIAS.PROFILE_STATISTICS,
          True),
         (PROFILE.SECTION_TECHNIQUE_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_TECHNIQUE,
          VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE,
          True)]
        if isHofEnabled:
            sectionsData.append((PROFILE.SECTION_HOF_TITLE,
             PROFILE.PROFILE_TABS_TOOLTIP_HOF,
             VIEW_ALIAS.PROFILE_HOF,
             True))
        return {'sectionsData': [ {'label': makeString(label),
                          'tooltip': tooltip,
                          'alias': alias,
                          'enabled': isEnabled} for label, tooltip, alias, isEnabled in sectionsData ],
         'selectedAlias': selectedAlias}

    @property
    def __isHofEnabled(self):
        return self.lobbyContext.getServerSettings().isHofEnabled()

    def __onServerSettingChanged(self, diff):
        if 'hallOfFame' in diff:
            if self.__ctx:
                self.__ctx.pop('itemCD', None)
            self.__tabNavigator.as_setInitDataS(self.__getSectionsData())
            self.__updateTabCounters()
            if not self.__isHofEnabled:
                showDisabledDialog()
        return

    def __updateTabCounters(self):
        if self.__isHofEnabled:
            counters = []
            hofCounter = getHofTabCounter()
            if hofCounter:
                counters.append({'componentId': VIEW_ALIAS.PROFILE_HOF,
                 'count': str(hofCounter)})
            if isHofButtonNew(PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON):
                counters.append({'componentId': VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE,
                 'count': '1'})
            self.__tabNavigator.as_setBtnTabCountersS(counters)
        else:
            self.__tabNavigator.as_setBtnTabCountersS([])
