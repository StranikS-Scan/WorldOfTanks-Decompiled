# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_header.py
import logging
import typing
import BigWorld
import inspect
import constants
import nations
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import WindowLayer
from gui import g_guiResetters
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.regular import missions_page
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_constants import QuestFlagTypes
from gui.Scaleform.daapi.view.meta.HangarHeaderMeta import HangarHeaderMeta
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_pass.battle_pass_helpers import getSupportedArenaBonusTypeFor
from gui.event_boards.listener import IEventBoardsListener
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import finders
from gui.server_events.events_constants import BATTLE_ROYALE_GROUPS_ID
from gui.server_events.events_constants import RANKED_DAILY_GROUP_ID
from gui.server_events.events_dispatcher import showPersonalMission, showMissionsElen, showMissionsMarathon, showPersonalMissionOperationsPage, showPersonalMissionsOperationsMap, showMissionsCategories, showMissionsBattlePass, showMissionsMapboxProgression
from gui.server_events.events_helpers import isRankedDaily, isDailyEpic
from gui.shared.event_dispatcher import showEventProgressionWindow
from gui.shared.formatters import icons
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_DAY
from personal_missions import PM_BRANCH
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IBattlePassController, IResourceWellController, IHangarGuiController, IMarathonEventsController, IFestivityController, IRankedBattlesController, IQuestsController, IBattleRoyaleController, IMapboxController, IEpicBattleMetaGameController, IFunRandomController, IComp7Controller, ILimitedUIController, ILiveOpsWebEventsController, IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.prebattle_vehicle import IPrebattleVehicle
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
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _eventsController = dependency.descriptor(IEventBoardController)
    _festivityController = dependency.descriptor(IFestivityController)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __liveOpsWebEventsController = dependency.descriptor(ILiveOpsWebEventsController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __resourceWell = dependency.descriptor(IResourceWellController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _questController = dependency.descriptor(IQuestsController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __gameEventController = dependency.descriptor(IEventBattlesController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self):
        super(HangarHeader, self).__init__()
        self._currentVehicle = None
        self.__screenWidth = None
        self.__isShowPersonalMission = True
        self.__activeWidgets = None
        self.__widgets = {wrapper.alias:wrapper for _, wrapper in inspect.getmembers(self.__class__, inspect.ismethod) if getattr(wrapper, 'alias', None)}
        return

    def onQuestBtnClick(self, questType, questID):
        _, flagsGetter = self.__hangarGuiCtrl.getHangarHeaderBlock()
        if flagsGetter is not None:
            flagsGetter.showQuestsInfo(questType, questID)
        if questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON:
            missions_page.setHideDoneFilter()
            showMissionsCategories(missionID=questID)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_GROUP_RANKED_DAILY:
            showMissionsCategories(groupID=RANKED_DAILY_GROUP_ID)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_PASS:
            showMissionsBattlePass()
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_MAPBOX:
            showMissionsMapboxProgression()
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT_BATTLES:
            showEventProgressionWindow()
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
        return

    def onUpdateHangarFlag(self):
        self.update()

    def onPrbEntitySwitched(self):
        super(HangarHeader, self).onPrbEntitySwitched()
        self.__updateBattleMattersEntryPoint()

    def update(self, *_):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)
        self.__updateWidget()
        self.__updateRightWidget()

    def updateRankedHeader(self, *_):
        self.__updateWidget()

    def updateBattleRoyaleHeader(self):
        self.__updateWidget()

    def updateEventHeader(self):
        self.__updateWidget()

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

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
        self.__liveOpsWebEventsController.onSettingsChanged += self.__updateRightWidget
        self.__liveOpsWebEventsController.onEventStateChanged += self.__updateRightWidget
        self.__battleMattersController.onStateChanged += self.__onBattleMattersStateChanged
        self.__battleMattersController.onFinish += self.__onBattleMattersStateChanged
        self.__limitedUIController.startObserve(LUI_RULES.BattlePassEntry, self.__updateBattlePassWidgetVisibility)
        self.__limitedUIController.startObserve(LUI_RULES.BattleMissions, self.__updateVOHeader)
        self.__limitedUIController.startObserve(LUI_RULES.BattleMattersFlag, self.__updateBattleMattersEntryPoint)
        self.__limitedUIController.startObserve(LUI_RULES.PersonalMissions, self.__updateVOHeader)
        self.__limitedUIController.startObserve(LUI_RULES.LiveOpsWebEventsEntryPoint, self.__updateRightWidget)
        self.__updateBattleMattersEntryPoint()
        g_clientUpdateManager.addCallbacks({'inventory.1': self.update})
        if self._eventsController:
            self._eventsController.addListener(self)
        self._marathonsCtrl.onFlagUpdateNotify += self.update
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
        self.__liveOpsWebEventsController.onEventStateChanged -= self.__updateRightWidget
        self.__liveOpsWebEventsController.onSettingsChanged -= self.__updateRightWidget
        self.__battleMattersController.onStateChanged -= self.__onBattleMattersStateChanged
        self.__battleMattersController.onFinish -= self.__onBattleMattersStateChanged
        self.__limitedUIController.stopObserve(LUI_RULES.BattlePassEntry, self.__updateBattlePassWidgetVisibility)
        self.__limitedUIController.stopObserve(LUI_RULES.BattleMissions, self.__updateVOHeader)
        self.__limitedUIController.stopObserve(LUI_RULES.BattleMattersFlag, self.__updateBattleMattersEntryPoint)
        self.__limitedUIController.stopObserve(LUI_RULES.PersonalMissions, self.__updateVOHeader)
        self.__limitedUIController.stopObserve(LUI_RULES.LiveOpsWebEventsEntryPoint, self.__updateRightWidget)
        self._currentVehicle = None
        self.__screenWidth = None
        self.__activeWidgets = None
        self.__widgets.clear()
        self.__widgets = None
        if self._eventsController:
            self._eventsController.removeListener(self)
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_guiResetters.remove(self.__onChangeScreenResolution)
        self.stopGlobalListening()
        super(HangarHeader, self)._dispose()
        return

    def _makeHeaderVO(self):
        isVisible, flagsGetter = self.__hangarGuiCtrl.getHangarHeaderBlock()
        if flagsGetter is None:
            return {'isVisible': isVisible,
             'quests': []}
        else:
            isGrouped = self.__screenWidth <= _SCREEN_WIDTH_FOR_MARATHON_GROUP
            params = {QuestFlagTypes.MARATHON: {'isGrouped': isGrouped}}
            quests = flagsGetter.getVO(self._currentVehicle.item, params)
            return {'isVisible': isVisible,
             'quests': quests}

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == HANGAR_ALIASES.WHITE_TIGER_WIDGET:
            event = viewPy.getOnEscKeyDown()
            event += self.onEscape

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == HANGAR_ALIASES.WHITE_TIGER_WIDGET and viewPy.getInjectView():
            event = viewPy.getOnEscKeyDown()
            event -= self.onEscape

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

    def __getEventQuestsToHeaderVO(self, vehicle):
        quests = []
        eventQuests = self.__getEventQuestVO(vehicle)
        if eventQuests:
            quests.append(eventQuests)
        return quests

    def __getEventQuestVO(self, vehicle):
        quests = [ q for q in self._questController.getQuestForVehicle(vehicle) if q.isEventBattlesQuest() ]
        totalCount = len(quests)
        completedQuests = len([ q for q in quests if q.isCompleted() ])
        icon = R.images.gui.maps.icons.library.outline.quests_disabled()
        flag = R.images.gui.maps.icons.library.hangarFlag.flag_gray()
        flagDisabledIcon = None
        label = ''
        stateIcon = None
        isEnabled = False
        isAnyPrimeTimeNow = self.__gameEventController.isInPrimeTime()
        if isAnyPrimeTimeNow and vehicle:
            isAnyPrimeTimeLeft = self.__gameEventController.hasPrimeTimesLeftForCurrentCycle()
            isLastSeasonDay = self.__gameEventController.isLastSeasonDay()
            eventType = vehicle.eventType
            icon = R.images.gui.maps.icons.wtevent.quests.vehicleTypes.dyn(eventType)()
            if totalCount > 0:
                diff = totalCount - completedQuests
                isEnabled = True
                allBossCompleted = totalCount == completedQuests and eventType == VEHICLE_TAGS.EVENT_BOSS
                flag = R.images.gui.maps.icons.wtevent.quests.hangarFlag.dyn(eventType)()
                if diff > 0:
                    label = backport.text(R.strings.menu.hangar_header.battle_quests_label.active(), total=diff)
                elif isAnyPrimeTimeLeft and not isLastSeasonDay and not allBossCompleted:
                    stateIcon = backport.image(R.images.gui.maps.icons.library.clock_icon_s_32())
                else:
                    stateIcon = backport.image(R.images.gui.maps.icons.library.completed_32())
            else:
                stateIcon = backport.image(R.images.gui.maps.icons.library.clock_icon_s_32())
                flagDisabledIcon = backport.image(R.images.gui.maps.icons.wtevent.quests.hangarFlag.dyn(eventType)())
        questsVO = [self._headerQuestFormaterVo(enable=isEnabled, icon=backport.image(icon), label=label, stateIcon=stateIcon, questType=HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT_BATTLES, flag=backport.image(flag), flagDisabled=flagDisabledIcon, tooltip=TOOLTIPS_CONSTANTS.EVENT_BATTLES_QUESTS_PREVIEW, isTooltipSpecial=True)]
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_EVENT_BATTLES, '', questsVO)

    def __getBPWidget(self):
        isBPAvailable = not self.__battlePassController.isDisabled()
        isValidBattleType = self.prbDispatcher and self.prbDispatcher.getEntity() and self.__battlePassController.isValidBattleType(self.prbDispatcher.getEntity())
        isRuleCompleted = self.__limitedUIController.isRuleCompleted(LUI_RULES.BattlePassEntry)
        isVisible = isBPAvailable and isValidBattleType and isRuleCompleted
        return HANGAR_ALIASES.BATTLE_PASSS_ENTRY_POINT if isVisible else ''

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

    @widgetFunc(HANGAR_ALIASES.WHITE_TIGER_WIDGET)
    def __getWTWidget(self):
        return HANGAR_ALIASES.WHITE_TIGER_WIDGET if self.__gameEventController.isEventPrbActive() else ''

    def __updateWidget(self):
        alias = self.__hangarGuiCtrl.getHangarWidgetAlias() or self.__getBPWidget() or self.__getWTWidget()
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

    def __onServerSettingChanged(self, diff):
        if 'elenSettings' in diff or constants.PremiumConfigs.PREM_QUESTS in diff:
            self.update()

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
        if not self.__epicController.isEnabled() or not self.__limitedUIController.isRuleCompleted(LUI_RULES.BattleMissions):
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
        isRuleCompleted = self.__limitedUIController.isRuleCompleted(LUI_RULES.BattlePassEntry)
        secondaryEntryPointAvailable = secondaryPointCanBeAvailable and not self.__battlePassController.isDisabled() and isRuleCompleted
        self.as_setSecondaryEntryPointVisibleS(secondaryEntryPointAvailable)
        if secondaryEntryPointAvailable:
            self.getComponent(HANGAR_ALIASES.SECONDARY_ENTRY_POINT).update(currentArenaBonusType)

    def __updateVisibilityPersonalMission(self, isVisible):
        self.__isShowPersonalMission = isVisible

    def __updateVOHeader(self, *_):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)

    def __updateRightWidget(self, *_):
        isRandom = self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.WINBACK)
        alias = ''
        if isRandom:
            if self.__resourceWell.isActive() or self.__resourceWell.isPaused() or self.__resourceWell.isNotStarted():
                alias = HANGAR_ALIASES.RESOURCE_WELL_ENTRY_POINT
            elif self.__liveOpsWebEventsController.canShowHangarEntryPoint() and self.__limitedUIController.isRuleCompleted(LUI_RULES.LiveOpsWebEventsEntryPoint):
                alias = HANGAR_ALIASES.LIVE_OPS_WEB_EVENTS_ENTRY_POINT
        if self.__activeWidgets.update(ActiveWidgets.RIGHT, alias):
            self.as_addSecondaryEntryPointS(alias, True)

    def __updateBattleMattersEntryPoint(self, *_):
        isValidArena = self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.WINBACK)
        controller = self.__battleMattersController
        isLuiRuleCompleted = self.__limitedUIController.isRuleCompleted(LUI_RULES.BattleMattersFlag)
        isBattleMattersMShow = controller.isEnabled() and (not controller.isFinished() or controller.hasDelayedRewards()) and isValidArena and isLuiRuleCompleted
        alias = HANGAR_ALIASES.BATTLE_MATTERS_ENTRY_POINT if isBattleMattersMShow else ''
        if self.__activeWidgets.update(ActiveWidgets.LEFT, alias):
            self.as_addSecondaryEntryPointS(alias, False)
