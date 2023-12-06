# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_controller.py
import typing
import logging
from collections import namedtuple, defaultdict
import Math
import constants
from CurrentVehicle import g_currentVehicle
from Event import EventManager, Event
from ExtensionsManager import g_extensionsManager
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_OLD_REWARDS_BY_YEAR_VISITED
from adisp import adisp_async, adisp_process
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.loot_box_bonus_group import LootBoxBonusGroup
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.system_factory import registerNotificationsListeners
from helpers import dependency
from items import new_year, collectibles
from items.components.ny_constants import TOY_TYPES, TOY_TYPES_BY_OBJECT, NY_STATE, ToyTypes, ToySettings, TOY_TYPE_IDS_BY_NAME, MAX_ATMOSPHERE_LVL, TOKEN_VARIADIC_DISCOUNT_PREFIX, YEARS, YEARS_INFO, CurrentNYConstants
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.ny_bonuses import BonusHelper, BonusesSortTags, BONUS_TAG_HANDLER_MAP, BONUSES_GUI_CONFIG_PATH, aggregateToys, leaveOneToyPerRank, BONUSES_KEY_FUNC
from items.new_year import getToyMask
from new_year.ny_level_helper import LevelInfo, getLevelIndexes
from new_year.ny_navigation_helper import NewYearNavigationHelper
from new_year.ny_processor import HangToyProcessor
from new_year.ny_tutorial_controller import NewYearTutorialController
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
from skeletons.gui.game_control import IBootcampController, IBattleRoyaleController
from web.web_client_api.loot_boxes import addBonusAlias
_HangarFlag = namedtuple('_HangarFlag', 'icon, iconDisabled, flagBackground')
_NewYearSysMessages = namedtuple('_NewYearSysMessages', 'keyText, priority, type')
_NY_STATE_TRANSITION_SYS_MESSAGES = {(NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED): _NewYearSysMessages(R.strings.ny.notification.suspend(), 'high', SystemMessages.SM_TYPE.Warning),
 (NY_STATE.SUSPENDED, NY_STATE.IN_PROGRESS): _NewYearSysMessages(R.strings.ny.notification.resume(), 'high', SystemMessages.SM_TYPE.Warning),
 (NY_STATE.NOT_STARTED, NY_STATE.IN_PROGRESS): _NewYearSysMessages(R.strings.ny.notification.start(), 'high', SystemMessages.SM_TYPE.NewYearEventStarted),
 (NY_STATE.POST_EVENT, NY_STATE.FINISHED): _NewYearSysMessages(R.strings.ny.notification.finish(), 'medium', SystemMessages.SM_TYPE.Information)}
_NY_STATE_SYS_MESSAGES = {NY_STATE.SUSPENDED: _NewYearSysMessages(R.strings.ny.notification.suspend(), 'medium', SystemMessages.SM_TYPE.ErrorHeader),
 NY_STATE.POST_EVENT: _NewYearSysMessages(R.strings.ny.notification.postEvent(), 'medium', SystemMessages.SM_TYPE.ErrorHeader),
 NY_STATE.FINISHED: _NewYearSysMessages(R.strings.ny.notification.finish(), 'medium', SystemMessages.SM_TYPE.ErrorHeader)}

def _getPostEventMessage(ctrl):
    return _NewYearSysMessages(R.strings.ny.notification.finish(), 'medium', SystemMessages.SM_TYPE.Information)


_NY_STATE_TRANSITION_CONDITIONAL_MESSAGES = {(NY_STATE.IN_PROGRESS, NY_STATE.POST_EVENT): _getPostEventMessage}
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
        self.__variadicDiscountCount = 0
        self.__regularToyGroups = {}
        self.__spaceUpdated = False
        self.__isBattleRoyaleMode = False
        self.__navigationHelper = NewYearNavigationHelper()
        self.__tutorialController = NewYearTutorialController()
        return

    def init(self):
        self.__commandProcessor = dependency.instance(IFestivityFactory).getProcessor()
        self.__buildRegularToyGroups()
        self.__initLootboxes()

    def fini(self):
        self.__finiLootboxes()
        self.__regularToyGroups.clear()
        self.__commandProcessor = None
        self.__tutorialController.fini()
        return

    def onLobbyInited(self, event):
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

    def isPostEvent(self):
        return self.__state == NY_STATE.POST_EVENT and not self._bootcampController.isInBootcamp()

    def isSuspended(self):
        return self.__state == NY_STATE.SUSPENDED and not self._bootcampController.isInBootcamp()

    def isFinished(self):
        return self.__state == NY_STATE.FINISHED and not self._bootcampController.isInBootcamp()

    def getActiveSettingBonusValue(self):
        return BonusHelper.getCommonPostEventBonus() if self.isPostEvent() else BonusHelper.getCommonBonus()

    def getActiveMultiplier(self):
        return BonusHelper.getCommonPostEventAtmosphereMultiplier() if self.isPostEvent() else BonusHelper.getAtmosphereMultiplier()

    def getActiveCollectionsBonus(self):
        return BonusHelper.getCommonPostEventCollectionsBonus() if self.isPostEvent() else BonusHelper.getCommonCollectionsFactor()

    def getHangarQuestsFlagData(self):
        return _HangarFlag(None, None, None)

    def getHangarWidgetLinkage(self):
        return None

    def getHangarEdgeColor(self):
        return Math.Vector4(0.212, 0.843, 1, 1)

    def getToyDescr(self, toyID):
        return new_year.g_cache.toys.get(toyID)

    def getToysByType(self, toyType):
        toysByType = [ toy for toy in self.__getCurrentToys().itervalues() if toy.getToyType() == toyType ]
        return sorted(toysByType, key=lambda toy: toy.getSortPriority())

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
            if toyType in objectToyTypes and toy.getCount() > 0 and toy.getUnseenCount() != 0 and _atmospherePredicate(toy) and (toyID not in toyIdsInSlots or slot is None and self.getNumberOfSlotsByType(toyType) != toyIdsInSlots[toyID]):
                return True

        return False

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
        for collectionName in YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR_STR, useMega=False):
            collectionID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[collectionName]
            expectedToyCount = new_year.g_cache.toyCountByCollectionID[collectionID]
            collectedToyCount = sum(collectionDistribution[collectionID])
            if expectedToyCount != collectedToyCount:
                return False

        return True

    def getMaxToysStyle(self):
        allToys = self.__getToysInSlots()
        toys = [ item for item in allToys if item is not None ]
        return None if not toys else max(ToySettings.NEW, key=lambda style: len([ toy for toy in toys if toy.setting == style ]))

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

            currentQuest = collectionTypeToQuest.get(ToySettings.NEW[0].lower())
        else:
            currentQuest = collectionTypeToQuest.get(collectionType.lower())
        return currentQuest

    @property
    def tutorial(self):
        return self.__tutorialController

    def isWidgetVisible(self, prbState, alias=None):
        correctAlias = alias in (VIEW_ALIAS.LOBBY_HANGAR, R.views.lobby.new_year.MainView())
        correctPrb = self.__isCorrectPrb(prbState)
        return self.isEnabled() and correctPrb and correctAlias

    def isCreditBonusVisible(self, prbState):
        hasVehicle = g_currentVehicle.isPresent()
        correctPrb = self.__isCorrectPrb(prbState)
        return self.isEnabled() and correctPrb and hasVehicle

    @staticmethod
    def __isCorrectPrb(state):
        if state is None:
            return False
        else:
            isRandom = state.isInPreQueue(constants.QUEUE_TYPE.RANDOMS) or state.isInUnit(constants.PREBATTLE_TYPE.SQUAD)
            isVersusAI = state.isInPreQueue(constants.QUEUE_TYPE.VERSUS_AI) or state.isInUnit(constants.PREBATTLE_TYPE.VERSUS_AI)
            isTraining = state.isInLegacy(constants.PREBATTLE_TYPE.TRAINING)
            isFunRandom = state.isInPreQueue(constants.QUEUE_TYPE.FUN_RANDOM) or state.isInUnit(constants.PREBATTLE_TYPE.FUN_RANDOM)
            return isRandom or isVersusAI or isTraining or isFunRandom

    def resetNYDailyLimits(self):
        self.__commandProcessor.resetNYDailyLimits()

    def addToys(self, toysDict=None):
        self.__commandProcessor.addToys(toysDict)

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
            oldCollectionsVisited = AccountSettings.getNewYear(settingsKey)
            oldCollectionsVisited[yearNum] = True
            AccountSettings.setNewYear(settingsKey, oldCollectionsVisited)

    def getVariadicDiscountCount(self):
        return self.__variadicDiscountCount

    def updateVariadicDiscounts(self):
        self.__variadicDiscountCount = len([ token for token in self._itemsCache.items.tokens.getTokens().keys() if token.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX) ])
        self.onVariadicDiscountsUpdated()

    def isOldRewardsBubbleNeeded(self, years):
        return self.__isShowBubbleOnTabForYears(years, NY_OLD_REWARDS_BY_YEAR_VISITED)

    def onPrbEntitySwitched(self):
        isBattleRoyaleMode = self._battleRoyaleController.isBattleRoyaleMode()
        if self.__isBattleRoyaleMode != isBattleRoyaleMode:
            self.__isBattleRoyaleMode = isBattleRoyaleMode
            self.onStateChanged()

    def getSlotDescrs(self):
        return tuple(new_year.g_cache.slots)

    def __isShowBubbleOnTabForYears(self, years, settingsKey):
        isMaxLevel = self._itemsCache.items.festivity.getMaxLevel() == MAX_ATMOSPHERE_LVL
        if not isMaxLevel:
            return False
        oldCollectionsByYearVisited = AccountSettings.getNewYear(settingsKey)
        for year in years:
            beg, end = YEARS_INFO.getCollectionDistributionsRangeForYear(year)
            isCollectionCompleted = self.isCollectionCompleted(range(beg, end))
            if not isCollectionCompleted and not oldCollectionsByYearVisited[year]:
                return True

        return False

    def __onClientUpdated(self, diff, _):
        festivityKey = self._itemsCache.items.festivity.dataKey
        if festivityKey in diff:
            self.onDataUpdated(diff[festivityKey].keys())

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
        if self.__state != state:
            self.__showSystemMessage(state)
            self.__state = state
            self.onStateChanged()

    def __showSystemMessage(self, newState):
        msg = _NY_STATE_TRANSITION_SYS_MESSAGES.get((self.__state, newState))
        if not msg:
            msgCondition = _NY_STATE_TRANSITION_CONDITIONAL_MESSAGES.get((self.__state, newState))
            if msgCondition:
                msg = msgCondition(self)
        if msg is not None:
            if msg.type == SystemMessages.SM_TYPE.NewYearEventStarted:
                auxData = [msg.type,
                 msg.priority,
                 None,
                 None]
                serviceChannel = self._systemMessages.proto.serviceChannel
                serviceChannel.pushClientMessage(backport.text(msg.keyText), SCH_CLIENT_MSG_TYPE.NY_EVENT_BUTTON_MESSAGE, auxData=auxData)
            else:
                SystemMessages.pushMessage(backport.text(msg.keyText), priority=msg.priority, type=msg.type)
        return

    def __hangToys(self):
        self.onSetHangToyEffectEnabled(False)
        for slotID, toyID in enumerate(self._itemsCache.items.festivity.getSlots()):
            self.onUpdateSlot(slotID, toyID)

    def __createLevels(self):
        self.__levelsInfo = {}
        levelRewardsByID = new_year.g_cache.levelRewardsByID
        quests = self._eventsCache.getQuestsByIDs(levelRewardsByID.itervalues())
        for level in getLevelIndexes():
            self.__levelsInfo[level] = LevelInfo(level, quests[levelRewardsByID[level]])

    def __clear(self):
        self.__levelsInfo = None
        self.__spaceUpdated = False
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
            if toyDescr.setting not in ToySettings.NEW:
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
        addBonusesToGroup(LootBoxBonusGroup.FEATUREITEMS, (CurrentNYConstants.IP_TYPE_CUSTOM_TOYS, CurrentNYConstants.IP_TYPE_CUSTOM_ANYOF_TOYS))
        from gui_lootboxes_common import constants_utils
        from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import NYMysteryBoxWithToysBonusUIPacker, NYBoxWithToysBonusUIPacker, NYToyBonusUIPackerLarge
        constants_utils.addBonusPackerToDefaultMap({CurrentNYConstants.TOYS: NYMysteryBoxWithToysBonusUIPacker(),
         CurrentNYConstants.ANY_OF: NYMysteryBoxWithToysBonusUIPacker()})
        constants_utils.addBonusPackerToRewardsMap({CurrentNYConstants.TOYS: NYBoxWithToysBonusUIPacker()})
        constants_utils.addBonusPackerToMainRewardsMap({CurrentNYConstants.TOYS: NYToyBonusUIPackerLarge()})
        constants_utils.addBonusesOrder(BONUSES_GUI_CONFIG_PATH, BonusesSortTags.RANGE, BONUS_TAG_HANDLER_MAP, BONUSES_KEY_FUNC)
        constants_utils.addSecondaryRewardsProcessor(aggregateToys)
        constants_utils.addBonusGroupTooltipProcessor(aggregateToys)
        constants_utils.addBonusProbabilitiesSlotProcessor(leaveOneToyPerRank)
        from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import registerHandler
        from gui.impl.lobby.new_year.gui_lootbox_integration.unique_reward_handler import NewYearVehicleUniqueRewardHandler
        registerHandler(NewYearVehicleUniqueRewardHandler)
        from web.web_client_api.loot_boxes import addBonusWrappers
        from new_year.ny_w2c_bonus_wrappers import ToyWrapper
        addBonusWrappers({CurrentNYConstants.IP_TYPE_CUSTOM_TOYS: ToyWrapper})
        addBonusAlias({CurrentNYConstants.IP_TYPE_CUSTOM_ANYOF_TOYS: CurrentNYConstants.IP_TYPE_CUSTOM_TOYS})
        from new_year.ny_listeners import NYGuiLootBoxConfigListener
        registerNotificationsListeners((NYGuiLootBoxConfigListener,))

    def __finiLootboxes(self):
        if not g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
            return
        from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import unregisterHandler
        from gui.impl.lobby.new_year.gui_lootbox_integration.unique_reward_handler import NewYearVehicleUniqueRewardHandler
        unregisterHandler(NewYearVehicleUniqueRewardHandler)
