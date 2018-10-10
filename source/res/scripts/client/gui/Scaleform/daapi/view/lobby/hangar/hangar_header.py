# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_header.py
import constants
import nations
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.missions.regular import missions_page
from gui.Scaleform.daapi.view.meta.HangarHeaderMeta import HangarHeaderMeta
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.marathon.marathon_constants import DEFAULT_MARATHON_PREFIX
from gui.server_events import finders
from gui.server_events.events_dispatcher import showMissionsForCurrentVehicle, showPersonalMission, showMissionsElen, showMissionsMarathon, showPersonalMissionOperationsPage, showPersonalMissionsOperationsMap
from gui.shared.formatters import text_styles, icons
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from personal_missions import PM_BRANCH
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.shared.personality import ServicesLocator
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IQuestsController, IMarathonEventsController
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.connection_mgr import IConnectionManager
from gui.prb_control import prb_getters
from skeletons.gui.lobby_context import ILobbyContext
from gui.prb_control.entities.listener import IGlobalListener
from gui.event_boards.listener import IEventBoardsListener

class WIDGET_PM_STATE(object):
    DISABLED = 0
    BRANCH_DISABLED = 2
    OPERATION_DISABLED = 4
    MISSION_DISABLED = 8
    UNAVAILABLE = 16
    LOW_LEVEL = 32
    NO_VEHICLE = 64
    DONE = 128
    DONE_LOCKED_NEXT = DONE | UNAVAILABLE
    DONE_LOW_NEXT = DONE | NO_VEHICLE
    COMPLETED = 256
    COMPLETED_LOCKED_NEXT = COMPLETED | UNAVAILABLE
    COMPLETED_LOW_NEXT = COMPLETED | NO_VEHICLE
    AVAILABLE = 512
    IN_PROGRESS = 1024
    ON_PAUSE = 2048


class LABEL_STATE(object):
    ACTIVE = 'active'
    EMPTY = 'empty'
    INACTIVE = 'inactive'
    ALL_DONE = 'all_done'


class HANGAR_FLAGS_ORDER(object):
    FIRST = 1
    SECOND = 2
    THIRD = 3


QUEST_TYPE_BY_PM_BRANCH = {PM_BRANCH.REGULAR: HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR,
 PM_BRANCH.PERSONAL_MISSION_2: HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2}
HANGAR_HEADER_QUESTS_TO_PM_BRANCH = {value:key for key, value in QUEST_TYPE_BY_PM_BRANCH.iteritems()}
FLAG_BY_QUEST_TYPE = {HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_RED,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_VINOUS,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_BLUE,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_KHACKI}
TOOLTIPS_HANGAR_HEADER_PM = {WIDGET_PM_STATE.BRANCH_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_BRANCH_DISABLED,
 WIDGET_PM_STATE.LOW_LEVEL: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_LOWLEVEL,
 WIDGET_PM_STATE.MISSION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_MISSION_DISABLED,
 WIDGET_PM_STATE.AVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_AVAILABLE,
 WIDGET_PM_STATE.COMPLETED_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETEDLOCKEDNEXT,
 WIDGET_PM_STATE.COMPLETED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.DONE_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.DONE_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONELOCKEDNEXT,
 WIDGET_PM_STATE.DONE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.NO_VEHICLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_NOVEHICLE,
 WIDGET_PM_STATE.UNAVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_BRANCH_DISABLED,
 WIDGET_PM_STATE.OPERATION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_OPERATION_DISABLED,
 WIDGET_PM_STATE.DISABLED: None}
TOOLTIPS_HANGAR_HEADER_PM2 = {WIDGET_PM_STATE.BRANCH_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_BRANCH_DISABLED,
 WIDGET_PM_STATE.LOW_LEVEL: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_LOWLEVEL,
 WIDGET_PM_STATE.MISSION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_MISSION_DISABLED,
 WIDGET_PM_STATE.AVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_AVAILABLE,
 WIDGET_PM_STATE.COMPLETED_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_COMPLETEDLOCKEDNEXT,
 WIDGET_PM_STATE.COMPLETED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.DONE_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.DONE_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_DONELOCKEDNEXT,
 WIDGET_PM_STATE.DONE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.NO_VEHICLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_NOVEHICLE,
 WIDGET_PM_STATE.UNAVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_UNAVAILABLEFULL,
 WIDGET_PM_STATE.OPERATION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_OPERATION_DISABLED,
 WIDGET_PM_STATE.DISABLED: None}

def _findPersonalMissionsState(eventsCache, vehicle, branch):
    branchState = WIDGET_PM_STATE.DISABLED
    vehicleLvl = vehicle.level
    vehicleType = vehicle.descriptor.type
    fullDone = True
    statesQueue = (WIDGET_PM_STATE.AVAILABLE,
     WIDGET_PM_STATE.COMPLETED_LOW_NEXT,
     WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT,
     WIDGET_PM_STATE.COMPLETED,
     WIDGET_PM_STATE.DONE_LOW_NEXT,
     WIDGET_PM_STATE.DONE_LOCKED_NEXT,
     WIDGET_PM_STATE.DONE,
     WIDGET_PM_STATE.NO_VEHICLE,
     WIDGET_PM_STATE.UNAVAILABLE,
     WIDGET_PM_STATE.OPERATION_DISABLED,
     WIDGET_PM_STATE.DISABLED)
    for operation in eventsCache.getPersonalMissions().getOperationsForBranch(branch).itervalues():
        operationState = WIDGET_PM_STATE.DISABLED
        if not operation.isCompleted():
            fullDone = False
        if operation.isDisabled():
            operationState |= WIDGET_PM_STATE.OPERATION_DISABLED
        elif not operation.isUnlocked():
            operationState |= WIDGET_PM_STATE.UNAVAILABLE
            continue
        for chainID, chain in operation.getQuests().iteritems():
            if not operation.getChainClassifier(chainID).matchVehicle(vehicleType):
                continue
            firsQuest = chain.values()[0]
            if vehicleLvl < firsQuest.getVehMinLevel():
                operationState |= WIDGET_PM_STATE.NO_VEHICLE
            for quest in chain.itervalues():
                if quest.isInProgress():
                    if operation.isDisabled():
                        return (WIDGET_PM_STATE.OPERATION_DISABLED, None)
                    if quest.isDisabled():
                        return (WIDGET_PM_STATE.MISSION_DISABLED, None)
                    if quest.isOnPause:
                        return (WIDGET_PM_STATE.ON_PAUSE, quest)
                    if vehicleLvl < quest.getVehMinLevel():
                        return (WIDGET_PM_STATE.LOW_LEVEL, None)
                    return (WIDGET_PM_STATE.IN_PROGRESS, quest)
                if operation.isDisabled() or quest.isDisabled() or operationState & WIDGET_PM_STATE.NO_VEHICLE:
                    continue
                if quest.isFullCompleted():
                    operationState |= WIDGET_PM_STATE.DONE
                if quest.isMainCompleted():
                    operationState |= WIDGET_PM_STATE.COMPLETED
                operationState |= WIDGET_PM_STATE.AVAILABLE

        branchState |= operationState

    if fullDone:
        branchState |= WIDGET_PM_STATE.COMPLETED
    for priorState in statesQueue:
        if branchState & priorState == priorState:
            return (priorState, None)

    return None


def _getPersonalMissionsIcon(vehicle, branch, active):
    if branch == PM_BRANCH.REGULAR:
        if active:
            return RES_ICONS.vehicleTypeOutline(vehicle.type)
        return RES_ICONS.vehicleTypeInactiveOutline(vehicle.type)
    if branch == PM_BRANCH.PERSONAL_MISSION_2:
        allianceId = nations.NATION_TO_ALLIANCE_IDS_MAP[vehicle.nationID]
        alliance = nations.ALLIANCES_TAGS_ORDER[allianceId]
        if active:
            return RES_ICONS.getAlliance32x32Icon(alliance)
        return RES_ICONS.getAlliance32x32InactiveIcon(alliance)


def _getPersonalMissionsTooltip(branch, key):
    if branch == PM_BRANCH.REGULAR:
        return TOOLTIPS_HANGAR_HEADER_PM.get(key, '')
    return TOOLTIPS_HANGAR_HEADER_PM2.get(key, '') if branch == PM_BRANCH.PERSONAL_MISSION_2 else ''


class HangarHeader(HangarHeaderMeta, IGlobalListener, IEventBoardsListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _questController = dependency.descriptor(IQuestsController)
    _eventsController = dependency.descriptor(IEventBoardController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    def __init__(self):
        super(HangarHeader, self).__init__()
        self._currentVehicle = None
        return

    def onQuestBtnClick(self, questType, questID):
        if questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON:
            missions_page.setHideDoneFilter()
            showMissionsForCurrentVehicle()
        elif questType in QUEST_TYPE_BY_PM_BRANCH.itervalues():
            if questID:
                showPersonalMission(missionID=int(questID))
            elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR:
                self.__showAvailablePMOperation(PM_BRANCH.REGULAR)
            elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2:
                self.__showAvailablePMOperation(PM_BRANCH.PERSONAL_MISSION_2)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT:
            showMissionsElen(questID)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_MARATHON:
            marathonPrefix = questID or DEFAULT_MARATHON_PREFIX
            showMissionsMarathon(marathonPrefix)

    def onUpdateHangarFlag(self):
        self.update()

    def update(self, *args):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)

    def _populate(self):
        super(HangarHeader, self)._populate()
        self._currentVehicle = g_currentVehicle
        self._eventsCache.onSyncCompleted += self.update
        self._eventsCache.onProgressUpdated += self.update
        g_clientUpdateManager.addCallbacks({'inventory.1': self.update,
         'stats.tutorialsCompleted': self.update})
        if self._eventsController:
            self._eventsController.addListener(self)
        self._marathonsCtrl.onFlagUpdateNotify += self.update
        self.addListener(events.TutorialEvent.SET_HANGAR_HEADER_ENABLED, self.__onSetHangarHeaderEnabled, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._marathonsCtrl.onFlagUpdateNotify -= self.update
        self._eventsCache.onSyncCompleted -= self.update
        self._eventsCache.onProgressUpdated -= self.update
        self._currentVehicle = None
        if self._eventsController:
            self._eventsController.removeListener(self)
        self.removeListener(events.TutorialEvent.SET_HANGAR_HEADER_ENABLED, self.__onSetHangarHeaderEnabled, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(HangarHeader, self)._dispose()
        return

    def _makeHeaderVO(self):
        if self.app.tutorialManager.hangarHeaderEnabled and self._currentVehicle.isPresent():
            vehicle = self._currentVehicle.item
            quests = self._getQuestsToHeaderVO(vehicle)
            headerVO = {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
             'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.shortUserName), text_styles.stats(MENU.levels_roman(vehicle.level))),
             'isPremIGR': vehicle.isPremiumIGR,
             'isVisible': True,
             'quests': quests}
        else:
            headerVO = {'isVisible': False,
             'quests': []}
        return headerVO

    def _getQuestsToHeaderVO(self, vehicle):
        quests = []
        personalMissions = self.__getPersonalMissionsVO(vehicle)
        if personalMissions:
            quests.append(personalMissions)
        battleQuests = self.__getBattleQuestsVO(vehicle)
        if battleQuests:
            quests.append(battleQuests)
        marathonQuests = self.__getMarathonQuestsVO(vehicle)
        if marathonQuests:
            quests.append(marathonQuests)
        eventQuests = self.__getElenQuestsVO(vehicle)
        if eventQuests:
            quests.append(eventQuests)
        return quests

    def __showAvailablePMOperation(self, branch):
        for operationID in finders.BRANCH_TO_OPERATION_IDS[branch]:
            operation = self._eventsCache.getPersonalMissions().getAllOperations()[operationID]
            result, _ = operation.isAvailable()
            if result:
                showPersonalMissionOperationsPage(branch, operationID)
                return

        showPersonalMissionsOperationsMap()

    def __getPersonalMissionsVO(self, vehicle):
        result = []
        states = []
        for branch in reversed(PM_BRANCH.ACTIVE_BRANCHES):
            questType = QUEST_TYPE_BY_PM_BRANCH[branch]
            if not self._lobbyContext.getServerSettings().isPersonalMissionsEnabled(branch):
                result.append(self._headerQuestFormaterVo(False, _getPersonalMissionsIcon(vehicle, branch, False), _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.EMPTY)), questType, tooltip=_getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.BRANCH_DISABLED)))
                states.append(WIDGET_PM_STATE.BRANCH_DISABLED)
            pmState, quest = _findPersonalMissionsState(self._eventsCache, vehicle, branch)
            states.append(pmState)
            enable = True
            personalMissionID = ''
            if pmState == WIDGET_PM_STATE.IN_PROGRESS:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ACTIVE), current=quest.getInternalID())
                personalMissionID = quest.getID()
                tooltip = TOOLTIPS_CONSTANTS.PERSONAL_QUESTS_PREVIEW
            elif pmState == WIDGET_PM_STATE.ON_PAUSE:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ON_PAUSE))
                personalMissionID = quest.getID()
                tooltip = TOOLTIPS_CONSTANTS.PERSONAL_QUESTS_PREVIEW
            elif pmState == WIDGET_PM_STATE.AVAILABLE:
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_PLUS
                label = MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.EMPTY)
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.AVAILABLE)
            elif pmState == WIDGET_PM_STATE.COMPLETED:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.COMPLETED)
            elif pmState == WIDGET_PM_STATE.COMPLETED_LOW_NEXT:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.COMPLETED_LOW_NEXT)
            elif pmState == WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT)
            elif pmState == WIDGET_PM_STATE.DONE:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.DONE)
            elif pmState == WIDGET_PM_STATE.DONE_LOW_NEXT:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.DONE_LOW_NEXT)
            elif pmState == WIDGET_PM_STATE.DONE_LOCKED_NEXT:
                icon = _getPersonalMissionsIcon(vehicle, branch, True)
                label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.DONE_LOCKED_NEXT)
                enable = False
            else:
                icon = _getPersonalMissionsIcon(vehicle, branch, False)
                label = MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.INACTIVE)
                tooltip = _getPersonalMissionsTooltip(branch, pmState)
                enable = False
            result.append(self._headerQuestFormaterVo(enable, icon, label, questType, questID=personalMissionID, tooltip=tooltip, isTooltipSpecial=bool(pmState & WIDGET_PM_STATE.IN_PROGRESS or pmState & WIDGET_PM_STATE.ON_PAUSE)))

        if all([ st == WIDGET_PM_STATE.DONE for st in states ]):
            for vo in result:
                vo['tooltip'] = TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONEALL

        elif all([ st == WIDGET_PM_STATE.NO_VEHICLE for st in states ]):
            for vo in result:
                vo['tooltip'] = TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DISABLEDALL

        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_PERSONAL, RES_ICONS.MAPS_ICONS_QUESTS_HEADERFLAGICONS_PERSONAL, result)

    def __onServerSettingChanged(self, diff):
        if 'elenSettings' in diff:
            self.update()

    def __getBattleQuestsVO(self, vehicle):
        quests = self._questController.getQuestForVehicle(vehicle)
        totalCount = len(quests)
        completedQuests = len([ q for q in quests if q.isCompleted() ])
        if totalCount > 0:
            if completedQuests != totalCount:
                label = _ms(MENU.hangarHeaderBattleQuestsLabel(LABEL_STATE.ACTIVE), total=totalCount - completedQuests)
            else:
                label = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE)
            commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_AVAILABLE
        else:
            commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_DISABLED
            label = ''
        quests = [self._headerQuestFormaterVo(totalCount > 0, commonQuestsIcon, label, HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON, tooltip=TOOLTIPS_CONSTANTS.QUESTS_PREVIEW, isTooltipSpecial=True)]
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', quests)

    def __getMarathonQuestsVO(self, vehicle):
        marathonEvent = self._marathonsCtrl.getPrimaryMarathon()
        if marathonEvent:
            flagVO = marathonEvent.getMarathonFlagState(vehicle)
            if flagVO['visible']:
                quests = [self._headerQuestFormaterVo(flagVO['enable'], flagVO['flagHeaderIcon'], '', HANGAR_HEADER_QUESTS.QUEST_TYPE_MARATHON, flag=flagVO['flagMain'], stateIcon=flagVO['flagStateIcon'], questID=marathonEvent.prefix, tooltip=flagVO['tooltip'], isTooltipSpecial=True)]
                return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_MARATHON, '', quests)
        return None

    def __getElenQuestsVO(self, vehicle):
        eventsData = self._eventsController.getEventsSettingsData()
        hangarFlagData = self._eventsController.getHangarFlagData()
        isElenEnabled = ServicesLocator.lobbyContext.getServerSettings().isElenEnabled()
        dataError = eventsData is None or hangarFlagData is None
        if dataError or not isElenEnabled or not eventsData.hasActiveEvents() or hangarFlagData.isSpecialAccount():
            return
        else:
            isRegistered = False
            currentEvent = eventsData.getEventForVehicle(vehicle.intCD)
            if currentEvent is not None and currentEvent.isStarted() and not currentEvent.isFinished():
                eventId = currentEvent.getEventID()
                isRegistered = hangarFlagData.isRegistered(eventId)
                hasAnotherActiveEvents = eventsData.hasAnotherActiveEvents(eventId)
                regIsFinished = currentEvent.isRegistrationFinished()
                notValidEvent = regIsFinished and not isRegistered or hangarFlagData.wasCanceled(eventId)
                if notValidEvent and not hasAnotherActiveEvents:
                    return
                if notValidEvent and hasAnotherActiveEvents:
                    enable = False
                else:
                    enable = True
            else:
                if not eventsData.hasActiveEventsByState(hangarFlagData.getHangarFlags()):
                    return
                eventId = None
                enable = False
            if enable:
                eventQuestsTooltip = TOOLTIPS_CONSTANTS.EVENT_QUESTS_PREVIEW
                eventQuestsTooltipIsSpecial = True
                battleType = currentEvent.getBattleType()
                wrongBattleType = self.prbEntity.getEntityType() != battleType
                inSquadState = self.prbDispatcher.getFunctionalState().isInUnit(constants.PREBATTLE_TYPE.SQUAD)
                if inSquadState:
                    unit = prb_getters.getUnit(safe=True)
                    if len(unit.getMembers()) == 1:
                        inSquadState = False
                wrongSquadState = inSquadState and not currentEvent.getIsSquadAllowed()
                noserver = not currentEvent.isAvailableServer(self._connectionMgr.peripheryID)
                hasWarning = wrongBattleType or noserver or wrongSquadState
                registrationWillExpiredSoon = currentEvent.isRegistrationFinishSoon()
                endSoonWarning = currentEvent.isEndSoon() and not hasWarning and isRegistered
                if registrationWillExpiredSoon and not isRegistered or endSoonWarning:
                    eventQuestsLabel = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON)
                elif hasWarning and isRegistered:
                    eventQuestsLabel = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ALERT_ICON)
                else:
                    eventQuestsLabel = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ICON_FLAG)
                if isRegistered:
                    eventQuestsIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_CUP_ICON
                else:
                    eventQuestsIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_CROSS
            else:
                if not eventsData.hasActiveEvents():
                    return
                eventQuestsTooltip = TOOLTIPS.HANGAR_ELEN_BOTTOM_NOEVENTS
                eventQuestsTooltipIsSpecial = False
                eventQuestsLabel = '--'
                eventQuestsIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_CUP_DISABLE_ICON
            quests = [self._headerQuestFormaterVo(enable, eventQuestsIcon, eventQuestsLabel, HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT, questID=eventId, isReward=True, tooltip=eventQuestsTooltip, isTooltipSpecial=eventQuestsTooltipIsSpecial)]
            return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_EVENTS, '', quests)

    def _wrapQuestGroup(self, groupID, icon, quests):
        return {'groupID': groupID,
         'groupIcon': icon,
         'quests': quests}

    def _headerQuestFormaterVo(self, enable, icon, label, questType, flag=None, stateIcon=None, questID=None, isReward=False, tooltip='', isTooltipSpecial=False):
        return {'enable': enable,
         'flag': flag or FLAG_BY_QUEST_TYPE[questType],
         'icon': icon,
         'stateIcon': stateIcon,
         'label': label,
         'questType': questType,
         'questID': str(questID),
         'isReward': isReward,
         'tooltip': tooltip,
         'isTooltipSpecial': isTooltipSpecial}

    def __onSetHangarHeaderEnabled(self, _=None):
        self.update()
