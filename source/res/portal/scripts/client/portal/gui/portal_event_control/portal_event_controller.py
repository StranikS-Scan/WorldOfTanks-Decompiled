# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/portal_event_control/portal_event_controller.py
import copy
import Event
import logging
import nations
import math
import typing
import BigWorld
from items import vehicles
import AccountCommands
from adisp import adisp_process
from account_helpers import AccountSettings
from account_helpers.portal import Portal
from account_helpers.AccountSettings import PORTAL_VEHICLE, CURRENT_VEHICLE
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from gui.impl import backport
from gui.game_control.season_provider import SeasonProvider
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui import SystemMessages
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, time_utils, int2roman
from PlayerEvents import g_playerEvents
from portal.gui.portal_event_helpers import EXECUTE_AFTER_ALL_EVENT_VEHICLES_LOADED
from portal.sounds.sound_helpers import play2DSound
from portal_account_settings import getSelectedComplexityLevel, setSelectedComplexityLevel, setOutroVideoViewed, setIntroVideoViewed, isIntroVideoViewed, isPortalFinishedNotificationViewed, setPortalFinishedNotificationViewed, setPortalStartedNotificationViewed, isPortalStartedNotificationViewed, resetViewedVehicleUpgradesStages
from portal.gui.portal_gui_constants import PREBATTLE_ACTION_NAME
from portal.gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from portal.gui.shared import event_dispatcher
from portal.skeletons.portal_event_controller import IPortalEventController
from portal_common.portal_constants import PORTAL_GAME_PARAMS_KEY, QUEUE_TYPE, PREBATTLE_TYPE, PORTAL_BATTLE_LEVELS_TO_VEHICLE_LEVELS, PORTAL_VEHICLE_UPGRADES_KEY, PORTAL_VEHICLE_EXPERIENCE_KEY, PORTAL_MAX_COMPLEXITY_KEY
from portal_common.portal_account_helpers.vehicle_upgrade_tree import VehicleUpgradeTreeSerializer
from portal_constants import PORTAL_HANGAR_SCENE, PORTAL_VIDEO, PORTAL_HANGAR_SPACE_PATH
from shared_utils import makeTupleByDict, first
from skeletons.gui.game_control import IHangarSpaceSwitchController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, EventPriority
from portal.gui.impl.gen.view_models.views.lobby.portal_complexity_level import ComplexityLevelStatus
from portal.gui.shared.event_dispatcher import showVideo
from gui.shared.event_dispatcher import showHangar
from tutorial.control.context import GLOBAL_FLAG
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from portal.sounds.sound_constants import PortalMusicState, PortalBattleUISound
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)
_PORTAL_VEHICLES_ORDER = (nations.INDICES['poland'],
 nations.INDICES['ussr'],
 nations.INDICES['france'],
 nations.INDICES['uk'])
if typing.TYPE_CHECKING:
    from PortalAccountComponent import PortalAccountComponent

class _PortalConfig(namedtuple('_PortalConfig', ('isEnabled', 'isBattleEnabled', 'realmConfig', 'seasons', 'cycleTimes', 'stamp', 'progression', 'medals', 'badges', 'stampsPerProgressionStage', 'primeTimes', 'peripheryIDs'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isBattleEnabled=False, realmConfig={}, seasons={}, cycleTimes={}, stamp='', progression=[], medals=[], badges=[], stampsPerProgressionStage=0, primeTimes={}, peripheryIDs={})
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
        self.__vehicleUpgradeMasks = {}
        self.__vehiclesExperience = {}
        self.__isEnabled = None
        self.__needToShowComplexityUnlock = False
        self.__inPortalLobby = False
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

    @EXECUTE_AFTER_ALL_EVENT_VEHICLES_LOADED
    def __onPrbEntitySwitchedToEvent(self):
        PortalMusicState.setState(PortalMusicState.LOBBY)
        if not isIntroVideoViewed():
            self.showIntroVideo()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.PORTAL_ACTIVE, True)

    def showIntroVideo(self):
        setIntroVideoViewed(True)
        showVideo(PORTAL_VIDEO.INTRO)

    def showOutroVideo(self):
        setOutroVideoViewed(True)
        showVideo(PORTAL_VIDEO.OUTRO)

    def onPrbEnter(self):
        self.__inPortalLobby = True
        g_eventBus.addListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY, priority=EventPriority.VERY_LOW)
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onHangarVehicleSelected, EVENT_BUS_SCOPE.LOBBY)

    def onPrbLeave(self):
        self.__inPortalLobby = False
        g_eventBus.removeListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onHangarVehicleSelected, EVENT_BUS_SCOPE.LOBBY)
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.PORTAL_ACTIVE, False)
        play2DSound(PortalMusicState.EXIT)

    def __viewLoaded(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.onPrbEntitySwitched()

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
            self.__onPrbEntitySwitchedToEvent()

    def isEnabled(self):
        return self.__eventConfig.isEnabled

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

    def __addListeners(self):
        portal = self.portal
        portal.onMaxComplexityLevelIncreased += self.__onMaxComplexityLevelChanged

    def __removeListeners(self):
        portal = self.portal
        portal.onMaxComplexityLevelIncreased -= self.__onMaxComplexityLevelChanged

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
        isPortalActive = self.getCurrentSeason() is not None
        if isPortalActive:
            if not isPortalStartedNotificationViewed():
                SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.enabled.body()), type=SystemMessages.SM_TYPE.PortalEventEnabled, priority=NotificationPriorityLevel.MEDIUM)
                setPortalStartedNotificationViewed(True)
        elif not isPortalFinishedNotificationViewed():
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

    def getCurrentStampsCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.__eventConfig.stamp)

    def getCurrentStampsAtLevel(self, level):
        if level < 1 or level > self.getTotalLevelsCount():
            return 0
        currentStamps = self.getCurrentStampsCount()
        stampsPerLevel = self.getStampsCountPerLevel()
        finishedLevels = self.getFinishedLevelsCount()
        if level <= finishedLevels:
            return stampsPerLevel
        return currentStamps % stampsPerLevel if level == finishedLevels + 1 else 0

    def getTotalLevelsCount(self):
        return len(self.__eventConfig.progression)

    def getProgression(self):
        return self.__eventConfig.progression

    def getFinishedLevelsCount(self):
        stampsCount = self.getCurrentStampsCount()
        stampsPerLevel = self.getStampsCountPerLevel()
        totalLevels = self.getTotalLevelsCount()
        return min(int(math.floor(stampsCount / stampsPerLevel)), totalLevels)

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
        vehExp = self.__vehiclesExperience.get(vehicle.compactDescr, None)
        if vehExp is None:
            _logger.error('There is no experience info for %s', vehicle.name)
            return False
        else:
            upgradeNodes = self.getVehicleUpgradeNodes(vehicle)
            neededPoints = upgradeNodes.get(currentLevel, {}).get('requiredPoints', None)
            return neededPoints and vehExp >= neededPoints

    def getQuestRewards(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda quest: quest.getID() == questID)
        bonuses = quests[questID].getBonuses()
        return bonuses

    def getStampsCountPerLevel(self):
        return self.__eventConfig.stampsPerProgressionStage

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

    def __onClientUpdated(self, diff, _):
        portalSection = diff.get('portal', {})
        if not portalSection:
            return
        else:
            vehicleUpgradesMasks = portalSection.get(PORTAL_VEHICLE_UPGRADES_KEY, {})
            vehicleExperience = portalSection.get(PORTAL_VEHICLE_EXPERIENCE_KEY, {})
            maxComplexityLevel = portalSection.get(PORTAL_MAX_COMPLEXITY_KEY, None)
            if vehicleUpgradesMasks:
                for vehicle, mask in vehicleUpgradesMasks.items():
                    self.__vehicleUpgradeMasks[vehicle] = mask

                self.onVehicleUpgradesMasksChanged(vehicleUpgradesMasks)
            if vehicleExperience:
                for vehicle, vehicleExp in vehicleExperience.items():
                    exp = vehicleExp.get('exp')
                    if exp is None:
                        continue
                    self.__vehiclesExperience[vehicle] = exp
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

    def getVehicleUpgradeTree(self, vehicle):
        vehicleUpgradeTree = self.__vehicleUpgradeMasks.get(vehicle.compactDescr, None)
        if vehicleUpgradeTree is None:
            _logger.error('There is no upgrade tree for %s', vehicle.name)
            return 0
        else:
            return vehicleUpgradeTree

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
        exp = self.__vehiclesExperience.get(vehicle.intCD)
        if exp is None:
            _logger.error('There is no experience for  %s', vehicle.name)
            return 0
        else:
            return exp

    def __onMaxComplexityLevelChanged(self, maxComplexityLevel):
        self.__maxComplexityLevel = maxComplexityLevel
        self.battleLevel = maxComplexityLevel
        self.__needToShowComplexityUnlock = True
        battleLevelName = backport.text(R.strings.portal_lobby.complexity.level.dyn('c_{}'.format(maxComplexityLevel))())
        SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.portalDifficultyLevel.body(), level=battleLevelName), type=SystemMessages.SM_TYPE.PortalDifficultyLevelChanged, priority=NotificationPriorityLevel.MEDIUM)

    def showComplexityUnlock(self):
        if self.__needToShowComplexityUnlock:
            event_dispatcher.showComplexityUnlockedView(self.__maxComplexityLevel)
            self.__needToShowComplexityUnlock = False

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
        if isSuspended:
            SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.suspended()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)

    def __onFrozenStateChanged(self, isFrozen):
        if isFrozen:
            SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.eventLocked()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
        else:
            SystemMessages.pushMessage(text=backport.text(R.strings.portal_messenger.serviceChannelMessages.eventState.eventUnlocked()), priority=NotificationPriorityLevel.MEDIUM)

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
