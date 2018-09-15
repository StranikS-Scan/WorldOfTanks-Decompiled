# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_details_container_view.py
from operator import methodcaller
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getDetailedMissionData
from gui.Scaleform.daapi.view.meta.PersonalMissionDetailsContainerViewMeta import PersonalMissionDetailsContainerViewMeta
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.server_events import events_helpers
from gui.shared import events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
MAY_PAWN_PERSONAL_MISSION = '_MayPawnPersonalMission'

def getTutorialGlobalStorage():
    try:
        from tutorial.control.context import GlobalStorage
    except ImportError:
        LOG_ERROR('Can not load package tutorial')
        GlobalStorage = None

    return GlobalStorage


class PersonalMissionDetailsContainerView(LobbySubView, PersonalMissionDetailsContainerViewMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(PersonalMissionDetailsContainerView, self).__init__(ctx)
        self.__selectedQuestID = 0
        self._initialize(ctx)
        self.__quests = self.__getQuests()
        quest = self.__quests.get(self.__selectedQuestID)
        mayPawn = self.eventsCache.random.getFreeTokensCount() >= quest.getPawnCost() and quest.canBePawned()
        self.__storage = getTutorialGlobalStorage()
        if self.__storage:
            self.__storage.setValue(MAY_PAWN_PERSONAL_MISSION, mayPawn)

    def closeView(self):
        self.destroy()

    def useSheet(self, eventID):
        self._pawnMission(eventID)

    def startMission(self, eventID):
        self._processMission(eventID)

    def obtainAward(self, eventID):
        LOG_ERROR('Award obtain from personal mission details view is not available.')

    def onChangePage(self, eventID):
        self.__selectedQuestID = int(eventID)
        quest = self.__quests.get(self.__selectedQuestID)
        mayPawn = self.eventsCache.random.getFreeTokensCount() >= quest.getPawnCost() and quest.canBePawned()
        if self.__storage:
            self.__storage.setValue(MAY_PAWN_PERSONAL_MISSION, mayPawn)
        vehicleSelector = self.components.get(QUESTS_ALIASES.PERSONAL_MISSIONS_VEHICLE_SELECTOR_ALIAS)
        criteria, extraConditions = getDetailedMissionData(quest).getVehicleRequirementsCriteria()
        vehicleSelector.as_closeS()
        vehicleSelector.setSelectedQuest(self.__selectedQuestID)
        if criteria and quest.isInProgress() and quest.isAvailable()[0]:
            vehicleSelector.setCriteria(criteria, extraConditions)
        else:
            vehicleSelector.as_hideSelectedVehicleS()

    def declineMission(self, eventID):
        self._declineMission(eventID)

    def retryMission(self, eventID):
        self._processMission(eventID)

    def _initialize(self, ctx=None):
        ctx = ctx or {}
        self.__selectedQuestID = int(ctx.get('eventID', 0))

    @decorators.process('updating')
    def _processMission(self, eventID):
        quest = events_helpers.getPersonalMissionsCache().getQuests()[int(eventID)]
        result = yield events_helpers.getPersonalMissionsSelectProcessor()(quest, events_helpers.getPersonalMissionsCache()).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def _declineMission(self, eventID):
        result = yield events_helpers.getPersonalMissionsRefuseProcessor()(events_helpers.getPersonalMissionsCache().getQuests()[int(eventID)], events_helpers.getPersonalMissionsCache()).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def _pawnMission(self, eventID):
        quest = events_helpers.getPersonalMissionsCache().getQuests()[int(eventID)]
        result = yield events_helpers.getPersonalMissionsPawnProcessor()(quest).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def _populate(self):
        super(PersonalMissionDetailsContainerView, self)._populate()
        self.eventsCache.onSyncCompleted += self.__setData
        self.eventsCache.onProgressUpdated += self._onProgressUpdated
        self.__setData()

    def _invalidate(self, ctx=None):
        self._initialize(ctx)
        self.__setData()

    def _dispose(self):
        super(PersonalMissionDetailsContainerView, self)._dispose()
        self.eventsCache.onSyncCompleted -= self.__setData
        self.eventsCache.onProgressUpdated -= self._onProgressUpdated
        self.__storage = None
        self.__quests = None
        return

    def _onProgressUpdated(self, _):
        self.__quests = self.__getQuests()
        self.__setData()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_PERSONAL_MISSION_DETAILS_VIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleDetailsClose(self, _):
        """ We may need to close details externally when it already open.
        """
        self.closeView()

    def __getQuests(self):
        selectedQuest = self.eventsCache.personalMissions.getQuests().get(self.__selectedQuestID, None)
        tile = self.eventsCache.personalMissions.getOperations()[selectedQuest.getOperationID()]
        quests = tile.getQuestsByFilter(lambda q: bool(selectedQuest.getVehicleClasses() & q.getVehicleClasses()))
        return quests

    def __setData(self):
        datailedList = []
        for idx, q in enumerate(sorted(self.__quests.itervalues(), key=methodcaller('getID'))):
            datailedList.append(getDetailedMissionData(q).getInfo())

        pages = map(lambda (i, mission): {'buttonsGroup': 'MissionDetailsPageGroup',
         'pageIndex': i,
         'label': '%i' % (i + 1),
         'tooltip': {'isSpecial': True,
                     'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_MAP_REGION,
                     'specialArgs': [int(mission.get('eventID')), 0]},
         'status': mission.get('status'),
         'selected': self.__selectedQuestID == int(mission.get('eventID'))}, enumerate(datailedList))
        self.as_setInitDataS({'title': 'Title',
         'missions': datailedList,
         'pages': pages})
