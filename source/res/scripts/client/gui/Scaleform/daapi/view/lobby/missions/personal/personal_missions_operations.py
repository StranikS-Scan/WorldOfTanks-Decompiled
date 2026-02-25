# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_operations.py
import operator
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PersonalMissions
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import checkOldCampaignsIntroSeen
from gui.Scaleform.daapi.view.meta.PMOldOperationsMeta import PMOldOperationsMeta
from gui.Scaleform.daapi.view.meta.PersonalMissionOperationsMeta import PersonalMissionOperationsMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.optimization_manager import ExternalFullscreenGraphicsOptimizationComponent
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl.lobby.personal_missions.personal_missions_operations_view import PersonalMissionsOperationsView
from gui.impl.lobby.personal_missions.personal_missions_window_events import showIntroVideoView, showIntroView
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import PERSONAL_MISSIONS_SOUND_SPACE
from gui.server_events.pm3_constants import PERSONAL_MISSIONS_3_SOUND_SPACE, SOUNDS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.server_events import IEventsCache
from gui.sounds.voice_over_phrase_player import VoiceOverHandler

class PersonalMissionOperations(LobbySubView, PersonalMissionOperationsMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_3_SOUND_SPACE
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx):
        super(PersonalMissionOperations, self).__init__(ctx)
        self.__graphicOptimization = ExternalFullscreenGraphicsOptimizationComponent()
        self.__voiceHandler = VoiceOverHandler()
        ctx = ctx or {}
        branch = ctx.get('branch')
        if branch:
            self.setBranch(branch)
        operationID = ctx.get('operationID')
        if operationID:
            self.setOperationID(operationID)

    def closeView(self):
        event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR))
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def onTabSelected(self, tabIdx):
        branch = self.__getBranchByTabIndex(tabIdx)
        self.setBranch(branch)
        self._handleCampaignTab(branch)

    def _handleCampaignTab(self, branch):
        if branch == PM_BRANCH.PERSONAL_MISSION_3:
            if self.__isIntroSeenShown():
                self.soundManager.setState(SOUNDS.STATE_SCREEN_GROUP, SOUNDS.STATE_PLACE_SPLIT_SCREEN)
                self.__voiceHandler.createPlayer()
                self._switchCommonSoundSpace(PERSONAL_MISSIONS_3_SOUND_SPACE)
        else:
            self.__voiceHandler.destroyPlayer()
            self._switchCommonSoundSpace(PERSONAL_MISSIONS_SOUND_SPACE)
            checkOldCampaignsIntroSeen()

    def __isIntroSeenShown(self):
        isNotShown = not AccountSettings.getPersonalMissions(PersonalMissions.INTRO_SEEN)
        if isNotShown:
            showIntroView()
            showIntroVideoView()
            return False
        return True

    def _populate(self):
        super(PersonalMissionOperations, self)._populate()
        self.__graphicOptimization.init()
        tabIdx = self.__getTabIndexByBranch()
        self.as_setSelectedTabS(tabIdx)
        self.eventsCache.onPersonalQuestsVisited()

    def _dispose(self):
        self.__voiceHandler.destroyPlayer()
        self.__graphicOptimization.fini()
        super(PersonalMissionOperations, self)._dispose()

    def __getTabIndexByBranch(self):
        return 1 if self.getBranch() < PM_BRANCH.PERSONAL_MISSION_3 else 0

    def __getBranchByTabIndex(self, tabIdx):
        return PM_BRANCH.REGULAR if tabIdx > 0 else PM_BRANCH.PERSONAL_MISSION_3


class PMOldOperations(PMOldOperationsMeta, PersonalMissionsNavigation):
    eventsCache = dependency.descriptor(IEventsCache)

    def _populate(self):
        super(PMOldOperations, self)._populate()
        self.eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self.eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.__setTitle()
        self.__update()

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self.eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        super(PMOldOperations, self)._dispose()

    def showInfo(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onOperationClick(self, branch, operationID):
        self.setBranch(branch)
        self.setOperationID(operationID)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS), ctx={'branch': branch,
         'operationID': operationID}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __update(self):
        operations = []
        timeIconAlreadySet = False
        for branch in PM_BRANCH.OLD_BRANCHES:
            for oID, o in sorted(self.eventsCache.getPersonalMissions().getOperationsForBranch(branch).iteritems(), key=operator.itemgetter(0)):
                state = PERSONAL_MISSIONS_ALIASES.OPERATION_LOCKED_STATE
                tooltipAlias = TOOLTIPS_CONSTANTS.OPERATION
                postponedTime = ''
                enabled = True
                if o.isDisabled():
                    state, postponedTime = missions_helper.getPostponedOperationState(oID)
                    if postponedTime:
                        tooltipAlias = TOOLTIPS_CONSTANTS.OPERATION_POSTPONED
                    enabled = False
                elif o.isFullCompleted():
                    state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_FULL_STATE
                elif o.isAwardAchieved():
                    state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE
                elif o.isInProgress():
                    state = PERSONAL_MISSIONS_ALIASES.OPERATION_CURRENT_STATE
                elif o.isUnlocked():
                    state = PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE
                operationVO = {'id': oID,
                 'pmType': branch,
                 'state': state,
                 'icon': RES_ICONS.getPersonalMissionOperation(str(oID), self.__formatImageState(state)),
                 'postponedTime': postponedTime if not timeIconAlreadySet else '',
                 'enabled': enabled,
                 'tooltipAlias': tooltipAlias}
                if postponedTime:
                    timeIconAlreadySet = True
                operations.append(operationVO)

        self.as_setOperationsS(operations)
        self.enableNavigationSoundEffect()

    def __onQuestsUpdated(self, *args):
        self.__update()

    def __setTitle(self):
        titleVO = {'title': PERSONAL_MISSIONS.OPERATIONINFO_TITLE,
         'tooltip': {'tooltip': '',
                     'specialArgs': [],
                     'specialAlias': None,
                     'isSpecial': False}}
        self.as_setTitleS(titleVO)
        return

    def __formatImageState(self, state):
        if state == PERSONAL_MISSIONS_ALIASES.OPERATION_DISABLED_STATE:
            return PERSONAL_MISSIONS_ALIASES.OPERATION_LOCKED_STATE
        return PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE if state == PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_FULL_STATE else state

    def _onSettingsChanged(self, diff):
        if 'isRegularQuestEnabled' in diff and not diff['isRegularQuestEnabled'] or 'isPM2QuestEnabled' in diff and not diff['isPM2QuestEnabled'] or 'disabledPMOperations' in diff and diff['disabledPMOperations'] or 'disabledPersonalMissions' in diff and diff['disabledPersonalMissions']:
            self.__update()


class PM3Operations(InjectComponentAdaptor):

    def onSectionActivated(self):
        if self.__view is not None:
            self.__view.activate()
        return

    def onSectionDeactivated(self):
        if self.__view is not None:
            self.__view.deactivate()
        return

    def _makeInjectView(self, *args):
        self.__view = PersonalMissionsOperationsView()
        return self.__view
