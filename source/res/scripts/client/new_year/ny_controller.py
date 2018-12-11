# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_controller.py
import typing
import logging
from collections import namedtuple
import Math
from Event import EventManager, Event
from PlayerEvents import g_playerEvents
from adisp import async, process
from gui import SystemMessages
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.NY import NY
from gui.impl.new_year.navigation import NewYearNavigation
from helpers import dependency, i18n
from items import ny19
from items.components.ny_constants import TOY_TYPES_BY_OBJECT, NY_STATE
from items.ny19 import calcBattleBonus
from new_year.ny_level_helper import LevelInfo, getLevelIndexes, NewYearAtmospherePresenter
from new_year.ny_processor import HangToyProcessor
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from skeletons.gui.game_control import IBootcampController
_HangarFlag = namedtuple('_HangarFlag', 'icon, iconDisabled, flagBackground')
_NEW_YEAR_HANGAR_FLAG = _HangarFlag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_NY_QUESTS_AVAILABLE, RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_NY_QUESTS_DISABLED, RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_NY)
_NewYearSysMessages = namedtuple('_NewYearSysMessages', 'keyText, priority, type')
_NY_STATE_SYS_MESSAGES = {(NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED): _NewYearSysMessages(NY.NOTIFICATION_SUSPEND, 'high', SystemMessages.SM_TYPE.Warning),
 (NY_STATE.SUSPENDED, NY_STATE.IN_PROGRESS): _NewYearSysMessages(NY.NOTIFICATION_RESUME, 'high', SystemMessages.SM_TYPE.Warning),
 (NY_STATE.NOT_STARTED, NY_STATE.IN_PROGRESS): _NewYearSysMessages(NY.NOTIFICATION_START, 'high', SystemMessages.SM_TYPE.NewYearEventStarted),
 (NY_STATE.IN_PROGRESS, NY_STATE.FINISHED): _NewYearSysMessages(NY.NOTIFICATION_FINISH, 'medium', SystemMessages.SM_TYPE.Information)}
_logger = logging.getLogger(__name__)

def _getState(state):
    return NY_STATE.FINISHED if state not in NY_STATE.ALL else state


class NewYearController(INewYearController):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _customizableObjectMgr = dependency.descriptor(ICustomizableObjectsManager)
    _bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(NewYearController, self).__init__()
        self.__commandProcessor = None
        self.__endDate = None
        self.__state = None
        self.__levelsInfo = None
        self.__em = EventManager()
        self.onDataUpdated = Event(self.__em)
        self.onStateChanged = Event(self.__em)
        self.__isCheckedUnusedRewards = False
        return

    def init(self):
        self.__commandProcessor = dependency.instance(IFestivityFactory).getProcessor()

    def fini(self):
        self.__commandProcessor = None
        return

    def onLobbyInited(self, event):
        if self._bootcampController.isInBootcamp():
            return
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self._eventsCache.onSyncCompleted += self.__onEventsDataChanged
        self.__eventsDataUpdate()

    def onLobbyStarted(self, ctx):
        self.__hangToys()

    def onAvatarBecomePlayer(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self._eventsCache.onSyncCompleted -= self.__onEventsDataChanged
        self.__clear()

    def onDisconnected(self):
        self.__isCheckedUnusedRewards = False
        NewYearNavigation.resetCraftFilter()
        self.__clear()

    def isEnabled(self):
        return self.__state == NY_STATE.IN_PROGRESS and not self._bootcampController.isInBootcamp()

    def getHangarQuestsFlagData(self):
        return _NEW_YEAR_HANGAR_FLAG if self.isEnabled() else _HangarFlag(None, None, None)

    def getHangarWidgetLinkage(self):
        return None

    def getHangarEdgeColor(self):
        return Math.Vector4(0.212, 0.843, 1, 1)

    def getToyDescr(self, toyID):
        return ny19.g_cache.toys.get(toyID)

    def getToysByType(self, toyType):
        allToys = self.__getCurrentToys()
        return sorted([ toy for toy in allToys.itervalues() if toy.getToyType() == toyType ])

    def getLevel(self, level):
        if self.__levelsInfo is None:
            self.__createLevels()
        return self.__levelsInfo[level]

    @async
    @process
    def hangToy(self, toyID, slotID, callback):
        result = yield HangToyProcessor(toyID, slotID).request()
        if result.success:
            self.__update3DSlot(toyID, slotID)
        else:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        callback(result)

    def getToysInSlots(self, objectName=None, slotID=None):
        slotDescrs = [self.getSlotDescrs()[slotID]] if slotID else self.getSlotDescrs(objectName)
        slotsData = self._itemsCache.items.festivity.getSlots()
        result = []
        for slotDescr in slotDescrs:
            toyID = slotsData[slotDescr.id]
            if toyID != -1:
                result.append(self.getToyDescr(toyID))
            result.append(None)

        return result

    def getSlotDescrs(self, objectName=None):
        if objectName:
            return sorted([ slot for slot in self.__getSlotsDescrs() if slot.object == objectName ])
        return self.__getSlotsDescrs()

    def checkForNewToys(self, slot=None, objectType=None):
        worstRanks = {}
        toyInSlots = self.getToysInSlots(objectType, slotID=slot)
        toyIdsInSlots = set()
        for toy in toyInSlots:
            if toy is None:
                continue
            toyIdsInSlots.add(toy.id)
            toyType = toy.type
            if toyType in worstRanks and worstRanks[toyType] > toy.rank or toyType not in worstRanks:
                worstRanks[toyType] = toy.rank

        objectToyTypes = TOY_TYPES_BY_OBJECT[objectType] if objectType else self.getSlotDescrs()[slot].type
        for toy in self.__getCurrentToys().itervalues():
            toyType = toy.getToyType()
            toyID = toy.getID()
            if toy.getCount() <= 0 or toyType not in objectToyTypes or toy.getUnseenCount() <= 0 or toyID in toyIdsInSlots:
                continue
            if toyType not in worstRanks or toy.getRank() >= int(worstRanks[toyType]):
                return True

        return False

    def getBattleBonus(self, bonusType):
        return calcBattleBonus(bonusType, self._itemsCache.items.festivity.getCollectionDistributions(), NewYearAtmospherePresenter.getLevel())

    def isCollectionCompleted(self, collectionIDs=None):
        totalCounts = ny19.g_cache.toyCountByCollectionID
        collectionDistribution = self._itemsCache.items.festivity.getCollectionDistributions()
        if collectionIDs:
            collectionCount = 0
            totalCount = 0
            for collectionID in collectionIDs:
                collectionCount += sum(collectionDistribution[collectionID])
                totalCount += totalCounts[collectionID]

            return collectionCount == totalCount
        return sum((sum(rankDistrs) for rankDistrs in collectionDistribution)) == sum(totalCounts)

    def getFinishTime(self):
        return self.__endDate

    def sendSeenToys(self, toyIDs):
        self.__commandProcessor.sendSeen(toyIDs)

    def sendSeenToysInCollection(self, toyIDs):
        result = []
        for toyID in toyIDs:
            result.extend((toyID, 0))

        self.__commandProcessor.seenInCollection(result)

    def sendViewAlbum(self, settingID, rank):
        self.__commandProcessor.viewAlbum(settingID, rank)

    def addToys(self, toysDict=None):
        self.__commandProcessor.addToys(toysDict)

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

    def __eventsDataUpdate(self):
        state = None
        endDate = None
        for action in self._eventsCache.getActions().itervalues():
            if 'EventState' in action.getModifiersDict():
                actionDate = action.getFinishTime()
                endDate = actionDate if endDate is None else min(action, endDate)
                state = action.getModifiersDict()['EventState'].getState()

        self.__endDate = endDate
        self.__setState(state)
        return

    def __setState(self, state):
        state = _getState(state)
        if self.__state != state:
            msg = _NY_STATE_SYS_MESSAGES.get((self.__state, state))
            if msg is not None:
                SystemMessages.pushMessage(i18n.makeString(msg.keyText), priority=msg.priority, type=msg.type)
            self.__state = state
            self.onStateChanged()
        if state == NY_STATE.FINISHED:
            self.__checkUnusedRewards()
        else:
            self.__isCheckedUnusedRewards = False
        return

    def __hangToys(self):
        for slotID, toyID in enumerate(self._itemsCache.items.festivity.getSlots()):
            self.__update3DSlot(toyID, slotID, False)

    def __update3DSlot(self, toyID, slotID, withHangingEffect=True):
        toy = self.getToyDescr(toyID)
        self._customizableObjectMgr.updateSlot(self.__getSlotsDescrs()[slotID], toy, withHangingEffect)

    def __createLevels(self):
        self.__levelsInfo = {}
        for level in getLevelIndexes():
            self.__levelsInfo[level] = LevelInfo(level)

    def __clear(self):
        self.__levelsInfo = None
        self.__endDate = None
        return

    def __getSlotsDescrs(self):
        return tuple(ny19.g_cache.slots)

    def __getCurrentToys(self):
        return self._itemsCache.items.festivity.getToys()

    def __checkUnusedRewards(self):
        if self.__isCheckedUnusedRewards:
            return
        else:
            self.__isCheckedUnusedRewards = True
            if self.__levelsInfo is None:
                self.__createLevels()
            hasUnusedRewards = False
            for levelInfo in self.__levelsInfo.itervalues():
                if not levelInfo.isQuestCompleted():
                    continue
                if not levelInfo.discountApplied() or levelInfo.hasTankman() and not levelInfo.tankmanIsRecruited():
                    hasUnusedRewards = True
                    break

            if hasUnusedRewards:
                SystemMessages.pushMessage(i18n.makeString(NY.NOTIFICATION_REWARDSREMINDER), SystemMessages.SM_TYPE.NewYearRewardsReminder)
            return
