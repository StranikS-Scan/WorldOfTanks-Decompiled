# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_controller.py
import typing
import logging
import Math
import constants
from collections import namedtuple, defaultdict
from CurrentVehicle import g_currentVehicle
from Event import EventManager, Event
from ExtensionsManager import g_extensionsManager
from PlayerEvents import g_playerEvents
from new_year_account_settings import getNYSetting, setNYSettings
from new_year.ny_constants import NY_IS_CELEB_VOICEOVERS_ENABLED, NY_SEEN_QUESTS
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import adisp_async, adisp_process
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl.gen.view_models.constants.loot_box_bonus_group import LootBoxBonusGroup
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.dispatcher import g_prbLoader
from helpers import dependency, server_settings
from new_year_common.items import new_year, collectibles
from new_year_common.items.components.ny_constants import TOY_TYPES, TOY_TYPES_BY_OBJECT, NY_STATE, ToyTypes, ToySettings, TOY_TYPE_IDS_BY_NAME, MAX_ATMOSPHERE_LVL, TOKEN_VARIADIC_DISCOUNT_PREFIX, YEARS, YEARS_INFO, CurrentNYConstants, CustomizationObjects
from new_year.gui.shared.ny_bonuses import BonusHelper, BonusesSortTags, BONUS_TAG_HANDLER_MAP, BONUSES_GUI_CONFIG_PATH, aggregateToys, leaveOneToyPerRank, BONUSES_KEY_FUNC
from new_year_common.items.new_year import getToyMask
from new_year.gui.shared.ny_toy_info import NewYearCurrentToyInfo
from new_year.gui.shared.ny_level_helper import LevelInfo, getLevelIndexes, NewYearAtmospherePresenter
from new_year.gui.game_control.ny_navigation_helper import NewYearNavigationHelper
from new_year.gui.shared.gui_items.processors.ny_processor import HangToyProcessor, BuyToyProcessor
from new_year.gui.game_control.ny_tutorial_controller import NewYearTutorialController
from new_year_common.settings import NY_CONFIG_NAME
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.game_control import IUnseenEventsCounter
from new_year.skeletons.new_year import INewYearController
from skeletons.gui.game_control import IBootcampController, IBattleRoyaleController, IGuiLootBoxesController
from new_year.helpers.server_settings import getNewYearObjectsConfig, getNewYearGeneralConfig, getNewYearMachineConfig
from new_year.gui.shared.utils.ny_requester import NewYearToy
from new_year.helpers.ny_helpers import getCurrentObjectLevel
from new_year.ny_constants import NewYearLootBoxes
_HangarFlag = namedtuple('_HangarFlag', 'icon, iconDisabled, flagBackground')
_NewYearSysMessages = namedtuple('_NewYearSysMessages', 'keyText, priority, type')
_NY_STATE_TRANSITION_SYS_MESSAGES = {(NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED): _NewYearSysMessages(R.strings.ny.notification.suspend(), NotificationPriorityLevel.HIGH, SM_TYPE.ErrorHeader),
 (NY_STATE.SUSPENDED, NY_STATE.IN_PROGRESS): _NewYearSysMessages(R.strings.ny.notification.resume(), NotificationPriorityLevel.HIGH, SM_TYPE.InformationHeader),
 (NY_STATE.IN_PROGRESS, NY_STATE.FINISHED): _NewYearSysMessages(R.strings.ny.notification.finish(), NotificationPriorityLevel.MEDIUM, SM_TYPE.InformationHeader)}
_NY_STATE_SYS_MESSAGES = {NY_STATE.IN_PROGRESS: _NewYearSysMessages(R.strings.ny.notification.start(), NotificationPriorityLevel.MEDIUM, SM_TYPE.NewYearInfo),
 NY_STATE.SUSPENDED: _NewYearSysMessages(R.strings.ny.notification.suspend(), NotificationPriorityLevel.MEDIUM, SM_TYPE.ErrorHeader),
 NY_STATE.FINISHED: _NewYearSysMessages(R.strings.ny.notification.finish(), NotificationPriorityLevel.MEDIUM, SM_TYPE.ErrorHeader)}
_NY_QUESTS_STATE_MESSAGES = {NY_STATE.IN_PROGRESS: _NewYearSysMessages(R.strings.ny.quests.start(), NotificationPriorityLevel.MEDIUM, SM_TYPE.NewYearQuestInfo),
 NY_STATE.SUSPENDED: _NewYearSysMessages(R.strings.ny.quests.suspend(), NotificationPriorityLevel.MEDIUM, SM_TYPE.ErrorSimple)}
NY_QUEUE_TYPES_TO_PREBATTLE_ACTION_NAME = {constants.QUEUE_TYPE.VERSUS_AI: 'versusAI',
 constants.QUEUE_TYPE.RANDOMS: PREBATTLE_ACTION_NAME.RANDOM,
 constants.QUEUE_TYPE.COMP7: PREBATTLE_ACTION_NAME.COMP7}
_logger = logging.getLogger(__name__)

def _getState(state):
    return NY_STATE.FINISHED if state not in NY_STATE.ALL else state


class NewYearController(INewYearController, IGlobalListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcampController = dependency.descriptor(IBootcampController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _GUILootboxes = dependency.descriptor(IGuiLootBoxesController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __gui = dependency.descriptor(IGuiLoader)
    __unseenEventsManager = dependency.descriptor(IUnseenEventsCounter)

    def __init__(self):
        super(NewYearController, self).__init__()
        self.__finishTime = 0
        self.__commandProcessor = None
        self.__state = None
        self.__levelsInfo = None
        self.__em = EventManager()
        self.onDataUpdated = Event(self.__em)
        self.onStateChanged = Event(self.__em)
        self.onUpdateSlot = Event(self.__em)
        self.onSetHangToyEffectEnabled = Event(self.__em)
        self.onVariadicDiscountsUpdated = Event(self.__em)
        self.onCustomizationObjectUpdated = Event(self.__em)
        self.onSpaceObjectHover = Event(self.__em)
        self.onGUIObjectHover = Event(self.__em)
        self.onNySettingsChanged = Event(self.__em)
        self.onOnboardingFinished = Event(self.__em)
        self.onUIControlsLockChanged = Event(self.__em)
        self.onPetVisibilityUpdated = Event(self.__em)
        self.__variadicDiscountCount = 0
        self.__regularToyGroups = {}
        self.__spaceUpdated = False
        self.__isBattleRoyaleMode = False
        self.__navigationHelper = NewYearNavigationHelper()
        self.__tutorialController = NewYearTutorialController()
        self.__lockedUIControls = set()
        self.__customReturnActionName = None
        self.__lastMachineEnabled = None
        self.__lastPetVisible = None
        return

    def init(self):
        self.__commandProcessor = dependency.instance(IFestivityFactory).getProcessor()
        self.__buildRegularToyGroups()
        self.__initLootboxes()
        _logger.info('NewYearController initialized')

    def fini(self):
        self.__finiLootboxes()
        self.__regularToyGroups.clear()
        self.__commandProcessor = None
        self.__tutorialController.fini()
        _logger.info('NewYearController finalized')
        return

    def onLobbyInited(self, event):
        self.__lastMachineEnabled = getNewYearMachineConfig().isEnabled()
        self.__lastPetVisible = getNewYearGeneralConfig().getPetVisible()
        if self._bootcampController.isInBootcamp():
            return
        self.__isBattleRoyaleMode = self._battleRoyaleController.isBattleRoyaleMode()
        self.__navigationHelper.onLobbyInited()
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self._eventsCache.onSyncCompleted += self.__onEventsDataChanged
        self._hangarSpace.onSpaceCreate += self.__onSpaceCreate
        self._hangarSpace.onSpaceRefresh += self.__onSpaceRefresh
        self.__eventsDataUpdate()
        self.startGlobalListening()
        self.updateVariadicDiscounts()
        self.__updateUnseenQuests()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def onAvatarBecomePlayer(self):
        self.__tutorialController.onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        self.__tutorialController.onAccountBecomePlayer()

    def onConnected(self):
        self.__tutorialController.onConnected()

    def onDisconnected(self):
        self.__tutorialController.onDisconnected()
        self.__clear()

    def isEnabled(self):
        return self.__state == NY_STATE.IN_PROGRESS and not self._bootcampController.isInBootcamp() and not self.__isBattleRoyaleMode

    def isMaxAtmosphereLevel(self):
        return self._itemsCache.items.festivity.getMaxLevel() == MAX_ATMOSPHERE_LVL

    def isInProgress(self):
        return self.__state == NY_STATE.IN_PROGRESS

    def isPostEvent(self):
        return self.__state == NY_STATE.POST_EVENT and not self._bootcampController.isInBootcamp()

    def isSuspended(self):
        return self.__state == NY_STATE.SUSPENDED and not self._bootcampController.isInBootcamp()

    def isFinished(self):
        return self.__state == NY_STATE.FINISHED and not self._bootcampController.isInBootcamp()

    def isOnboardingFinished(self):
        return not self.isFirstEntrance() and getCurrentObjectLevel(CustomizationObjects.FIR) > 0

    def isFirstEntrance(self):
        return self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.NY_FIRST_ENTRANCE, True)

    def isPetToysRemoved(self):
        return self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_PET_TOYS_REMOVED: False})

    def isWelcomeMessageSent(self):
        return self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.NY_WELCOME_NOTIFICATION, False)

    def isOnboardingOpen(self):
        return self.__gui.windowsManager.getViewsByLayout(R.views.new_year.lobby.new_year.OnboardingView())

    def getActiveSettingBonusValue(self):
        return BonusHelper.getCommonPostEventBonus() if self.isPostEvent() else BonusHelper.getCommonBonus()

    def getMaxBonusValue(self):
        return BonusHelper.getCommonPostEventBonus() + getNewYearGeneralConfig().getMaxDynamicBonusValue()

    def getHangarQuestsFlagData(self):
        return _HangarFlag(None, None, None)

    def getHangarWidgetLinkage(self):
        return None

    def getHangarEdgeColor(self):
        return Math.Vector4(0.212, 0.843, 1, 1)

    def getToyDescr(self, toyID):
        return new_year.g_cache.toys.get(toyID)

    def getToyByID(self, toyID):
        toy = self.__getCurrentToys().get(toyID)
        return NewYearToy(toyID, 0, 0, 0) if not toy and toyID in new_year.g_cache.toys else toy

    def getToysByType(self, toyType):
        toysByType = [ toy for toy in self.__getCurrentToys().itervalues() if toy.getToyType() == toyType ]
        return sorted(toysByType, key=lambda toy: toy.getSortPriority())

    def getAllToysByTypeFromCache(self, toyType):
        inventoryToys = {toy.getID():toy for toy in self.__getCurrentToys().itervalues() if toy.getToyType() == toyType}
        cachedToys = [ NewYearToy(toy.id, 0, 0, 0) for toy in new_year.g_cache.toys.itervalues() if toy.type == toyType and toy.id not in inventoryToys ]
        toys = list(inventoryToys.values())
        toys.extend(cachedToys)
        return sorted(toys, key=lambda toy: toy.getSortPriority())

    def getAllCollectedToysId(self, year=None):
        collectedToys = set()
        toyCollection = self._itemsCache.items.festivity.getToyCollection()
        toys = new_year.g_cache.toys if year is None else collectibles.g_cache[YEARS.getYearStrFromYearNum(year)].toys
        for toyID, toyDescr in toys.iteritems():
            bytePos, mask = getToyMask(toyID, toyDescr.collection)
            if toyCollection[bytePos] & mask:
                collectedToys.add(toyID)

        return collectedToys

    def getLevel(self, level):
        if self.__levelsInfo is None:
            self.__createLevels()
        return self.__levelsInfo[level]

    @adisp_async
    @adisp_process
    def hangToy(self, toyID, slotID, callback=None):
        result = yield HangToyProcessor(toyID, slotID).request()
        self.onSetHangToyEffectEnabled(True)
        if result.success:
            self.onUpdateSlot(slotID, toyID)
        else:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if callback is not None:
            callback(result)
        return

    @adisp_async
    @adisp_process
    def buyToy(self, toyID, callback=None):
        result = yield BuyToyProcessor(toyID).request()
        if callback is not None:
            callback(result)
        if result.success or result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=result.msgPriority, messageData=result.msgData)
        return

    def __getToysInSlots(self, slotID=None):
        if slotID:
            slot = self.getSlotDescrs()[slotID]
            slotDescrs = [slot] if slot else []
        else:
            slotDescrs = self.getSlotDescrs()
        slotsData = self._itemsCache.items.festivity.getSlots()
        result = []
        for slotDescr in slotDescrs:
            if slotDescr.id < len(slotsData):
                toyID = slotsData[slotDescr.id]
                if toyID != -1:
                    result.append(self.getToyDescr(toyID))
                else:
                    result.append(None)

        return result

    def getNumberOfSlotsByType(self, slotType):
        return len([ slot for slot in self.getSlotDescrs() if slot.type == slotType ])

    def checkForNewToys(self, slot=None, objectType=None):
        toyInSlots = self.__getToysInSlots(slotID=slot)
        toyIdsInSlots = defaultdict(int)
        for toy in toyInSlots:
            if toy is None:
                continue
            toyIdsInSlots[toy.id] += 1

        if objectType is None and slot is None:
            objectToyTypes = ToyTypes.ALL
        else:
            objectToyTypes = TOY_TYPES_BY_OBJECT[objectType] if objectType else (self.getSlotDescrs()[slot].type,)
        isMaxAtmosphere = self.isMaxAtmosphereLevel()

        def _atmospherePredicate(toyToCheck):
            return toyToCheck.isNewInCollection() if isMaxAtmosphere else toyToCheck.getCount() > 0

        for toy in self.__getCurrentToys().itervalues():
            toyType = toy.getToyType()
            toyID = toy.getID()
            if toyType in objectToyTypes and toy.getCount() > 0 and toy.getUnseenCount() > 0 and _atmospherePredicate(toy) and (toyID not in toyIdsInSlots or slot is None and self.getNumberOfSlotsByType(toyType) != toyIdsInSlots[toyID]):
                return True

        return False

    def getPetToys(self):
        toysByType = [ toy for toy in self.__getCurrentToys().itervalues() if toy.getToyType() in ToyTypes.PET ]
        return sorted(toysByType, key=lambda toy: toy.getSortPriority())

    def isCollectionCompleted(self, collectionIDs=None):
        totalCounts = new_year.g_cache.toyCountByCollectionID
        collectionDistribution = self._itemsCache.items.festivity.getCollectionDistributions()
        if collectionIDs:
            collectionCount = 0
            totalCount = 0
            for collectionID in collectionIDs:
                collectionCount += sum(collectionDistribution[collectionID])
                totalCount += totalCounts[collectionID]

            return collectionCount == totalCount
        return sum((sum(rankDistrs) for rankDistrs in collectionDistribution)) == sum(totalCounts)

    def sendSeenToys(self, toyIDs):
        self.__commandProcessor.sendSeen(toyIDs)

    def sendSeenToysInCollection(self, toyIDs):
        result = []
        for toyID in toyIDs:
            result.extend((toyID, 0))

        self.__commandProcessor.seenInCollection(result)

    def sendViewAlbum(self, settingID, rank):
        self.__commandProcessor.viewAlbum(settingID, rank)

    def getUniqueMegaToysCount(self):
        allExistingUniqueMegaToys = set((toy.getToyType() for toy in self.__getCurrentToys().itervalues() if toy.isMega() and toy.getCount() > 0))
        toysInSlots = self.__getToysInSlots()
        uniqueMegaToysInSlots = set((toy.type for toy in toysInSlots if toy is not None and toy.setting == ToySettings.MEGA_TOYS))
        uniqueMegaToys = allExistingUniqueMegaToys.union(uniqueMegaToysInSlots)
        return len(uniqueMegaToys)

    def isFullRegularToysGroup(self, typeID, settingID, rank):
        toyGroup = self.__regularToyGroups.get((typeID, settingID, rank))
        if toyGroup is None:
            _logger.error('Unknown toy group: (%d, %d, %d)', typeID, settingID, rank)
            return False
        else:
            allCurrentToysIds = set((toy.getID() for toy in self.__getCurrentToys().itervalues()))
            for toyID in toyGroup:
                if toyID not in allCurrentToysIds:
                    return False

            return True

    def isRegularToysCollected(self):
        collectionDistribution = self._itemsCache.items.festivity.getCollectionDistributions()
        for collectionName in YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR_STR, useMega=False, usePet=False):
            collectionID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[collectionName]
            expectedToyCount = new_year.g_cache.toyCountByCollectionID[collectionID]
            collectedToyCount = sum(collectionDistribution[collectionID])
            if expectedToyCount != collectedToyCount:
                return False

        return True

    def getMaxToysStyle(self):
        allToys = self.__getToysInSlots()
        toys = [ item for item in allToys if item is not None ]
        return None if not toys else max(ToySettings.CURRENT_USUAL, key=lambda style: len([ toy for toy in toys if toy.setting == style ]))

    def getFinishTime(self):
        return self.__finishTime

    def showStateMessage(self):
        msg = _NY_STATE_SYS_MESSAGES.get(self.__state)
        if msg is not None:
            SystemMessages.pushMessage(backport.text(msg.keyText), type=msg.type, priority=msg.priority, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})
        return

    def getCollectionAwardQuest(self, collectionTypeToQuest, collectionType, filterFunc):
        if not collectionTypeToQuest:
            quests = self._eventsCache.getHiddenQuests(filterFunc).values()
            for q in quests:
                collectionTypeToQuest[q.getID().split(':')[2]] = q

            currentQuest = collectionTypeToQuest.get(ToySettings.CURRENT_USUAL[0].lower())
        else:
            currentQuest = collectionTypeToQuest.get(collectionType.lower())
        return currentQuest

    @property
    def tutorial(self):
        return self.__tutorialController

    def isWidgetVisible(self, prbState):
        correctPrb = self.__isCorrectPrb(prbState)
        return (self.isEnabled() or self.isSuspended()) and correctPrb

    def isCreditBonusVisible(self, prbState):
        hasVehicle = g_currentVehicle.isPresent()
        correctPrb = self.__isCorrectPrb(prbState)
        return self.isEnabled() and correctPrb and hasVehicle

    def setSpaceObjectHover(self, gameObjectName, value):
        self.onSpaceObjectHover(gameObjectName, value)

    def setGuiObjectHover(self, objectName, value):
        self.onGUIObjectHover(objectName, value)

    def lockUIControls(self, lockID):
        isLocked = self.isUIControlsLocked()
        self.__lockedUIControls.add(lockID)
        if isLocked != self.isUIControlsLocked():
            self.onUIControlsLockChanged(self.isUIControlsLocked())

    def unlockUIControls(self, lockID):
        isLocked = self.isUIControlsLocked()
        self.__lockedUIControls.discard(lockID)
        if isLocked != self.isUIControlsLocked():
            self.onUIControlsLockChanged(self.isUIControlsLocked())

    def isUIControlsLocked(self):
        return bool(self.__lockedUIControls)

    def isLootboxBigType(self, lbType):
        return lbType == NewYearLootBoxes.NY_CUR_YEAR_BIG

    def isLootboxTankType(self, lbType):
        return lbType == NewYearLootBoxes.NY_CUR_YEAR_TANKS

    @staticmethod
    def __isCorrectPrb(state):
        if state is None:
            return False
        else:
            isRandom = state.isInPreQueue(constants.QUEUE_TYPE.RANDOMS) or state.isInUnit(constants.PREBATTLE_TYPE.SQUAD)
            return isRandom

    @staticmethod
    def __isCorrectPrbForQuest(state):
        if state is None:
            return False
        else:
            isRandom = state.isInPreQueue(constants.QUEUE_TYPE.RANDOMS) or state.isInUnit(constants.PREBATTLE_TYPE.SQUAD)
            isVersusAI = state.isInPreQueue(constants.QUEUE_TYPE.VERSUS_AI) or state.isInUnit(constants.PREBATTLE_TYPE.VERSUS_AI)
            isComp7 = state.isInPreQueue(constants.QUEUE_TYPE.COMP7) or state.isInUnit(constants.PREBATTLE_TYPE.COMP7)
            return isRandom or isVersusAI or isComp7

    def resetNYDailyLimits(self):
        self.__commandProcessor.resetNYDailyLimits()

    def addToys(self, toysDict=None):
        self.__commandProcessor.addToys(toysDict)

    def addAllToysCopy(self, copyCount=10):
        import BigWorld
        for _ in xrange(1, copyCount + 1):
            BigWorld.callback(3.0, self.addToys)

    def addFragments(self, count=1000):
        self.__commandProcessor.addFragments(count)

    def addToysSet(self, settingId=''):
        if settingId == '' or settingId not in YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME:
            return
        toysDict = {toyID:1 for toyID, toy in new_year.g_cache.toys.iteritems() if toy.setting == settingId}
        self.__commandProcessor.addToys(toysDict)

    def addOldToys(self, year, toysDict=None):
        self.__commandProcessor.addOldToys(year, toysDict)

    def markPreviousYearTabVisited(self, yearName, settingsKey):
        yearNum = YEARS_INFO.convertYearToNum(yearName)
        isMaxLevel = self._itemsCache.items.festivity.getMaxLevel() == MAX_ATMOSPHERE_LVL
        isCurrentYearSelected = yearNum == YEARS_INFO.CURRENT_YEAR
        if isMaxLevel and not isCurrentYearSelected:
            oldCollectionsVisited = getNYSetting(settingsKey)
            oldCollectionsVisited[yearNum] = True
            setNYSettings(settingsKey, oldCollectionsVisited)

    def getVariadicDiscountCount(self):
        return self.__variadicDiscountCount

    def updateVariadicDiscounts(self):
        self.__variadicDiscountCount = len([ token for token in self._itemsCache.items.tokens.getTokens().keys() if token.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX) ])
        self.onVariadicDiscountsUpdated()

    def onPrbEntitySwitched(self):
        isBattleRoyaleMode = self._battleRoyaleController.isBattleRoyaleMode()
        if self.__isBattleRoyaleMode != isBattleRoyaleMode:
            self.__isBattleRoyaleMode = isBattleRoyaleMode
            self.onStateChanged()

    @adisp_async
    @adisp_process
    def switchToNewYearPrebattle(self, callback):
        clb = False
        if g_prbLoader and g_prbLoader.getDispatcher():
            entity = g_prbLoader.getDispatcher().getEntity()
            if entity:
                queueType = entity.getQueueType()
                result = yield self.prbDispatcher.doSelectAction(PrbAction(self.prbNewYearActionName))
                if result:
                    self.__customReturnActionName = NY_QUEUE_TYPES_TO_PREBATTLE_ACTION_NAME.get(queueType, None)
                clb = result
        if not clb:
            LOG_ERROR('New Year Hangar cannot be loaded.')
        callback(clb)
        return

    @adisp_process
    def switchFromNewYearPrebattle(self):
        if not self.__customReturnActionName:
            return
        else:
            result = yield self.prbDispatcher.doSelectAction(PrbAction(self.__customReturnActionName))
            if result:
                self.__customReturnActionName = None
            else:
                LOG_ERROR('Cannot switch from New Year Hangar.')
            return

    def isNewYearBattleMode(self):
        if self.prbDispatcher is None:
            return False
        else:
            state = self.prbDispatcher.getFunctionalState()
            return self.__isCorrectPrb(state)

    @property
    def prbNewYearActionName(self):
        return PREBATTLE_ACTION_NAME.RANDOM

    def isCelebVoiceoverEnabled(self):
        return getNYSetting(NY_IS_CELEB_VOICEOVERS_ENABLED) and self.isEnabled()

    def getSlotDescrs(self):
        return tuple(new_year.g_cache.slots)

    def __onClientUpdated(self, diff, _):
        festivityKey = self._itemsCache.items.festivity.dataKey
        if festivityKey in diff:
            self.onDataUpdated(diff[festivityKey].keys())
        newYearObjectsConfig = getNewYearObjectsConfig()
        levelUP = [ ny_object for ny_object in CustomizationObjects.ALL if newYearObjectsConfig.getObjectToken(ny_object) in diff.get('tokens', {}) ]
        if levelUP:
            self.onCustomizationObjectUpdated(*levelUP)

    def __onEventsDataChanged(self):
        self.__eventsDataUpdate()
        if self.__levelsInfo is not None:
            for levelInfo in self.__levelsInfo.itervalues():
                levelInfo.updateBonuses()

        return

    def __onSpaceCreate(self):
        self.__spaceUpdated = False
        self.__hangToys()

    def __onSpaceRefresh(self):
        self.__spaceUpdated = True

    def __eventsDataUpdate(self):
        state = None
        for action in self._eventsCache.getActions().itervalues():
            if 'EventState' in action.getModifiersDict():
                state = action.getModifiersDict()['EventState'].getState()
                self.__finishTime = action.getFinishTime()

        self.__setState(state)
        return

    def __setState(self, state):
        state = _getState(state)
        self.__showSystemMessage(state)
        self.__state = state
        self.onStateChanged()

    def __updateNYQuestsStateMessage(self, state):
        questMsg = _NY_QUESTS_STATE_MESSAGES.get(state)
        if questMsg is not None:
            SystemMessages.pushMessage(text=backport.text(questMsg.keyText), type=questMsg.type, priority=questMsg.priority)
        return

    def __showSystemMessage(self, state):
        msg = _NY_STATE_TRANSITION_SYS_MESSAGES.get((self.__state, state))
        if not self.isWelcomeMessageSent():
            self.__pushNYMessage(_NY_STATE_SYS_MESSAGES[NY_STATE.IN_PROGRESS])
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_WELCOME_NOTIFICATION: True})
        elif msg is not None:
            self.__pushNYMessage(msg)
            self.__updateNYQuestsStateMessage(state)
        if state == NY_STATE.FINISHED and not self.isPetToysRemoved():
            toysId = [ '"{toyName}"'.format(toyName=backport.text(NewYearCurrentToyInfo(int(toy.getID())).getName())) for toy in self.getPetToys() ]
            text = '\n'.join(toysId)
            SystemMessages.pushMessage(text=text, type=SM_TYPE.NYRacoonItems, priority=NotificationPriorityLevel.HIGH)
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_PET_TOYS_REMOVED: True})
        return

    def __pushNYMessage(self, message):
        SystemMessages.pushMessage(text=backport.text(message.keyText), priority=message.priority, type=message.type, messageData={'header': backport.text(R.strings.ny.notification.header())})

    def __hangToys(self):
        self.onSetHangToyEffectEnabled(False)
        for slotID, toyID in enumerate(self._itemsCache.items.festivity.getSlots()):
            self.onUpdateSlot(slotID, toyID)

    def __createLevels(self):
        self.__levelsInfo = {}
        levelRewardsByID = new_year.g_cache.levelRewardsByID
        for level in getLevelIndexes():
            if level in levelRewardsByID:
                quest = self._eventsCache.getQuestByID(levelRewardsByID[level])
                self.__levelsInfo[level] = LevelInfo(level, quest)

    def __clear(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__levelsInfo = None
        self.__spaceUpdated = False
        self.__customReturnActionName = None
        self.__lastMachineEnabled = None
        self.__lastPetVisible = None
        self.__lockedUIControls.clear()
        self.__navigationHelper.clear()
        self.stopGlobalListening()
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self._eventsCache.onSyncCompleted -= self.__onEventsDataChanged
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self._hangarSpace.onSpaceRefresh -= self.__onSpaceRefresh
        return

    def __getCurrentToys(self):
        return self._itemsCache.items.festivity.getToys()

    def __buildRegularToyGroups(self):
        for toyID, toyDescr in new_year.g_cache.toys.iteritems():
            if toyDescr.setting in ToySettings.MEGA:
                continue
            if toyDescr.setting in ToySettings.CURRENT_PET:
                continue
            if toyDescr.setting not in ToySettings.CURRENT_USUAL:
                _logger.error('Wrong toy setting: "%s"', toyDescr.setting)
                continue
            if toyDescr.type not in TOY_TYPES:
                _logger.error('Wrong toy type: "%s"', toyDescr.type)
                continue
            rank = toyDescr.rank
            if rank not in xrange(1, YEARS_INFO.getMaxToyRankByYear(YEARS_INFO.CURRENT_YEAR) + 1):
                _logger.error('Wrong toy rank: "%d"', rank)
                continue
            toyTypeID = TOY_TYPE_IDS_BY_NAME[toyDescr.type]
            toySettingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toyDescr.setting]
            self.__regularToyGroups.setdefault((toyTypeID, toySettingID, rank), []).append(toyID)

    def __initLootboxes(self):
        if not g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
            return
        from gui.shared.gui_items.loot_box import addBonusesToGroup
        addBonusesToGroup(LootBoxBonusGroup.FEATUREITEMS, (CurrentNYConstants.IP_TYPE_CUSTOM_TOYS,
         CurrentNYConstants.IP_TYPE_CUSTOM_ANYOF_TOYS,
         CurrentNYConstants.IP_TYPE_CUSTOM_MANDATINS,
         CurrentNYConstants.IP_TYPE_CUSTOM_CURRENCIES))
        from gui_lootboxes_common import constants_utils
        from new_year.gui.bonuses.bonuses_packers import NYMysteryBoxWithToysBonusUIPacker, NYBoxWithToysBonusUIPacker, NYToyBonusUIPackerLarge, NYToyBonusUIPacker
        from new_year.gui.impl.new_year.new_year_bonus_packer import NYMandarinsBonusPacker
        constants_utils.addBonusPackerToDefaultMap({CurrentNYConstants.TOYS: NYMysteryBoxWithToysBonusUIPacker(),
         CurrentNYConstants.ANY_OF: NYMysteryBoxWithToysBonusUIPacker(),
         CurrentNYConstants.MANDARINS: NYMandarinsBonusPacker()})
        constants_utils.addBonusPackerToRewardsMap({CurrentNYConstants.TOYS: NYBoxWithToysBonusUIPacker(),
         CurrentNYConstants.MANDARINS: NYMandarinsBonusPacker()})
        constants_utils.addBonusPackerToMainRewardsMap({CurrentNYConstants.TOYS: NYToyBonusUIPackerLarge(),
         CurrentNYConstants.MANDARINS: NYMandarinsBonusPacker()})
        constants_utils.addBonusPackerToStatisticsMap({CurrentNYConstants.TOYS: NYToyBonusUIPacker(),
         CurrentNYConstants.MANDARINS: NYMandarinsBonusPacker()})
        constants_utils.addBonusesOrder(BONUSES_GUI_CONFIG_PATH, BonusesSortTags.RANGE, BONUS_TAG_HANDLER_MAP, BONUSES_KEY_FUNC)
        constants_utils.addSecondaryRewardsProcessor(aggregateToys)
        constants_utils.addBonusGroupTooltipProcessor(aggregateToys)
        constants_utils.addBonusProbabilitiesSlotProcessor(leaveOneToyPerRank)
        from web.web_client_api.loot_boxes import addBonusWrappers, addBonusAlias
        from new_year.gui.shared.ny_w2c_bonus_wrappers import ToyWrapper
        addBonusWrappers({CurrentNYConstants.IP_TYPE_CUSTOM_TOYS: ToyWrapper})
        addBonusAlias({CurrentNYConstants.IP_TYPE_CUSTOM_ANYOF_TOYS: CurrentNYConstants.IP_TYPE_CUSTOM_TOYS})
        from gui.server_events.bonuses import registerTokenFactoryExtra
        from NewYearBonusesClient import mandarinPredicate, mandarinFactory, toyCompensationPredicate, toyCompensationTokenFactory
        registerTokenFactoryExtra(mandarinPredicate, mandarinFactory)
        registerTokenFactoryExtra(toyCompensationPredicate, toyCompensationTokenFactory)

    def __finiLootboxes(self):
        if not g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
            return
        from gui.server_events.bonuses import unregisterTokenFactoryExtra
        from NewYearBonusesClient import mandarinPredicate, mandarinFactory, toyCompensationPredicate, toyCompensationTokenFactory
        unregisterTokenFactoryExtra(mandarinPredicate, mandarinFactory)
        unregisterTokenFactoryExtra(toyCompensationPredicate, toyCompensationTokenFactory)

    @server_settings.serverSettingsChangeListener(NY_CONFIG_NAME)
    def __onServerSettingsChanged(self, diff):
        self.onNySettingsChanged()
        self.__sendMachineNotification(diff)
        self.__sendRacoonNotification(diff)

    def __sendMachineNotification(self, diff):
        isMachineEnabled = diff.get('ny_config', {}).get('machine_config', {}).get('isEnabled')
        if isMachineEnabled is None:
            return
        elif self.__lastMachineEnabled is not None and isMachineEnabled == self.__lastMachineEnabled:
            return
        else:
            self.__lastMachineEnabled = isMachineEnabled
            if isMachineEnabled:
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.available.text()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.machine.header())})
            else:
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.unavailable.text()), type=SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.machine.header())})
            return

    def __sendRacoonNotification(self, diff):
        isRacoonEnabled = diff.get('ny_config', {}).get('general_config', {}).get('petVisible')
        if isRacoonEnabled is None:
            return
        else:
            self.onPetVisibilityUpdated(isRacoonEnabled)
            if NewYearAtmospherePresenter.getLevel() < getNewYearGeneralConfig().getRaccoonLevelOpen():
                return
            if self.__lastPetVisible is not None and isRacoonEnabled == self.__lastPetVisible:
                return
            self.__lastPetVisible = isRacoonEnabled
            if isRacoonEnabled:
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.racoon.available.text()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.racoon.news())})
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.leaderboard.available()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.leaderboard.header())})
            else:
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.racoon.unavailable.text()), type=SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.racoon.news())})
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.leaderboard.unavailable()), type=SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.leaderboard.header())})
            return

    def __updateUnseenQuests(self):
        seenQuests = getNYSetting(NY_SEEN_QUESTS)
        for qID, _ in self._eventsCache.getNyCelebQuests().iteritems():
            if qID not in seenQuests:
                self.__unseenEventsManager.addUnseenEvent(qID, 1)


def isAllNyQuestsCompleted(eventsCache):
    for questID, quest in eventsCache.getAllQuests().iteritems():
        if (questID.startswith(CurrentNYConstants.NY_DAILY_QUESTS_PREFIX) or questID.startswith(CurrentNYConstants.NY_WEEKLY_QUESTS_PREFIX)) and quest.isAvailable().isValid and not quest.isCompleted():
            return False

    return True


def getNYQuests(eventsCache):
    quests = sorted(eventsCache.getAllQuests().iteritems())
    nyDailyQuests = {}
    nyWeeklyQuests = {}
    for questID, quest in quests:
        if not (quest.isStarted() and quest.isAvailable()):
            continue
        if questID.startswith(CurrentNYConstants.NY_DAILY_QUESTS_PREFIX):
            nyDailyQuests[questID] = quest
        if questID.startswith(CurrentNYConstants.NY_WEEKLY_QUESTS_PREFIX):
            nyWeeklyQuests[questID] = quest

    return (nyDailyQuests, nyWeeklyQuests)
