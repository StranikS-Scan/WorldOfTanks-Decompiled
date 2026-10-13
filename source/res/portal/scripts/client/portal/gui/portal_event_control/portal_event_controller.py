# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/portal_event_control/portal_event_controller.py
import copy
import AccountCommands
import Event
import logging
import nations
import typing
import BigWorld
from items import vehicles
from adisp import adisp_process
from account_helpers import AccountSettings
from account_helpers.portal import Portal
from account_helpers.AccountSettings import PORTAL_VEHICLE, CURRENT_VEHICLE
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from shared_utils import makeTupleByDict, first
from helpers import dependency, time_utils, int2roman
from PlayerEvents import g_playerEvents
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen_utils import INVALID_RES_ID
from gui.game_control.season_provider import SeasonProvider
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui import SystemMessages
from gui.shared.notifications import NotificationPriorityLevel
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, EventPriority
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.event_dispatcher import showHangar
from tutorial.control.context import GLOBAL_FLAG
from skeletons.gui.game_control import IHangarSpaceSwitchController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.shared import IItemsCache
from portal.sounds.sound_helpers import play2DSound
from portal_account_settings import getSelectedComplexityLevel, setSelectedComplexityLevel, setOutroVideoViewed, setIntroVideoViewed, isIntroVideoViewed, isPortalFinishedNotificationViewed, setPortalFinishedNotificationViewed, setPortalStartedNotificationViewed, isPortalStartedNotificationViewed, resetViewedVehicleUpgradesStages, getPortalLastSeasonID, setPortalLastSeasonID
from portal.gui.portal_event_helpers import EXECUTE_AFTER_ALL_EVENT_VEHICLES_LOADED, LAST_LEVEL_QUEST
from portal.gui.portal_gui_constants import PREBATTLE_ACTION_NAME
from portal.gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from portal.gui.shared import event_dispatcher
from portal.gui.shared.events import PortalComplexity
from portal.gui.impl.gen.view_models.views.lobby.portal_complexity_level import ComplexityLevelStatus
from portal.gui.shared.event_dispatcher import showVideo
from portal.skeletons.portal_event_controller import IPortalEventController
from portal_common.portal_constants import PORTAL_GAME_PARAMS_KEY, QUEUE_TYPE, PREBATTLE_TYPE, PORTAL_BATTLE_LEVELS_TO_VEHICLE_LEVELS, PORTAL_VEHICLE_UPGRADES_KEY, PORTAL_VEHICLE_EXPERIENCE_KEY, PORTAL_MAX_COMPLEXITY_KEY
from portal_common.portal_account_helpers.vehicle_upgrade_tree import VehicleUpgradeTreeSerializer
from portal_constants import PORTAL_HANGAR_SCENE, PORTAL_VIDEO, PORTAL_HANGAR_SPACE_PATH
from portal.sounds.sound_constants import PortalMusicState, PortalBattleUISound
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Tuple, Type
    from PortalAccountComponent import PortalAccountComponent
    from Vehicle import Vehicle
    from items.artefacts import Equipment
    from gui.shared.events import LoadViewEvent, HasCtxEvent
    from gui.server_events.bonuses import SimpleBonus
    from gui.prb_control.dispatcher import _PreBattleDispatcher
    from helpers.server_settings import ServerSettings
_logger = logging.getLogger(__name__)
_PORTAL_VEHICLES_ORDER = (nations.INDICES['poland'],
 nations.INDICES['ussr'],
 nations.INDICES['france'],
 nations.INDICES['uk'])

class _PortalConfig(namedtuple('_PortalConfig', ('isEnabled', 'isBattleEnabled', 'realmConfig', 'seasons', 'cycleTimes', 'stamp', 'progression', 'medals', 'badges', 'primeTimes', 'peripheryIDs'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isBattleEnabled=False, realmConfig={}, seasons={}, cycleTimes={}, stamp='', progression=[], medals=[], badges=[], primeTimes={}, peripheryIDs={})
        defaults.update(kwargs)
        return super(_PortalConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class PortalEventController(IPortalEventController, PerformanceAnalyzerMixin, Notifiable, SeasonProvider, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(PortalEventController, self).__init__()
        self.__serverSettings = None
        self.__eventConfig = None
        self.__maxComplexityLevel = None
        self.__maxAvailableComplexityLevel = None
        self.__battleLevel = getSelectedComplexityLevel()
        self.__selectedVehicle = None
        self.__isEnabled = None
        self.__needToShowComplexityUnlock = False
        self.__inPortalLobby = False
        self.__lastSuspended = False
        self.__lastFrozen = False
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onPortalBattleConfigChanged = Event.Event()
        self.onVehicleUpgradesMasksChanged = Event.Event()
        self.onVehicleExperienceChanged = Event.Event()
        self.onComplexityLevelChanged = Event.Event()
        self.onMaxAvailableComplexityLevelChanged = Event.Event()
        self.onPortalSquadStateChanged = Event.Event()
        return

    def init(self):
        super(PortalEventController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.__spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreated

    def fini(self):
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        super(PortalEventController, self).fini()

    @property
    def account(self):
        return getattr(BigWorld.player(), 'PortalAccountComponent', None)

    @property
    def portal(self):
        return getattr(BigWorld.player(), 'portal', None)

    def onLobbyInited(self, event):
        super(PortalEventController, self).onLobbyInited(event)
        self.startGlobalListening()

    def showIntroVideo(self):
        setIntroVideoViewed(True)
        showVideo(PORTAL_VIDEO.INTRO, R.subtitles.portal.portal_intro_vp8_8_128())

    def showOutroVideo(self):
        setOutroVideoViewed(True)
        showVideo(PORTAL_VIDEO.OUTRO, INVALID_RES_ID)

    def isOutroVideoAvailable(self):
        lastLevelQuest = self.__eventsCache.getQuestByID(LAST_LEVEL_QUEST)
        return lastLevelQuest.isCompleted() if lastLevelQuest is not None else False

    def onPrbEnter(self):
        self.__inPortalLobby = True
        g_eventBus.addListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY, priority=EventPriority.VERY_LOW)
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onHangarVehicleSelected, EVENT_BUS_SCOPE.LOBBY)

    def onPrbLeave(self):
        self.__inPortalLobby = False
        self.__removePrbListeners()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.PORTAL_ACTIVE, False)
        play2DSound(PortalMusicState.EXIT)

    def onDisconnected(self):
        super(PortalEventController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(PortalEventController, self).onAvatarBecomePlayer()
        if self.__inPortalLobby:
            play2DSound(PortalBattleUISound.HANGAR_EXIT)
            self.__inPortalLobby = False
        self.__clear()

    def onAccountBecomePlayer(self):
        super(PortalEventController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        if self.isEnabled:
            self.__addListeners()

    def onAccountBecomeNonPlayer(self):
        super(PortalEventController, self).onAccountBecomeNonPlayer()
        self.__removeListeners()

    def onPrbEntitySwitching(self):
        if self.isPortalMode():
            play2DSound(PortalBattleUISound.HANGAR_EXIT)

    def onPrbEntitySwitched(self):
        if self.isPortalMode():
            PortalMusicState.setState(PortalMusicState.LOBBY)
            self.__onPrbEntitySwitchedToEvent()

    def isEnabled(self):
        return self.__eventConfig.isEnabled

    def getEventStartTime(self):
        season = self.getCurrentSeason() or self.getNextSeason()
        return float(season.getStartDate()) if season else 0.0

    def getEventFinishTime(self):
        season = self.getCurrentSeason() or self.getNextSeason()
        return float(season.getEndDate()) if season else 0.0

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isBattleAvailable(self):
        return self.__eventConfig.isBattleEnabled if self.__eventConfig else False

    def isFrozen(self):
        return not self.isEnabled() and self.getCurrentSeason() is not None

    def isTemporaryUnavailable(self):
        return self.getCurrentSeason() is not None and (not self.isEnabled() or not self.isBattleAvailable())

    def isPortalMode(self):
        if self.prbDispatcher is None:
            return False
        else:
            state = self.prbDispatcher.getFunctionalState()
            return self.__isPortalMode(state)

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings()[PORTAL_GAME_PARAMS_KEY]

    def getModeSettings(self):
        if self.__eventConfig is None:
            self.__setEventConfig(self.__lobbyContext.getServerSettings().getSettings())
        return self.__eventConfig

    @property
    def battleLevel(self):
        return self.__battleLevel

    @battleLevel.setter
    def battleLevel(self, battleLevel):
        if self.prbDispatcher and self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.PORTAL):
            self.prbEntity.setBattleLevel(battleLevel)
            return
        self.__setBattleLevel(battleLevel)

    @property
    def maxComplexityLevel(self):
        return self.__maxComplexityLevel

    def setMaxAvailableComplexityLevel(self, maxAvaiableComplexityLevel):
        self.__maxAvailableComplexityLevel = maxAvaiableComplexityLevel
        self.onMaxAvailableComplexityLevelChanged()
        if self.__maxAvailableComplexityLevel and self.battleLevel > self.__maxAvailableComplexityLevel:
            self.battleLevel = self.__maxAvailableComplexityLevel

    def onSquadBattleLevelChanged(self, battleLevel):
        self.__setBattleLevel(battleLevel)

    @adisp_process
    def selectRandomBattle(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result:
                showHangar()
        else:
            _logger.error('Prebattle dispatcher is not defined.')
        return

    @adisp_process
    def doSelectEventPrbAndCallback(self, callback):
        if self.isPortalMode():
            callback()
            return
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            return
        result = yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.PORTAL_BATTLE))
        if result:
            callback()

    def selectPortal(self):
        if not self.isEnabled():
            return
        else:
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is None:
                _logger.error('Prebattle dispatcher for loading portal hangar is not defined')
                return
            self.__selectPortalPrebattleAction(dispatcher)
            return

    def getOrderedPortalVehicles(self):
        portalVehicles = sorted(self.__itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.PORTAL])).values(), key=lambda veh: _PORTAL_VEHICLES_ORDER.index(veh.nationID))
        return portalVehicles

    def setCurrentSelectedVehicle(self, vehicleID):
        portalVehicles = self.getOrderedPortalVehicles()
        selectedVehicle = next((veh for veh in portalVehicles if veh.invID == vehicleID), None)
        g_currentVehicle.selectVehicle(selectedVehicle.invID)
        return

    def selectNextPortalVehicle(self):
        portalVehicles = [ veh for veh in self.getOrderedPortalVehicles() if not veh.isLocked ]
        currentVehIndex = list.index([ portalVehicle.intCD for portalVehicle in portalVehicles ], g_currentVehicle.item.intCD)
        self.setCurrentSelectedVehicle(portalVehicles[(currentVehIndex + 1) % len(portalVehicles)].invID)

    def selectPrevPortalVehicle(self):
        portalVehicles = [ veh for veh in self.getOrderedPortalVehicles() if not veh.isLocked ]
        currentVehIndex = list.index([ portalVehicle.intCD for portalVehicle in portalVehicles ], g_currentVehicle.item.intCD)
        self.setCurrentSelectedVehicle(portalVehicles[(currentVehIndex - 1) % len(portalVehicles)].invID)

    def getPortalVehicleByInvID(self, invID):
        portalVehicles = self.getOrderedPortalVehicles()
        return next((veh for veh in portalVehicles if veh.invID == invID), None)

    def getCurrentSelectedVehicle(self):
        if g_currentVehicle.item is None or not g_currentVehicle.item.isOnlyForPortalBattlesVehicle and self.isPortalMode():
            self.__preSelectPortalVehicle()
        return g_currentVehicle.item

    def getComplexityLevelStatus(self, level):
        if self.__maxAvailableComplexityLevel:
            if self.__maxAvailableComplexityLevel < level <= self.__maxComplexityLevel:
                return ComplexityLevelStatus.LOCKED_BY_SQUAD
        if self.__maxComplexityLevel < level:
            return ComplexityLevelStatus.LOCKED
        return ComplexityLevelStatus.SELECTED if self.__battleLevel == level else ComplexityLevelStatus.DEFAULT

    def isComplexityLevelLocked(self, level):
        return ComplexityLevelStatus.LOCKED == self.getComplexityLevelStatus(level)

    def getComplexityRecommendedVehicleLvl(self, level):
        return PORTAL_BATTLE_LEVELS_TO_VEHICLE_LEVELS.get(int(level), 9)

    def getVehicleAbilities(self, vehicle, includeLocked=False):
        config = self.getConfig()
        combatEntities = config.get('combatEntities', {})
        abilitiesList = list()
        for entity in combatEntities.values():
            portalVehicles = entity.get('vehicles', {})
            if vehicle.name in portalVehicles:
                abilitiesList = copy.copy(portalVehicles[vehicle.name].get('abilities', []))

        deserializedTree = VehicleUpgradeTreeSerializer.deserializeTree(self.getVehicleUpgradeTree(vehicle))
        upgradeNodes = self.getVehicleUpgradeNodes(vehicle)
        unlockedAbilities = []
        for level in upgradeNodes:
            levelUpgrades = upgradeNodes[level].get('nodes', None)
            if levelUpgrades is None:
                _logger.error('There is no upgrade items for %s %s', vehicle.name, level)
                return []
            isLeftNodeResearched = deserializedTree.get(level, {}).get('leftNode', False)
            isRightNodeResearched = deserializedTree.get(level, {}).get('rightNode', False)
            if isLeftNodeResearched and levelUpgrades[0]['abilities'] or includeLocked:
                unlockedAbilities.extend(levelUpgrades[0]['abilities'])
            if isRightNodeResearched and levelUpgrades[1]['abilities'] or includeLocked:
                unlockedAbilities.extend(levelUpgrades[1]['abilities'])

        abilitiesList.extend(unlockedAbilities)
        return abilitiesList

    def getVehicleModifiers(self, vehicle):
        deserializedTree = VehicleUpgradeTreeSerializer.deserializeTree(self.getVehicleUpgradeTree(vehicle))
        upgradeNodes = self.getVehicleUpgradeNodes(vehicle)
        modifiers = []
        for level in deserializedTree:
            levelUpgrades = upgradeNodes[level].get('nodes', None)
            if levelUpgrades is None:
                _logger.error('There is no upgrade items for %s %s', vehicle.name, level)
                return []
            if deserializedTree[level]['leftNode'] and levelUpgrades[0]['vehicleModifiers']:
                modifiers.extend(levelUpgrades[0]['vehicleModifiers'])
            if deserializedTree[level]['rightNode'] and levelUpgrades[1]['vehicleModifiers']:
                modifiers.extend(levelUpgrades[1]['vehicleModifiers'])

        return modifiers

    def getCurrentStampsCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.__eventConfig.stamp)

    def getCurrentStampsAtLevel(self, level):
        if level < 1 or level > self.getTotalLevelsCount():
            return 0
        stampsNeeded = self.getStampsNeededForStage(level)
        if not stampsNeeded:
            return 0
        currentStamps = self.getCurrentStampsCount()
        finishedLevels = self.getFinishedLevelsCount()
        if level <= finishedLevels:
            return stampsNeeded
        if level == finishedLevels + 1:
            baseline = self.__getCumulativeStampsAfterCompletedStages(finishedLevels)
            return max(0, min(currentStamps - baseline, stampsNeeded))

    def getTotalLevelsCount(self):
        return len(self.__eventConfig.progression)

    def getProgression(self):
        return self.__eventConfig.progression

    def getFinishedLevelsCount(self):
        finished = 0
        for stage in self.__getSortedProgressionStages():
            questID = stage.get('quest', '')
            quests = self.__eventsCache.getAllQuests(lambda q, qid=questID: q.getID() == qid)
            quest = quests.get(questID)
            if quest is None or not quest.isCompleted():
                break
            finished += 1

        return finished

    def getCurrentLevel(self):
        finishedLevelsCount = self.getFinishedLevelsCount()
        totalLevels = self.getTotalLevelsCount()
        return min(finishedLevelsCount + 1, totalLevels)

    def getDeserializedUpgradeTreeLevel(self, vehicle, level):
        deserializedTreeLevel = VehicleUpgradeTreeSerializer.deserializeTreeLevel(self.getVehicleUpgradeTree(vehicle), level)
        return deserializedTreeLevel

    def getUpgradeLevel(self, vehicle):
        deserializedUpgradeTree = VehicleUpgradeTreeSerializer.deserializeTree(self.getVehicleUpgradeTree(vehicle))
        return len(deserializedUpgradeTree)

    def getMaxUnlockedLevel(self, vehicle):
        currentExp = self.getVehicleExperience(vehicle)
        currentLevel = self.getUpgradeLevel(vehicle)
        upgradeNodes = sorted(((k, v) for k, v in self.getVehicleUpgradeNodes(vehicle).items() if k >= currentLevel))
        requiredPointsTotal = 0
        for level, nodeData in upgradeNodes:
            requiredPointsTotal += nodeData.get('requiredPoints', 0)
            if currentExp < requiredPointsTotal:
                return level - 1

    def getCurrentVehicleLevel(self, vehicle):
        return self.getUpgradeLevel(vehicle) + 1

    def canUpgradeVehicle(self, vehicle):
        currentLevel = self.getUpgradeLevel(vehicle)
        vehExp = self.getVehicleExperience(vehicle)
        upgradeNodes = self.getVehicleUpgradeNodes(vehicle)
        neededPoints = upgradeNodes.get(currentLevel, {}).get('requiredPoints', None)
        return neededPoints and vehExp >= neededPoints

    def getQuestRewards(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda quest, qid=questID: quest.getID() == qid)
        quest = quests.get(questID)
        return [] if quest is None else quest.getBonuses()

    def getStampsNeededForStage(self, level):
        cur = self.__getCumulativeTokenThresholdForProgressionLevel(level)
        prev = self.__getCumulativeTokenThresholdForProgressionLevel(level - 1)
        return max(0, cur - prev)

    def getSeasonStartEndDate(self):
        season = self.getCurrentSeason() if self.getCurrentSeason() else self.getNextSeason()
        return (season.getStartDate(), season.getEndDate())

    def getAbilityDuration(self, abilityName):
        equipment = self.__getPortalEquipment(abilityName)
        return -1 if not equipment else equipment.duration

    def getAbilityCooldown(self, abilityName):
        equipment = self.__getPortalEquipment(abilityName)
        return -1 if not equipment else equipment.cooldownSeconds

    def getMedals(self):
        return self.__eventConfig.medals

    def getBadges(self):
        return self.__eventConfig.badges

    def upgradeCurrentVehicle(self, upgradeNodeNumber):
        self.account.upgradeVehicle(g_currentVehicle.invID, g_currentVehicle.item.compactDescr, upgradeNodeNumber, self.__onUpgradeVehicleCmdResponseReceived)

    def resetCurrentVehicleUpgrades(self):
        self.account.resetVehicleUpgrades(g_currentVehicle.invID, g_currentVehicle.item.compactDescr, self.__onUpgradeReset)
        resetViewedVehicleUpgradesStages(g_currentVehicle.intCD)

    def getVehicleUpgradeTree(self, vehicle):
        return self.portal.getVehicleUpgradeTree(vehicle)

    def getVehicleUpgradeNodes(self, vehicle):
        config = self.getConfig()
        vehicleUpgradesList = config.get('vehicleUpgradeNodes', {})
        upgradeNodes = {}
        for name, vehicleUpgrades in vehicleUpgradesList.items():
            vehicleName = vehicle.name.split(':')[-1]
            if vehicleName == name:
                upgradeNodes = vehicleUpgrades
                break

        if not upgradeNodes:
            _logger.error('There is no upgrade nodes for  %s', vehicle.name)
            return {}
        return upgradeNodes

    def getVehicleExperience(self, vehicle):
        return self.portal.getVehicleExperience(vehicle)

    def showComplexityUnlock(self):
        if self.__needToShowComplexityUnlock:
            event_dispatcher.showComplexityUnlockedView(self.__maxComplexityLevel)
            self.__needToShowComplexityUnlock = False

    @EXECUTE_AFTER_ALL_EVENT_VEHICLES_LOADED
    def __onPrbEntitySwitchedToEvent(self):
        if not isIntroVideoViewed():
            self.showIntroVideo()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.PORTAL_ACTIVE, True)

    def __viewLoaded(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.onPrbEntitySwitched()

    def __addListeners(self):
        g_eventBus.addListener(PortalComplexity.UNLOCKED, self.__onMaxComplexityLevelChanged, scope=EVENT_BUS_SCOPE.DEFAULT)

    def __removeListeners(self):
        g_eventBus.removeListener(PortalComplexity.UNLOCKED, self.__onMaxComplexityLevelChanged, scope=EVENT_BUS_SCOPE.DEFAULT)

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        self.__setEventConfig(self.__serverSettings.getSettings())
        self.__resetTimer()
        return

    def __updateEventBattlesSettings(self, diff):
        if PORTAL_GAME_PARAMS_KEY in diff:
            wasPortalBattleSuspended = self.isTemporaryUnavailable()
            wasPortalFrozen = self.isFrozen()
            self.__setEventConfig(diff)
            isPortalBattleSuspended = self.isTemporaryUnavailable()
            if isPortalBattleSuspended != wasPortalBattleSuspended:
                self.__onBattleSwitchChanged(isPortalBattleSuspended)
            isPortalFrozen = self.isFrozen()
            if isPortalFrozen != wasPortalFrozen:
                self.__onFrozenStateChanged(isPortalFrozen)
            self.__resetTimer()
            self.onPortalBattleConfigChanged(diff)

    def __clear(self):
        self.__removePrbListeners()
        self.stopGlobalListening()
        self.stopNotification()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        self.__eventConfig = None
        return

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        season = self.getCurrentSeason()
        currentSeasonID = season.getSeasonID() if season else 0
        lastSeasonID = getPortalLastSeasonID()
        if currentSeasonID != lastSeasonID:
            if currentSeasonID != 0:
                setPortalStartedNotificationViewed(False)
                setPortalFinishedNotificationViewed(False)
                setPortalLastSeasonID(currentSeasonID)
                self.__lastSuspended = False
                self.__lastFrozen = False
            else:
                setPortalLastSeasonID(0)
        isPortalActive = self.isAvailable()
        if isPortalActive:
            if not isPortalStartedNotificationViewed():
                SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.enabled.body()), type=SystemMessages.SM_TYPE.PortalEventEnabled, priority=NotificationPriorityLevel.MEDIUM)
                setPortalStartedNotificationViewed(True)
        elif season is None and isPortalStartedNotificationViewed():
            if not isPortalFinishedNotificationViewed():
                SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.disabled.body()), type=SystemMessages.SM_TYPE.PortalEventDisabled, priority=NotificationPriorityLevel.MEDIUM)
                setPortalFinishedNotificationViewed(True)
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)
        return

    def __onCheckSceneChange(self):
        if self.isPortalMode():
            self.__preSelectPortalVehicle()
            self.__spaceSwitchController.hangarSpaceUpdate(PORTAL_HANGAR_SCENE)
        else:
            self.__unSelectPortalVehicle()

    def __preSelectPortalVehicle(self):
        portalVehicleID = AccountSettings.getFavorites(PORTAL_VEHICLE)
        if not portalVehicleID or self.__itemsCache.items.getVehicle(portalVehicleID) is None:
            portalVehicles = self.getOrderedPortalVehicles()
            portalVehicle = first(portalVehicles)
            if portalVehicle:
                portalVehicleID = portalVehicle.invID
        if portalVehicleID:
            g_currentVehicle.selectVehicle(portalVehicleID)
        else:
            g_currentVehicle.selectNoVehicle()
        return

    def __unSelectPortalVehicle(self):
        if g_currentVehicle.item not in self.getOrderedPortalVehicles():
            return
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        if not storedVehInvID:
            criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
            criteria |= ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE])
            vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if vehicle:
                storedVehInvID = vehicle.invID
        if storedVehInvID:
            g_currentVehicle.selectVehicle(storedVehInvID)
        else:
            g_currentVehicle.selectNoVehicle()

    def __isPortalMode(self, state):
        return state.isInPreQueue(queueType=QUEUE_TYPE.PORTAL) or state.isInUnit(PREBATTLE_TYPE.PORTAL)

    @adisp_process
    def __selectPortalPrebattleAction(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.PORTAL_BATTLE))

    def __getProgressionQuestCumulativeTokenThreshold(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda q, qid=questID: q.getID() == qid)
        quest = quests.get(questID)
        if quest is None:
            return 0
        else:
            items = quest.accountReqs.getConditions().items
            return 0 if not items else int(items[0].getNeededCount())

    def __getCumulativeTokenThresholdForProgressionLevel(self, level):
        if level < 1:
            return 0
        for stage in self.__getSortedProgressionStages():
            if stage.get('level') == level:
                return self.__getProgressionQuestCumulativeTokenThreshold(stage.get('quest', ''))

    def __getSortedProgressionStages(self):
        return sorted(self.__eventConfig.progression, key=lambda s: s['level'])

    def __getCumulativeStampsAfterCompletedStages(self, completedStageCount):
        if completedStageCount <= 0:
            return 0
        stages = self.__getSortedProgressionStages()
        idx = min(completedStageCount, len(stages)) - 1
        level = stages[idx]['level']
        return self.__getCumulativeTokenThresholdForProgressionLevel(level)

    def __onClientUpdated(self, diff, _):
        portalSection = diff.get('portal', {})
        if not portalSection:
            return
        else:
            vehicleUpgradesMasks = portalSection.get(PORTAL_VEHICLE_UPGRADES_KEY, {})
            vehicleExperience = portalSection.get(PORTAL_VEHICLE_EXPERIENCE_KEY, {})
            maxComplexityLevel = portalSection.get(PORTAL_MAX_COMPLEXITY_KEY, None)
            if vehicleUpgradesMasks:
                self.onVehicleUpgradesMasksChanged(vehicleUpgradesMasks)
            if vehicleExperience:
                self.onVehicleExperienceChanged(vehicleExperience)
            if maxComplexityLevel is not None:
                self.__maxComplexityLevel = maxComplexityLevel
                self.battleLevel = maxComplexityLevel
            return

    def __getPortalEquipment(self, equipmentName):
        cache = vehicles.g_cache
        eqID = cache.equipmentIDs().get(equipmentName)
        equipment = cache.equipments().get(eqID) if eqID else None
        return equipment if equipment is not None and 'portal_ability' in equipment.tags else None

    def __onMaxComplexityLevelChanged(self, event):
        maxComplexityLevel = event.ctx['level']
        self.__maxComplexityLevel = maxComplexityLevel
        self.battleLevel = maxComplexityLevel
        self.__needToShowComplexityUnlock = True

    def __setEventConfig(self, settings):
        if PORTAL_GAME_PARAMS_KEY in settings:
            config = makeTupleByDict(_PortalConfig, settings[PORTAL_GAME_PARAMS_KEY])
        else:
            config = _PortalConfig.defaults()
        self.__eventConfig = config

    def __onUpgradeVehicleCmdResponseReceived(self, resultID, requestCode, errorStr, extDataStr=None):
        if requestCode != AccountCommands.RES_SUCCESS:
            return
        elif not extDataStr:
            return
        else:
            serviceChannelRes = R.strings.portal_messenger.serviceChannelMessages.vehicleUpgrade.levelUpgrade
            upgradeLevel = extDataStr.get('upgradeLevel')
            abilities = extDataStr.get('abilities')
            modules = extDataStr.get('modules')
            vehCD = extDataStr.get('vehCD')
            vehicleModifiers = extDataStr.get('vehicleModifiers')
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            spentPoints = extDataStr.get('spentPoints')
            formattedList = []
            vehicleStr = backport.text(serviceChannelRes.common.body(), vehicleName=vehicle.userName, upgradeLevel=int2roman(upgradeLevel + 2))
            formattedList.append(vehicleStr)
            for moduleCD in modules:
                text = backport.text(serviceChannelRes.modules.body(), moduleName=self.__itemsCache.items.getItemByCD(moduleCD).userName)
                formattedList.append(text)

            for ability in abilities:
                cache = vehicles.g_cache
                abilityID = cache.equipmentIDs().get(ability)
                abilityItem = cache.equipments().get(abilityID) if abilityID else None
                text = backport.text(serviceChannelRes.abilities.body(), abilityName=abilityItem.userString)
                formattedList.append(text)

            for vehicleModifier in vehicleModifiers:
                buffType = vehicleModifier.get('type', '').replace('/', '_')
                if buffType:
                    text = backport.text(serviceChannelRes.battleModifier.dyn(buffType)())
                    formattedList.append(text)

            SystemMessages.pushMessage(text='{0}'.format('\n'.join(formattedList)), messageData={'points': spentPoints}, type=SystemMessages.SM_TYPE.PortalVehicleUpgrade, priority=NotificationPriorityLevel.MEDIUM)
            return

    def __onBattleSwitchChanged(self, isSuspended):
        if isPortalFinishedNotificationViewed():
            return
        elif isSuspended == self.__lastSuspended:
            return
        else:
            self.__lastSuspended = isSuspended
            if isSuspended and self.getCurrentSeason() is not None:
                SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.suspended()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
            return

    def __onFrozenStateChanged(self, isFrozen):
        if isPortalFinishedNotificationViewed() or self.getCurrentSeason() is None:
            return
        elif isFrozen == self.__lastFrozen:
            return
        else:
            self.__lastFrozen = isFrozen
            if isFrozen:
                SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.eventLocked()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
            else:
                if not isPortalStartedNotificationViewed():
                    return
                SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.eventUnlocked()), priority=NotificationPriorityLevel.MEDIUM)
            return

    def __onUpgradeReset(self, resultID, requestCode, errorStr, extData=None):
        if not extData:
            return
        points = extData.get('vehicleUpgradePoints')
        SystemMessages.pushMessage('', messageData={'points': points}, type=SystemMessages.SM_TYPE.PortalResetVehicleUpgrade, priority=NotificationPriorityLevel.MEDIUM)

    def __onSpaceCreated(self):
        if self.__hangarSpace.spacePath == PORTAL_HANGAR_SPACE_PATH:
            play2DSound(PortalMusicState.EXIT)
            play2DSound(PortalMusicState.ENTER)

    def __onHangarVehicleSelected(self, event):
        vehicle = self.__itemsCache.items.getVehicle(event.ctx['vehicleInvID'])
        if vehicle and PORTAL_VEHICLE not in vehicle.tags:
            self.selectRandomBattle()

    def __setBattleLevel(self, battleLevel):
        if self.__battleLevel != battleLevel:
            setSelectedComplexityLevel(battleLevel)
            self.__battleLevel = battleLevel
            self.onComplexityLevelChanged(self.battleLevel)

    def __removePrbListeners(self):
        g_eventBus.removeListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onHangarVehicleSelected, EVENT_BUS_SCOPE.LOBBY)
