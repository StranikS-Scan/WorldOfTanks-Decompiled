# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_header.py
import logging
import typing
import BigWorld
import inspect
import constants
import nations
from CurrentVehicle import g_currentVehicle
from gui import g_guiResetters
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.missions.regular import missions_page
from gui.Scaleform.daapi.view.meta.HangarHeaderMeta import HangarHeaderMeta
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_pass.battle_pass_helpers import getSupportedArenaBonusTypeFor
from gui.event_boards.listener import IEventBoardsListener
from gui.impl import backport
from gui.impl.gen import R
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.prb_control import prb_getters
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import finders
from gui.server_events.events_constants import BATTLE_ROYALE_GROUPS_ID
from gui.server_events.events_constants import RANKED_DAILY_GROUP_ID
from gui.server_events.events_dispatcher import showPersonalMission, showMissionsElen, showMissionsMarathon, showPersonalMissionOperationsPage, showPersonalMissionsOperationsMap, showMissionsCategories, showMissionsBattlePass, showMissionsMapboxProgression
from gui.server_events.events_helpers import isRankedDaily, isDailyEpic
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import icons
from gui.shared.personality import ServicesLocator
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_DAY
from personal_missions import PM_BRANCH
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IBattlePassController, IBootcampController, ICollectiveGoalEntryPointController, IResourceWellController, IMarathonEventsController, IFestivityController, IRankedBattlesController, IQuestsController, IBattleRoyaleController, IMapboxController, IEpicBattleMetaGameController, IFunRandomController, IComp7Controller, ILimitedUIController, IArmoryYardController, IEarlyAccessController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.tutorial import ITutorialLoader
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

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


class ActiveWidgets(object):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

    def __init__(self):
        self.__widgets = {self.LEFT: '',
         self.CENTER: '',
         self.RIGHT: ''}
        super(ActiveWidgets, self).__init__()

    def update(self, position, alias):
        if position in self.__widgets:
            if self.__widgets[position] != alias:
                self.__widgets[position] = alias
                return True
        return False


QUEST_TYPE_BY_PM_BRANCH = {PM_BRANCH.REGULAR: HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR,
 PM_BRANCH.PERSONAL_MISSION_2: HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2}
HANGAR_HEADER_QUESTS_TO_PM_BRANCH = {value:key for key, value in QUEST_TYPE_BY_PM_BRANCH.iteritems()}
FLAG_BY_QUEST_TYPE = {HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_VINOUS,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_RED,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_BLUE,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_KHACKI,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_ROYALE: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_EPIC_STEELHUNTER}
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
_SCREEN_WIDTH_FOR_MARATHON_GROUP = 1300

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
                    if vehicleLvl < quest.getVehMinLevel():
                        return (WIDGET_PM_STATE.LOW_LEVEL, None)
                    if quest.isOnPause:
                        return (WIDGET_PM_STATE.ON_PAUSE, quest)
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


def _getActiveQuestLabel(total, completed):
    return backport.text(R.strings.menu.hangar_header.battle_quests_label.dyn(LABEL_STATE.ACTIVE)(), total=total - completed)


def widgetFunc(alias):

    def decorator(fn):

        def wrapper(self, *args, **kwargs):
            return fn(self, *args, **kwargs)

        wrapper.alias = alias
        return wrapper

    return decorator


class HangarHeader(HangarHeaderMeta, IGlobalListener, IEventBoardsListener):
    __slots__ = ('_currentVehicle', '__screenWidth', '__isShowPersonalMission')
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _questController = dependency.descriptor(IQuestsController)
    _eventsController = dependency.descriptor(IEventBoardController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    _festivityController = dependency.descriptor(IFestivityController)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __tutorialLoader = dependency.descriptor(ITutorialLoader)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __resourceWell = dependency.descriptor(IResourceWellController)
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __collectiveGoalEntryPointController = dependency.descriptor(ICollectiveGoalEntryPointController)
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        super(HangarHeader, self).__init__()
        self._currentVehicle = None
        self.__screenWidth = None
        self.__isShowPersonalMission = True
        self.__activeWidgets = None
        self.__widgets = {wrapper.alias:wrapper for _, wrapper in inspect.getmembers(self.__class__, inspect.ismethod) if getattr(wrapper, 'alias', None)}
        return

    def onQuestBtnClick(self, questType, questID):
        if questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON:
            missions_page.setHideDoneFilter()
            showMissionsCategories(missionID=questID)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_GROUP_RANKED_DAILY:
            showMissionsCategories(groupID=RANKED_DAILY_GROUP_ID)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_PASS:
            showMissionsBattlePass()
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_MAPBOX:
            showMissionsMapboxProgression()
        elif questType in QUEST_TYPE_BY_PM_BRANCH.itervalues():
            if questID:
                showPersonalMission(missionID=int(questID))
            elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR:
                self.__showAvailablePMOperation(PM_BRANCH.REGULAR)
            elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2:
                self.__showAvailablePMOperation(PM_BRANCH.PERSONAL_MISSION_2)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT:
            showMissionsElen(questID)
        elif HANGAR_HEADER_QUESTS.QUEST_TYPE_MARATHON in questType:
            marathonPrefix = questID or self._marathonsCtrl.getPrimaryMarathon()
            showMissionsMarathon(marathonPrefix)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_ROYALE:
            showMissionsCategories(groupID=BATTLE_ROYALE_GROUPS_ID)

    def onUpdateHangarFlag(self):
        self.update()

    def onPrbEntitySwitched(self):
        super(HangarHeader, self).onPrbEntitySwitched()
        self.__updateBattleMattersEntryPoint()

    def update(self, *_):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)
        self.__updateWidget()
        self.__updateResourceWellEntryPoint()
        self.__updateCollectiveGoalEntryPoint()
        self.__updateArmoryYardEntryPoint()
        self.__updateEarlyAccessEntryPoint()

    def updateRankedHeader(self, *_):
        self.__updateWidget()

    def updateBattleRoyaleHeader(self):
        self.__updateWidget()

    def _populate(self):
        super(HangarHeader, self)._populate()
        self._currentVehicle = g_currentVehicle
        self.__screenWidth = BigWorld.screenSize()[0]
        self.__activeWidgets = ActiveWidgets()
        self._eventsCache.onSyncCompleted += self.update
        self._eventsCache.onProgressUpdated += self.update
        self._festivityController.onStateChanged += self.update
        self.__battlePassController.onSeasonStateChanged += self.update
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.update
        self.__rankedController.onGameModeStatusUpdated += self.update
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.update
        self.__mapboxCtrl.addProgressionListener(self.update)
        self.__resourceWell.onEventUpdated += self.update
        self.__collectiveGoalEntryPointController.onEventUpdated += self.__updateCollectiveGoalEntryPoint
        self.__battleMattersController.onStateChanged += self.__onBattleMattersStateChanged
        self.__battleMattersController.onFinish += self.__onBattleMattersStateChanged
        self.__limitedUIController.startObserve(LuiRules.BP_ENTRY, self.__updateBattlePassWidgetVisibility)
        self.__limitedUIController.startObserve(LuiRules.BATTLE_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.startObserve(LuiRules.BM_FLAG, self.__updateVisibilityBattleMatter)
        self.__limitedUIController.startObserve(LuiRules.PERSONAL_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.startObserve(LuiRules.RESOURCE_WELL, self.__updateResourceWell)
        self.__updateBattleMattersEntryPoint()
        self.__armoryYardCtrl.onUpdated += self.update
        self.__earlyAccessCtrl.onUpdated += self.update
        g_clientUpdateManager.addCallbacks({'inventory.1': self.update,
         'stats.tutorialsCompleted': self.update})
        if self._eventsController:
            self._eventsController.addListener(self)
        self._marathonsCtrl.onFlagUpdateNotify += self.update
        self.addListener(events.TutorialEvent.SET_HANGAR_HEADER_ENABLED, self.__onSetHangarHeaderEnabled, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_guiResetters.add(self.__onChangeScreenResolution)
        self.startGlobalListening()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._marathonsCtrl.onFlagUpdateNotify -= self.update
        self.__mapboxCtrl.removeProgressionListener(self.update)
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.update
        self._eventsCache.onSyncCompleted -= self.update
        self._eventsCache.onProgressUpdated -= self.update
        self._festivityController.onStateChanged -= self.update
        self.__battlePassController.onSeasonStateChanged -= self.update
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.update
        self.__rankedController.onGameModeStatusUpdated -= self.update
        self.__resourceWell.onEventUpdated -= self.update
        self.__collectiveGoalEntryPointController.onEventUpdated -= self.__updateCollectiveGoalEntryPoint
        self.__battleMattersController.onStateChanged -= self.__onBattleMattersStateChanged
        self.__battleMattersController.onFinish -= self.__onBattleMattersStateChanged
        self.__limitedUIController.stopObserve(LuiRules.BP_ENTRY, self.__updateBattlePassWidgetVisibility)
        self.__limitedUIController.stopObserve(LuiRules.BATTLE_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.stopObserve(LuiRules.BM_FLAG, self.__updateVisibilityBattleMatter)
        self.__limitedUIController.stopObserve(LuiRules.PERSONAL_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.stopObserve(LuiRules.RESOURCE_WELL, self.__updateResourceWell)
        self.__armoryYardCtrl.onUpdated -= self.update
        self.__earlyAccessCtrl.onUpdated -= self.update
        self._currentVehicle = None
        self.__screenWidth = None
        self.__activeWidgets = None
        self.__widgets.clear()
        self.__widgets = None
        if self._eventsController:
            self._eventsController.removeListener(self)
        self.removeListener(events.TutorialEvent.SET_HANGAR_HEADER_ENABLED, self.__onSetHangarHeaderEnabled, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_guiResetters.remove(self.__onChangeScreenResolution)
        self.stopGlobalListening()
        super(HangarHeader, self)._dispose()
        return

    def _makeHeaderVO(self):
        emptyHeaderVO = {'isVisible': False,
         'quests': []}
        if not self.__tutorialLoader.gui.hangarHeaderEnabled:
            return emptyHeaderVO
        if self.__rankedController.isRankedPrbActive():
            return {'isVisible': True,
             'quests': self.__getRankedQuestsToHeaderVO()}
        if self.__epicController.isEpicPrbActive():
            return {'isVisible': True,
             'quests': self.__getEpicQuestsToHeaderVO()}
        if self.__funRandomCtrl.isFunRandomPrbActive():
            return {'isVisible': True,
             'quests': []}
        if self._currentVehicle.isPresent():
            return {'isVisible': True,
             'quests': self._getCommonQuestsToHeaderVO(self._currentVehicle.item)}
        return {'isVisible': True,
         'quests': []} if self.__comp7Controller.isComp7PrbActive() else emptyHeaderVO

    def _getCommonQuestsToHeaderVO(self, vehicle):
        quests = []
        if self.__battleRoyaleController.isBattleRoyaleMode():
            if not (self.__battleRoyaleController.isInPrimeTime() and self.__isShowPersonalMission):
                return []
        if self.isPersonalMissionEnabled():
            personalMissions = self.__getPersonalMissionsVO(vehicle)
            if personalMissions:
                quests.append(personalMissions)
        if self.__limitedUIController.isRuleCompleted(LuiRules.BATTLE_MISSIONS):
            battleQuests = self.__getBattleQuestsVO(vehicle)
            if battleQuests:
                quests.append(battleQuests)
        if self.__mapboxCtrl.isMapboxMode():
            mapboxProgression = self.__getMapboxProgressionVO()
            if mapboxProgression:
                quests.append(mapboxProgression)
        isMarathonQuestsGroupped = self.__screenWidth <= _SCREEN_WIDTH_FOR_MARATHON_GROUP
        marathonQuests = self.__getMarathonQuestsVO(vehicle, isMarathonQuestsGroupped)
        if marathonQuests:
            if isMarathonQuestsGroupped:
                quests.append(marathonQuests)
            else:
                quests.extend(marathonQuests)
        if self.isElenQuestsEnabled():
            eventQuests = self.__getElenQuestsVO(vehicle)
            if eventQuests:
                quests.append(eventQuests)
        return quests

    def isPersonalMissionEnabled(self):
        return self._lobbyContext.getServerSettings().isPersonalMissionsEnabled() and not self.__mapboxCtrl.isMapboxMode() and not self.__comp7Controller.isComp7PrbActive() and self.__limitedUIController.isRuleCompleted(LuiRules.PERSONAL_MISSIONS)

    def isElenQuestsEnabled(self):
        return not self.__comp7Controller.isComp7PrbActive()

    def __getRankedQuestsToHeaderVO(self):
        quests = []
        rankedBattleQuests = self.__getRankedBattleQuestsVO()
        if rankedBattleQuests:
            quests.append(rankedBattleQuests)
        return quests

    def __getEpicQuestsToHeaderVO(self):
        quests = []
        epicBattleQuests = self.__getEpicBattleQuestsVO()
        if epicBattleQuests:
            quests.append(epicBattleQuests)
        return quests

    @widgetFunc(HANGAR_ALIASES.COMP7_WIDGET)
    def __getComp7Widget(self):
        return self.__comp7Controller.isComp7PrbActive()

    @widgetFunc(HANGAR_ALIASES.BATTLE_PASSS_ENTRY_POINT)
    def __getBPWidget(self):
        isBPAvailable = not self.__battlePassController.isDisabled()
        isValidBattleType = self.prbDispatcher and self.prbDispatcher.getEntity() and self.__battlePassController.isValidBattleType(self.prbDispatcher.getEntity())
        isRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.BP_ENTRY)
        isVisible = isBPAvailable and isValidBattleType and not self.__bootcampController.isInBootcamp() and isRuleCompleted
        return isVisible

    @widgetFunc(HANGAR_ALIASES.RANKED_WIDGET)
    def __getRBWidget(self):
        return self.__rankedController.isRankedPrbActive()

    @widgetFunc(FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR_WIDGET)
    def __getFunRandomWidget(self):
        return self.__funRandomCtrl.isFunRandomPrbActive()

    @widgetFunc(HANGAR_ALIASES.BATTLE_ROYALE_ENTRY_POINT)
    def __getBattleRoyaleWidgetAlias(self):
        return self.__battleRoyaleController.isGeneralHangarEntryPoint() and self.__battleRoyaleController.isBattleRoyaleMode() and self.__battleRoyaleController.isEnabled()

    @widgetFunc(HANGAR_ALIASES.BATTLE_ROYALE_TOURNAMENT)
    def __getBattleRoyaleTournamentWidgetAlias(self):
        return not self.__battleRoyaleController.isGeneralHangarEntryPoint()

    @widgetFunc(HANGAR_ALIASES.EPIC_WIDGET)
    def __getEpicWidget(self):
        return self.__epicController.isEnabled() and self.__epicController.isEpicPrbActive()

    def __updateWidget(self):
        alias = self.__getWidgetAlias()
        if not self.__activeWidgets.update(ActiveWidgets.CENTER, alias):
            return
        self.as_addEntryPointS(alias)
        if alias == HANGAR_ALIASES.BATTLE_ROYALE_ENTRY_POINT:
            self.__updateVisibilityPersonalMission(True)
        elif alias == HANGAR_ALIASES.BATTLE_ROYALE_TOURNAMENT:
            self.__updateVisibilityPersonalMission(False)
        self.__updateBattlePassSmallWidget()

    def __getWidgetAlias(self):
        for alias, widgetGetter in self.__widgets.iteritems():
            if widgetGetter(self):
                return alias

    def __updateBattlePassWidgetVisibility(self, *_):
        self.__updateWidget()

    def __showAvailablePMOperation(self, branch):
        for operationID in finders.BRANCH_TO_OPERATION_IDS[branch]:
            operation = self._eventsCache.getPersonalMissions().getAllOperations()[operationID]
            result, _ = operation.isAvailable()
            if result:
                showPersonalMissionOperationsPage(branch, operationID)
                return

        showPersonalMissionsOperationsMap()

    def __onChangeScreenResolution(self):
        self.__screenWidth = BigWorld.screenSize()[0]
        self.update()

    def __onBattleMattersStateChanged(self):
        self.__updateBattleMattersEntryPoint()

    def __getDisabledPersonalMissionsVO(self, modeName):
        result = []
        strPath = R.strings.tooltips.hangar.header.personalMissions.unavailable
        for branch in reversed(PM_BRANCH.ACTIVE_BRANCHES):
            questType = QUEST_TYPE_BY_PM_BRANCH[branch]
            result.append(self._headerQuestFormaterVo(enable=False, icon='', label=_ms(MENU.hangarHeaderPersonalMissionsLabel(LABEL_STATE.EMPTY)), questType=questType, tooltip=makeTooltip(header=backport.text(strPath.header()), body=backport.text(strPath.body(), modeName=backport.text(strPath.mode.dyn(modeName)())))))

        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_PERSONAL, RES_ICONS.MAPS_ICONS_QUESTS_HEADERFLAGICONS_PERSONAL, result, isRightSide=True)

    def __getPersonalMissionsVO(self, vehicle):
        result = []
        states = []
        if vehicle.isOnlyForBattleRoyaleBattles:
            return []
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

        result = sorted(result, key=lambda quest: quest['enable'], reverse=True)
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_PERSONAL, RES_ICONS.MAPS_ICONS_QUESTS_HEADERFLAGICONS_PERSONAL, result, True)

    def __onServerSettingChanged(self, diff):
        if 'elenSettings' in diff or constants.PremiumConfigs.PREM_QUESTS in diff:
            self.update()

    def __getMapboxProgressionVO(self):
        data = self.__mapboxCtrl.getProgressionData()
        if data is not None and self.__mapboxCtrl.isActive():
            completed = data.totalBattles
            if completed is None:
                _logger.error('battles played is None')
                return
            total = max(data.rewards)
            if completed < total:
                label = _ms(MENU.hangarHeaderMapboxProgressionLabel(LABEL_STATE.ACTIVE), total=completed)
            else:
                label = icons.makeImageTag(RES_ICONS.MAPS_ICONS_MISSIONS_ICONS_CHECK_GREEN_XS)
            progressionIcon = backport.image(R.images.gui.maps.icons.quests.headerFlagIcons.mapbox())
            flag = backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_green())
        else:
            flag = backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_gray())
            progressionIcon = backport.image(R.images.gui.maps.icons.quests.headerFlagIcons.mapbox_disabled())
            label = ''
        quests = [self._headerQuestFormaterVo(data is not None, progressionIcon, label, HANGAR_HEADER_QUESTS.QUEST_TYPE_MAPBOX, flag=flag, tooltip=TOOLTIPS_CONSTANTS.MAPBOX_PROGRESSION_PREVIEW, isTooltipSpecial=True)]
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_PERSONAL, '', quests)

    def __getBattleQuestsVO(self, vehicle):
        quests = self._questController.getCurrentModeQuestsForVehicle(vehicle)
        if self.__comp7Controller.isComp7PrbActive():
            quests = [ quest for quest in quests if quest.hasBonusType(constants.ARENA_BONUS_TYPE.COMP7) ]
        totalCount = len(quests)
        completedQuests = len([ q for q in quests if q.isCompleted() ])
        festivityFlagData = self._festivityController.getHangarQuestsFlagData()
        if totalCount > 0:
            if completedQuests != totalCount:
                label = _getActiveQuestLabel(totalCount, completedQuests)
            else:
                label = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE)
            commonQuestsIcon = festivityFlagData.icon or RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_AVAILABLE
        else:
            commonQuestsIcon = festivityFlagData.iconDisabled or RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_DISABLED
            label = ''
        if self.__battleRoyaleController.isBattleRoyaleMode() and totalCount > 0:
            questType = HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_ROYALE
            label = self.__getBattleRoyaleLableForQuestsTooltip(totalCount, completedQuests)
        else:
            questType = HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON
        quests = [self._headerQuestFormaterVo(totalCount > 0, commonQuestsIcon, label, questType, flag=festivityFlagData.flagBackground, tooltip=TOOLTIPS_CONSTANTS.QUESTS_PREVIEW, isTooltipSpecial=True)]
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', quests)

    def __getBattleRoyaleLableForQuestsTooltip(self, totalCount, completedQuests):
        libraryIcons = R.images.gui.maps.icons.library
        if completedQuests != totalCount:
            label = _getActiveQuestLabel(totalCount, completedQuests)
        else:
            currentCycleEndTime, _ = self.__battleRoyaleController.getCurrentCycleInfo()
            cycleTimeLeft = currentCycleEndTime - time_utils.getCurrentLocalServerTimestamp()
            if cycleTimeLeft < ONE_DAY or not self.__battleRoyaleController.isDailyQuestsRefreshAvailable():
                label = icons.makeImageTag(backport.image(libraryIcons.ConfirmIcon_1()))
            else:
                label = icons.makeImageTag(backport.image(libraryIcons.time_icon()))
        return label

    def __getRankedBattleQuestsVO(self):
        quests = self._eventsCache.getActiveQuests(lambda q: isRankedDaily(q.getID()))
        label = ''
        totalCount = len(quests)
        completedQuests = len([ q for q in quests.itervalues() if q.isCompleted() ])
        commonQuestsIcon = R.images.gui.maps.icons.library.outline.quests_disabled()
        if totalCount > 0:
            commonQuestsIcon = R.images.gui.maps.icons.library.outline.quests_available()
            diff = totalCount - completedQuests
            isLeagues = self.__rankedController.isAccountMastered()
            isAnyPrimeNow = self.__rankedController.hasAvailablePrimeTimeServers()
            isAnyPrimeLeftTotal = self.__rankedController.hasPrimeTimesTotalLeft()
            isAnyPrimeLeftNextDay = self.__rankedController.hasPrimeTimesNextDayLeft()
            if not isAnyPrimeLeftTotal or not isLeagues:
                label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.CancelIcon_1()))
            elif diff > 0:
                if isAnyPrimeNow:
                    label = backport.text(R.strings.menu.hangar_header.battle_quests_label.active(), total=diff)
                else:
                    label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.CancelIcon_1()))
            elif not isAnyPrimeLeftNextDay:
                label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.ConfirmIcon_1()))
            else:
                label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.time_icon()))
        questsVo = [self._headerQuestFormaterVo(totalCount > 0, backport.image(commonQuestsIcon), label, HANGAR_HEADER_QUESTS.QUEST_GROUP_RANKED_DAILY, flag=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_ranked()), tooltip=TOOLTIPS_CONSTANTS.RANKED_QUESTS_PREVIEW, isTooltipSpecial=True)]
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_RANKED_DAILY, '', questsVo)

    def __getMarathonQuestsVO(self, vehicle, isGroupped=False):
        marathons = self._marathonsCtrl.getMarathons()
        if marathons:
            result = []
            for index, marathonEvent in enumerate(marathons):
                flagVO = marathonEvent.getMarathonFlagState(vehicle)
                if flagVO['visible']:
                    quest = self._headerQuestFormaterVo(flagVO['enable'], flagVO['flagHeaderIcon'], '', ''.join((HANGAR_HEADER_QUESTS.QUEST_TYPE_MARATHON, str(index))), flag=flagVO['flagMain'], stateIcon=flagVO['flagStateIcon'], questID=marathonEvent.prefix, tooltip=flagVO['tooltip'], isTooltipSpecial=flagVO['enable'])
                    if not isGroupped:
                        wrappedGroup = self._wrapQuestGroup(''.join((HANGAR_HEADER_QUESTS.QUEST_GROUP_MARATHON, str(index))), '', [quest])
                    result.append(quest if isGroupped else wrappedGroup)

            if result:
                if isGroupped:
                    return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_MARATHON, RES_ICONS.MAPS_ICONS_QUESTS_HEADERFLAGICONS_MARATHONS, result)
                return result
        return None

    def __getEpicBattleQuestsVO(self):
        if not self.__epicController.isEnabled() or not self.__limitedUIController.isRuleCompleted(LuiRules.BATTLE_MISSIONS):
            return None
        else:
            quests = [ q for q in self._questController.getQuestForVehicle(g_currentVehicle.item) if isDailyEpic(q.getGroupID()) ]
            totalCount = len(quests)
            completedQuests = len([ q for q in quests if q.isCompleted() ])
            libraryIcons = R.images.gui.maps.icons.library
            commonQuestsIcon = libraryIcons.outline.quests_available()
            if not totalCount:
                commonQuestsIcon = libraryIcons.outline.quests_disabled()
                label = ''
            elif not self.__epicController.isDailyQuestsUnlocked():
                label = icons.makeImageTag(backport.image(libraryIcons.CancelIcon_1()))
            elif completedQuests != totalCount:
                label = _getActiveQuestLabel(totalCount, completedQuests)
            else:
                currentCycleEndTime, _ = self.__epicController.getCurrentCycleInfo()
                cycleTimeLeft = currentCycleEndTime - time_utils.getCurrentLocalServerTimestamp()
                if cycleTimeLeft < ONE_DAY or not self.__epicController.isDailyQuestsRefreshAvailable():
                    label = icons.makeImageTag(backport.image(libraryIcons.ConfirmIcon_1()))
                else:
                    label = icons.makeImageTag(backport.image(libraryIcons.time_icon()))
            quests = [self._headerQuestFormaterVo(totalCount > 0, backport.image(commonQuestsIcon), label, HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON, flag=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_epic()), tooltip=TOOLTIPS_CONSTANTS.EPIC_QUESTS_PREVIEW, isTooltipSpecial=True)]
            return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', quests)

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
                inSquadState = False
                if self.prbDispatcher is not None:
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

    def _wrapQuestGroup(self, groupID, icon, quests, isRightSide=False):
        return {'groupID': groupID,
         'groupIcon': icon,
         'quests': quests,
         'isRightSide': isRightSide}

    def _headerQuestFormaterVo(self, enable, icon, label, questType, flag=None, flagDisabled=None, stateIcon=None, questID=None, isReward=False, tooltip='', isTooltipSpecial=False, isTooltipWulf=False):
        return {'enable': enable,
         'flag': flag or FLAG_BY_QUEST_TYPE[questType],
         'flagDisabled': flagDisabled or RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_GRAY,
         'icon': icon,
         'stateIcon': stateIcon,
         'label': label,
         'questType': questType,
         'questID': str(questID),
         'isReward': isReward,
         'tooltip': tooltip,
         'isTooltipSpecial': isTooltipSpecial,
         'isTooltipWulf': isTooltipWulf}

    def __onSetHangarHeaderEnabled(self, _=None):
        self.update()

    def __hideHeader(self):
        return {'isVisible': False,
         'quests': []}

    def __getCurentArenaBonusType(self):
        queueType = None
        isInUnit = False
        if self.prbDispatcher is not None and self.prbEntity is not None:
            state = self.prbDispatcher.getFunctionalState()
            isInUnit = state.isInUnit(state.entityTypeID)
            queueType = self.prbEntity.getQueueType()
        return getSupportedArenaBonusTypeFor(queueType, isInUnit)

    def __updateBattlePassSmallWidget(self):
        currentArenaBonusType = self.__getCurentArenaBonusType()
        secondaryPointCanBeAvailable = currentArenaBonusType not in (constants.ARENA_BONUS_TYPE.REGULAR,
         constants.ARENA_BONUS_TYPE.UNKNOWN,
         constants.ARENA_BONUS_TYPE.MAPBOX,
         constants.ARENA_BONUS_TYPE.WINBACK)
        isRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.BP_ENTRY)
        secondaryEntryPointAvailable = secondaryPointCanBeAvailable and not self.__battlePassController.isDisabled() and isRuleCompleted
        self.as_setSecondaryEntryPointVisibleS(secondaryEntryPointAvailable)
        if secondaryEntryPointAvailable:
            self.getComponent(HANGAR_ALIASES.SECONDARY_ENTRY_POINT).update(currentArenaBonusType)

    def __updateVisibilityPersonalMission(self, isVisible):
        self.__isShowPersonalMission = isVisible

    def __updateVOHeader(self, *_):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)

    def __updateResourceWellEntryPoint(self):
        isArenaBonusTypeFit = self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.WINBACK)
        isRandom = isArenaBonusTypeFit and not self.__bootcampController.isInBootcamp()
        isLuiRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.RESOURCE_WELL)
        isResourceWellVisible = self.__resourceWell.isActive() or self.__resourceWell.isPaused() or self.__resourceWell.isNotStarted()
        showResourceWellEntryPoint = isRandom and isResourceWellVisible and isLuiRuleCompleted
        alias = HANGAR_ALIASES.RESOURCE_WELL_ENTRY_POINT if showResourceWellEntryPoint else ''
        if self.__activeWidgets.update(ActiveWidgets.RIGHT, alias):
            self.as_addSecondaryEntryPointS(alias, True)

    def __updateCollectiveGoalEntryPoint(self):
        isCollecitveGoalVisible = self.__collectiveGoalEntryPointController.isEnabled()
        isVisibleInBonusType = self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.EPIC_RANDOM)
        self.as_setCollectiveGoalEntryPointS(isCollecitveGoalVisible and isVisibleInBonusType)

    def __updateArmoryYardEntryPoint(self):
        self.as_setArmoryYardEntryPointS(self.__armoryYardCtrl.isEnabled() and self.__limitedUIController.isRuleCompleted(LuiRules.ARMORY_YARD_ENTRY_POINT) and self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.EPIC_RANDOM, constants.ARENA_BONUS_TYPE.COMP7))

    def __updateEarlyAccessEntryPoint(self):
        self.as_setEarlyAccessEntryPointS(self.__earlyAccessCtrl.isEnabled() and self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.EPIC_RANDOM, constants.ARENA_BONUS_TYPE.COMP7))

    def __updateBattleMattersEntryPoint(self):
        isRandom = self.__getCurentArenaBonusType() == constants.ARENA_BONUS_TYPE.REGULAR
        controller = self.__battleMattersController
        isLuiRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.BM_FLAG)
        isBattleMattersMShow = controller.isEnabled() and (not controller.isFinished() or controller.hasDelayedRewards()) and isRandom and isLuiRuleCompleted
        alias = HANGAR_ALIASES.BATTLE_MATTERS_ENTRY_POINT if isBattleMattersMShow else ''
        if self.__activeWidgets.update(ActiveWidgets.LEFT, alias):
            self.as_addSecondaryEntryPointS(alias, False)

    def __updateVisibilityBattleMatter(self, *_):
        self.__updateBattleMattersEntryPoint()

    def __updateResourceWell(self, *_):
        self.__updateResourceWellEntryPoint()
