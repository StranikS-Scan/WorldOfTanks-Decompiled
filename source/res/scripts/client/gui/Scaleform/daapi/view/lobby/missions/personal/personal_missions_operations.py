# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_operations.py
import operator
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.daapi.view.meta.PersonalMissionOperationsMeta import PersonalMissionOperationsMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from personal_missions import PM_BRANCH
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class PersonalMissionOperations(LobbySubView, PersonalMissionOperationsMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE

    def __init__(self, ctx):
        super(PersonalMissionOperations, self).__init__(ctx)
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)

    def showInfo(self):
        g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)

    def onOperationClick(self, branch, operationID):
        self.setBranch(branch)
        self.setOperationID(operationID)
        g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ctx={'previewAlias': self.getAlias()}), scope=EVENT_BUS_SCOPE.LOBBY)

    def closeView(self):
        event = g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_HANGAR)
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalMissionOperations, self)._populate()
        self._eventsCache.onPersonalQuestsVisited()
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.__setTitle()
        self.__update()

    def _dispose(self):
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        super(PersonalMissionOperations, self)._dispose()

    def __update(self):
        operations = []
        timeIconAlreadySet = False
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            for oID, o in sorted(self._eventsCache.getPersonalMissions().getOperationsForBranch(branch).iteritems(), key=operator.itemgetter(0)):
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
        for branch in SOUNDS.RTCP_MISSION_BRANCH.values():
            self.soundManager.setRTPC(branch, SOUNDS.BRANCH_DEFAULT)

        self.soundManager.setRTPC(SOUNDS.RTCP_MISSIONS_ZOOM, SOUNDS.MAX_MISSIONS_ZOOM)
        self.soundManager.setRTPC(SOUNDS.RTCP_DEBRIS_CONTROL, SOUNDS.MAX_MISSIONS_ZOOM)

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
