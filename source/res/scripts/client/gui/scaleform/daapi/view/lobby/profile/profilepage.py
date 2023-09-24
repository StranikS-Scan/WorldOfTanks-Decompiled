# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfilePage.py
import logging
import BigWorld
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofTabCounter, isHofButtonNew, showDisabledDialog
from gui.Scaleform.daapi.view.meta.ProfileMeta import ProfileMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.collection.account_settings import getCollectionsTabCounter
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.game_control import IAchievements20Controller, ILimitedUIController, ICollectionsSystemController
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.daapi.view.lobby.profile.sound_constants import ACHIEVEMENTS_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.hof.web_handlers import createHofWebHandlers
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofDisabledKeys, onServerSettingsChange
from gui.shared.events import ProfilePageEvent, CollectionsEvent
_logger = logging.getLogger(__name__)

class ProfilePage(LobbySubView, ProfileMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    _limitedUIController = dependency.descriptor(ILimitedUIController)
    __achievements20Controller = dependency.descriptor(IAchievements20Controller)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
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
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def updateSubView(self, ctx):
        selectedAlias = ctx.get('selectedAlias')
        if selectedAlias is None:
            _logger.error('Should be specified "selectedAlias"')
            return
        else:
            self.__ctx.update(ctx)
            self.__tabNavigator.as_setInitDataS(self.__getSectionsData(resetSelectedAlias=True))
            if selectedAlias == VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE:
                techniquePage = self.__tabNavigator.components.get(VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE)
                if techniquePage:
                    techniquePage.updateView(ctx)
            return

    def _populate(self):
        super(ProfilePage, self)._populate()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__collectionsSystem.onServerSettingsChanged += self.__onCollectionsSettingsChanged
        self.__achievements20Controller.onUpdate += self.__onProfileVisited
        g_eventBus.addListener(CollectionsEvent.TAB_COUNTER_UPDATED, self.__onCollectionTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        if self.__ctx and self.__ctx.get('hofPageUrl'):
            self.__loadHofUrl(self.__ctx.get('hofPageUrl'))

    def _invalidate(self, *args, **kwargs):
        super(ProfilePage, self)._invalidate(*args, **kwargs)
        if args[0] and args[0].get('hofPageUrl'):
            self.__loadHofUrl(args[0].get('hofPageUrl'))

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__collectionsSystem.onServerSettingsChanged -= self.__onCollectionsSettingsChanged
        self.__achievements20Controller.onUpdate -= self.__onProfileVisited
        g_eventBus.removeListener(CollectionsEvent.TAB_COUNTER_UPDATED, self.__onCollectionTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.__tabNavigator = None
        super(ProfilePage, self)._dispose()
        return

    def __dossierUpdateCallBack(self, _):
        self.__tabNavigator.invokeUpdate()

    def __getSectionsData(self, resetSelectedAlias=False):
        isHofEnabled = self.__isHofEnabled
        if self.__tabNavigator and not resetSelectedAlias:
            selectedAlias = self.__tabNavigator.tabId
        else:
            selectedAlias = self.__ctx.get('selectedAlias')
        itemCD = None
        if selectedAlias is None or selectedAlias == VIEW_ALIAS.PROFILE_HOF and not isHofEnabled:
            itemCD = self.__ctx.get('itemCD')
            selectedAlias = VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE if itemCD else VIEW_ALIAS.PROFILE_SUMMARY_PAGE
        if itemCD is None and not (self.__ctx and self.__ctx.get('selectedAlias')):
            event = ProfilePageEvent(ProfilePageEvent.SELECT_PROFILE_ALIAS)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
            selectedAlias = event.ctx.get('selectedAlias', selectedAlias)
        sectionsData = [(PROFILE.SECTION_SUMMARY_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_SUMMARY,
          VIEW_ALIAS.PROFILE_TOTAL_PAGE,
          True,
          'statsSummary'),
         (PROFILE.SECTION_AWARDS_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_AWARDS,
          VIEW_ALIAS.PROFILE_AWARDS,
          True,
          'statsAwards'),
         (PROFILE.SECTION_STATISTICS_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_STATISTICS,
          VIEW_ALIAS.PROFILE_STATISTICS,
          True,
          'statsStatistics'),
         (PROFILE.SECTION_TECHNIQUE_TITLE,
          PROFILE.PROFILE_TABS_TOOLTIP_TECHNIQUE,
          VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE,
          True,
          'statsTechnique')]
        if isHofEnabled:
            sectionsData.append((PROFILE.SECTION_HOF_TITLE,
             PROFILE.PROFILE_TABS_TOOLTIP_HOF,
             VIEW_ALIAS.PROFILE_HOF,
             True,
             'statsHof'))
        if self.__collectionsSystem.isEnabled():
            sectionsData.append((PROFILE.SECTION_COLLECTIONS_TITLE,
             PROFILE.PROFILE_TABS_TOOLTIP_COLLECTIONS,
             VIEW_ALIAS.PROFILE_COLLECTIONS_PAGE,
             True,
             'statsCollections'))
        return {'sectionsData': [ {'label': makeString(label),
                          'tooltip': tooltip,
                          'alias': alias,
                          'enabled': isEnabled,
                          'id': uiId} for label, tooltip, alias, isEnabled, uiId in sectionsData ],
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

    def __onCollectionsSettingsChanged(self):
        self.__tabNavigator.as_setInitDataS(self.__getSectionsData())
        self.__updateTabCounters()

    def __updateTabCounters(self):
        counters = []
        if self.__achievements20Controller.getAchievementsTabCounter():
            counters.append({'componentId': VIEW_ALIAS.PROFILE_TOTAL_PAGE,
             'count': '1'})
        if self.__isHofEnabled:
            hofCounter = getHofTabCounter()
            if hofCounter and self._limitedUIController.isRuleCompleted(LuiRules.PROFILE_HOF):
                counters.append({'componentId': VIEW_ALIAS.PROFILE_HOF,
                 'count': str(hofCounter)})
            if isHofButtonNew(PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON) and self._limitedUIController.isRuleCompleted(LuiRules.PROFILE_TECHNIQUE_PAGE):
                counters.append({'componentId': VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE,
                 'count': '1'})
        if self.__collectionsSystem.isEnabled() and getCollectionsTabCounter(collectionsSystem=self.__collectionsSystem):
            counters.append({'componentId': VIEW_ALIAS.PROFILE_COLLECTIONS_PAGE,
             'count': ' '})
        self.__tabNavigator.as_setBtnTabCountersS(counters)

    def __loadHofUrl(self, url):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BROWSER_VIEW), ctx={'url': url,
         'returnAlias': VIEW_ALIAS.LOBBY_PROFILE,
         'allowRightClick': True,
         'webHandlers': createHofWebHandlers(),
         'selectedAlias': VIEW_ALIAS.PROFILE_HOF,
         'disabledKeys': getHofDisabledKeys(),
         'onServerSettingsChange': onServerSettingsChange}), EVENT_BUS_SCOPE.LOBBY)

    def __onProfileVisited(self):
        self.__updateTabCounters()

    def __onCollectionTabUpdated(self, *_):
        self.__updateTabCounters()
