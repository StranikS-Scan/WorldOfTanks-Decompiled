# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_details_container_view.py
import logging
from operator import methodcaller
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getDetailedMissionData, getMapRegionTooltipData
from gui.Scaleform.daapi.view.meta.PersonalMissionDetailsContainerViewMeta import PersonalMissionDetailsContainerViewMeta
from gui.shared import events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.events import PersonalMissionsEvent
from gui.shared.gui_items.processors import quests as quests_proc
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils import decorators
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from tutorial.control.context import GLOBAL_FLAG
_logger = logging.getLogger(__name__)

class PersonalMissionDetailsContainerView(LobbySubView, PersonalMissionDetailsContainerViewMeta):
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    _eventsCache = dependency.descriptor(IEventsCache)
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(PersonalMissionDetailsContainerView, self).__init__(ctx)
        self.__selectedQuestID = 0
        self.__storage = getTutorialGlobalStorage()
        self._initialize(ctx)
        self.__quests = self.__getQuests()
        quest = self.__quests.get(self.__selectedQuestID)
        self.__branch = quest.getPMType().branch
        self.__operationID = quest.getOperationID()

    def closeView(self):
        self.destroy()

    def useSheet(self, eventID):
        self._pawnMission(eventID)

    def startMission(self, eventID):
        self._processMission(eventID)

    def obtainAward(self, eventID):
        _logger.error('Award obtain from personal mission details view is not available.')

    def requestMissionData(self, index):
        missionData = self.__datailedList[index]
        self.as_setMissionDataS(missionData)
        self.changePage(missionData['eventID'])

    def changePage(self, eventID):
        self.__selectedQuestID = int(eventID)
        quest = self.__quests.get(self.__selectedQuestID)
        self.__setMayPawnForQuest(quest)

    def discardMission(self, eventID):
        self._discardMission(eventID)

    def retryMission(self, eventID):
        self._processMission(eventID)

    def onPauseClick(self, eventID):
        self._pauseMission(eventID)

    def _initialize(self, ctx=None):
        ctx = ctx or {}
        self.__selectedQuestID = int(ctx.get('eventID', 0))

    @decorators.process('updating')
    def _processMission(self, eventID):
        quest = self.__quests[int(eventID)]
        result = yield quests_proc.PMQuestSelect(quest, self._eventsCache.getPersonalMissions(), self.__branch).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def _discardMission(self, eventID):
        result = yield quests_proc.PMDiscard(self.__quests[int(eventID)], self.__branch).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def _pauseMission(self, eventID):
        quest = self.__quests[int(eventID)]
        result = yield quests_proc.PMPause(quest, not quest.isOnPause, self.__branch).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def _pawnMission(self, eventID):
        quest = self.__quests[int(eventID)]
        result = yield quests_proc.PMPawn(quest).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def _populate(self):
        super(PersonalMissionDetailsContainerView, self)._populate()
        self._eventsCache.onProgressUpdated += self._onProgressUpdated
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self._onSettingsChanged
        self.__setData()
        self.__setMayPawnForQuest(self.__quests.get(self.__selectedQuestID))
        self.fireEvent(PersonalMissionsEvent(PersonalMissionsEvent.ON_DETAILS_VIEW_OPEN), EVENT_BUS_SCOPE.LOBBY)

    def _invalidate(self, ctx=None):
        self._initialize(ctx)
        self.__quests = self.__getQuests()
        self.__setData()

    def _dispose(self):
        self.fireEvent(PersonalMissionsEvent(PersonalMissionsEvent.ON_DETAILS_VIEW_CLOSE), EVENT_BUS_SCOPE.LOBBY)
        super(PersonalMissionDetailsContainerView, self)._dispose()
        self._lobbyCtx.getServerSettings().onServerSettingsChange -= self._onSettingsChanged
        self._eventsCache.onProgressUpdated -= self._onProgressUpdated
        self.__storage = None
        self.__quests = None
        return

    def _onProgressUpdated(self, branch):
        if self.__branch == branch:
            self.__quests = self.__getQuests()
            self.__setData()
            for qData in self.__datailedList:
                if qData['eventID'] == str(self.__selectedQuestID):
                    self.as_setMissionDataS(qData)

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_PERSONAL_MISSION_DETAILS_VIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleDetailsClose(self, _):
        self.closeView()

    def __getQuests(self):
        selectedQuest = self._eventsCache.getPersonalMissions().getAllQuests().get(self.__selectedQuestID, None)
        self.__operationID = selectedQuest.getOperationID()
        tile = self._eventsCache.getPersonalMissions().getAllOperations()[self.__operationID]
        return tile.getQuestsInChainByFilter(selectedQuest.getChainID())

    def __setData(self):
        self.__datailedList = []
        pages = []
        for idx, q in enumerate(sorted(self.__quests.itervalues(), key=methodcaller('getID'))):
            qData = getDetailedMissionData(q).getInfo()
            self.__datailedList.append(qData)
            eventID = q.getID()
            status = qData.get('status')
            pages.append({'buttonsGroup': 'MissionDetailsPageGroup',
             'pageIndex': idx,
             'label': str(idx + 1),
             'tooltip': getMapRegionTooltipData(status, q),
             'status': status,
             'selected': self.__selectedQuestID == eventID})

        self.as_setInitDataS({'pages': pages})

    def __setMayPawnForQuest(self, quest):
        pawn = self._eventsCache.getPersonalMissions().getFreeTokensCount(self.__branch) >= quest.getPawnCost() and quest.canBePawned() and not quest.isDisabled()
        if self.__storage:
            self.__storage.setValue(GLOBAL_FLAG.MAY_PAWN_PERSONAL_MISSION, pawn, showImmediately=False)

    def _onSettingsChanged(self, diff):
        disabledBranch = False
        if self.__branch == PM_BRANCH.REGULAR and 'isRegularQuestEnabled' in diff:
            disabledBranch = not diff['isRegularQuestEnabled']
        if self.__branch == PM_BRANCH.PERSONAL_MISSION_2 and 'isPM2QuestEnabled' in diff:
            disabledBranch = not diff['isPM2QuestEnabled']
        disabledOp = False
        if 'disabledPMOperations' in diff and diff['disabledPMOperations']:
            disabledOp = self.__operationID in diff['disabledPMOperations'].keys()
        disabledQuest = False
        if 'disabledPersonalMissions' in diff and diff['disabledPersonalMissions']:
            disabledQuest = self.__selectedQuestID in diff['disabledPersonalMissions']
        if disabledBranch or disabledOp or disabledQuest:
            self.closeView()
        else:
            self._onProgressUpdated(None)
        return
