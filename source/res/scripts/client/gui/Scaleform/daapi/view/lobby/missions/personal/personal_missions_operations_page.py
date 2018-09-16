# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_operations_page.py
import operator
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.PersonalMissionOperationsPageMeta import PersonalMissionOperationsPageMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.server_events import events_helpers
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
BLINK_DELAY = 400
BLINK_DELAY_STEP = 300

class PersonalMissionOperationsPage(LobbySubView, PersonalMissionOperationsPageMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE

    def __init__(self, ctx):
        super(PersonalMissionOperationsPage, self).__init__(ctx)
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)

    def showInfo(self):
        g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)

    def onOperationClick(self, operationID):
        self.setOperationID(operationID)
        g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)

    def showAwards(self):
        g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)

    def closeView(self):
        event = g_entitiesFactories.makeLoadEvent(self.__backAlias)
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalMissionOperationsPage, self)._populate()
        self._eventsCache.onPersonalQuestsVisited()
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.__update()

    def _dispose(self):
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        super(PersonalMissionOperationsPage, self)._dispose()

    def __update(self):
        operations = []
        blinkDelay = BLINK_DELAY
        selectedOperation = -1
        areAllOperationsPassed = True
        sortedOperations = sorted(events_helpers.getPersonalMissionsCache().getOperations().iteritems(), key=operator.itemgetter(0))
        for oID, o in sortedOperations:
            title = text_styles.main(o.getShortUserName())
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE
            isAwardAchieved = o.isAwardAchieved()
            if o.isUnlocked() and not isAwardAchieved:
                selectedOperation = oID
            if not isAwardAchieved:
                areAllOperationsPassed = False
            if o.isFullCompleted():
                state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_FULL_STATE
            elif isAwardAchieved:
                state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE
            elif o.isInProgress():
                state = PERSONAL_MISSIONS_ALIASES.OPERATION_CURRENT_STATE
            operationVO = {'title': title,
             'id': oID,
             'state': state,
             'showDelay': blinkDelay}
            blinkDelay += BLINK_DELAY_STEP
            operations.append(operationVO)

        self.as_setDataS({'operationTitle': {'title': text_styles.promoTitle(PERSONAL_MISSIONS.OPERATIONINFO_TITLE)},
         'operations': operations,
         'selectedOperation': selectedOperation,
         'areAllOperationsPassed': areAllOperationsPassed})
        self.soundManager.setRTPC(SOUNDS.RTCP_MISSIONS_ZOOM, SOUNDS.MAX_MISSIONS_ZOOM)
        self.soundManager.setRTPC(SOUNDS.RTCP_DEBRIS_CONTROL, SOUNDS.MAX_MISSIONS_ZOOM)

    def __onQuestsUpdated(self, *args):
        self.__update()
