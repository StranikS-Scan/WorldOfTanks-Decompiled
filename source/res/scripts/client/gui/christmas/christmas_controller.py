# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/christmas/christmas_controller.py
from collections import defaultdict
import WWISE
import BigWorld
import ChristmassTreeManager as _ctm
import Event
from AnimatedGiftBox import AnimatedGiftBox
from account_helpers.AccountSettings import AccountSettings, CHRISTMAS_NEW_TOYS, CHRISTMAS_SHOWN_AWARDS
from adisp import async
from christmas_shared import CHRISTMAS_TREE_SCHEMA, TOY_TYPE_ID_TO_NAME, calcChristmasTreeRating, getToyID, ratingToLevelRange, EVENT_STATE, CHEST_STATE, TREE_RATING, FINAL_PRIZE_TOKEN_PREFIX, getUpperLvlBound
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.christmas.christmas_items import ChristmasItemInfo, ChristmasItem
from gui.shared.gui_items.processors.christmas import ToysConvertor, ChristmasTreeFiller, ChestBonusReceiver
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.decorators import process
import gui.awards.event_dispatcher as shared_events

class _TreeModel(object):

    @classmethod
    def installItem(cls, itemId, slotID):
        isLeftGarland = slotID == 5
        _ctm.hangToyByID(itemId, slotID, isLeftGarland)

    @classmethod
    def uninstallItem(cls, slotID):
        _ctm.removeToy(slotID)


class ChristmasStorage(object):

    def __init__(self, inventory, tree, newToys):
        super(ChristmasStorage, self).__init__()
        self.__inventory = inventory.copy()
        self.__itemsCache = []
        self.__ranksStats = defaultdict(lambda : 0)
        self.__cacheIsInvalid = True
        self.__newToys = set(newToys)
        self.__tree = tree[:]
        self.__initialTree = tree[:]
        self.__alchemyCache = [0] * 5
        self.onInventoryChanged = Event.Event()

    def init(self):
        g_christmasCtrl.onToysCacheChanged += self.__invalidateInventory

    def fini(self):
        g_christmasCtrl.onToysCacheChanged -= self.__invalidateInventory

    def getToyID(self, slotID):
        return self.__tree[slotID]

    def getToysOnTree(self):
        return self.__tree

    @property
    def inventory(self):
        return self.__inventory

    def getInventoryItems(self, objectType):
        self.__invalidateCache()
        if objectType is not None:
            return filter(lambda info: info.item.targetType == objectType, self.__itemsCache)
        else:
            return self.__itemsCache
            return

    def getRankStats(self):
        self.__invalidateCache()
        return self.__ranksStats

    def isStateChanged(self):
        return self.__tree != self.__initialTree

    def moveToy(self, toyId, sourceID=None, targetID=None):
        self.__moveToyForCache(self.__tree, toyId, sourceID, targetID)

    def getTreeLevelInfo(self):
        return g_christmasCtrl.getRatingInfo(self.__tree)

    def discardNew(self, toyId):
        if toyId in self.__newToys:
            self.__newToys.discard(toyId)
            self.__cacheIsInvalid = True

    def resetAlchemy(self):
        for itemId in self.__alchemyCache:
            self.__increaseInventory(itemId)

        self.__alchemyCache = [0] * 5

    def moveAlchemyToy(self, toyId, sourceID=None, targetID=None):
        self.__moveToyForCache(self.__alchemyCache, toyId, sourceID, targetID)

    def getAlchemyCache(self):
        return self.__alchemyCache

    def __moveToyForCache(self, cache, toyId, sourceID=None, targetID=None):
        if sourceID is not None and targetID is not None:
            cache[sourceID], cache[targetID] = cache[targetID], cache[sourceID]
        elif sourceID is not None:
            cache[sourceID] = 0
            self.__increaseInventory(toyId)
        elif targetID is not None:
            removable = cache[targetID]
            if removable != 0:
                self.__increaseInventory(removable)
            self.__decreaseInventory(toyId)
            cache[targetID] = toyId
        return

    def __decreaseInventory(self, toyId):
        self.__cacheIsInvalid = True
        self.__inventory[toyId] -= 1
        if self.__inventory[toyId] == 0:
            del self.__inventory[toyId]

    def __increaseInventory(self, toyId):
        if toyId is not None and toyId > 0:
            self.__cacheIsInvalid = True
            count = self.__inventory.get(toyId, 0)
            self.__inventory[toyId] = count + 1
        return

    def __invalidateInventory(self, diff, fullResync=False):
        if len(diff) > 0 or fullResync:
            self.__cacheIsInvalid = True
        if fullResync:
            self.__initialTree = g_christmasCtrl.getChristmasTree()
            self.__tree = self.__initialTree[:]
            self.__inventory = g_christmasCtrl.getToysCache()
            for slotId, toyID in enumerate(self.__alchemyCache):
                if toyID is not None and toyID > 0:
                    if toyID in self.__inventory:
                        self.__decreaseInventory(toyID)
                    else:
                        self.__alchemyCache[slotId] = 0

        else:
            for itemID, delta in diff.iteritems():
                currCount = self.__inventory.get(itemID, 0)
                newCount = currCount + delta
                if newCount < 0:
                    for idx, alchemyToyId in enumerate(self.__alchemyCache):
                        if itemID == alchemyToyId and newCount < 0:
                            self.moveAlchemyToy(itemID, sourceID=idx)
                            newCount += 1

                if newCount < 0:
                    for idx, toyOnTreeID in enumerate(self.__tree):
                        if itemID == toyOnTreeID and self.__initialTree[idx] != itemID and newCount < 0:
                            self.moveToy(itemID, sourceID=idx)
                            newCount += 1

                if newCount < 0:
                    LOG_ERROR('Invalid delta for item:', itemID, delta)
                elif newCount == 0:
                    if itemID in self.__inventory:
                        del self.__inventory[itemID]
                        self.__newToys.discard(itemID)
                else:
                    self.__inventory[itemID] = newCount
                if delta > 0:
                    self.__newToys.add(itemID)

        self.onInventoryChanged()
        return

    def __invalidateCache(self):
        if self.__cacheIsInvalid:
            self.__itemsCache = []
            self.__ranksStats = defaultdict(lambda : 0)
            for itemId, count in self.__inventory.iteritems():
                if count > 0:
                    itemInfo = g_christmasCtrl.getChristmasItemInfo(itemId, count, itemId in self.__newToys)
                    self.__itemsCache.append(itemInfo)
                    self.__ranksStats[itemInfo.item.rank] += count

            self.__cacheIsInvalid = False


class _ChristmasController(object):

    def __init__(self):
        super(_ChristmasController, self).__init__()
        self.__treeModel = _TreeModel()
        self.__knownToys = None
        self.__toysCache = {}
        self.__toysTotal = {}
        self.__christmasTree = [0] * len(CHRISTMAS_TREE_SCHEMA)
        self.__eventState = EVENT_STATE.NOT_STARTED
        self.__conversions = {}
        self.__storage = None
        self.__activeGUI = None
        self.__clientChristmas = None
        self.__areAwardsWindowsLocked = False
        self.__isFightBtnLocked = False
        self.__isNavigationDisabled = False
        self.__forceStorageResync = False
        self.__eventManager = Event.EventManager()
        self.onEventStopped = Event.Event(self.__eventManager)
        self.onEventStarted = Event.Event(self.__eventManager)
        self.onToysCacheChanged = Event.Event(self.__eventManager)
        self.onChestsUpdate = Event.Event(self.__eventManager)
        self.onOpenChestAnimationStarted = Event.Event(self.__eventManager)
        self.onRibbonAnimationFinished = Event.Event(self.__eventManager)
        self.onReceivedChestAnimationFinished = Event.Event(self.__eventManager)
        self.onExploseChestAnimationFinished = Event.Event(self.__eventManager)
        self.onCameraSwitchedToHangar = Event.Event(self.__eventManager)
        self.onCameraSwitchedToChest = Event.Event(self.__eventManager)
        self.onCameraSwitchedToTree = Event.Event(self.__eventManager)
        self.onAwardsAndFightBtnLocked = Event.Event(self.__eventManager)
        self.onAwardsAndFightBtnUnlocked = Event.Event(self.__eventManager)
        return

    def start(self):
        self.__clientChristmas = BigWorld.player().christmas
        self.__clientChristmas.onGlobalDataChanged += self.__updateGlobalState
        _ctm.g_christMassManager.onTreeLoaded += self.__onTreeLoaded
        _ctm.g_christMassManager.onChestLoaded += self.__onChestLoaded
        self.__clientChristmas.onInventoryChanged += self.__updateInventory
        self.__clientChristmas.onTreeChanged += self.__updateInventory
        self.__knownToys = self.__clientChristmas.getAllToys()
        self.__updateConversion()
        self.__updateInventory(self.__clientChristmas.getMyToys())

    def stop(self, clearCache=False):
        _ctm.g_christMassManager.onTreeLoaded -= self.__onTreeLoaded
        _ctm.g_christMassManager.onChestLoaded -= self.__onChestLoaded
        if clearCache:
            self.__toysCache, self.__toysTotal = {}, {}
        self.__stopEvent()
        if self.__clientChristmas is not None:
            self.__clientChristmas.onTreeChanged -= self.__updateInventory
            self.__clientChristmas.onInventoryChanged -= self.__updateInventory
            self.__clientChristmas.onGlobalDataChanged -= self.__updateGlobalState
            self.__clientChristmas = None
        return

    def lockAwardsWindowsAndFightBtn(self, lockFightBtn=True, lockAwardsWindows=True):
        self.__areAwardsWindowsLocked = lockAwardsWindows
        self.__isFightBtnLocked = lockFightBtn
        self.onAwardsAndFightBtnLocked()

    def unlockAwardsWindowsAndFightBtn(self):
        self.__areAwardsWindowsLocked = False
        self.__isFightBtnLocked = False
        self.onAwardsAndFightBtnUnlocked()

    def areAwardsWindowsLocked(self):
        return self.__areAwardsWindowsLocked

    def isFightBtnLocked(self):
        return self.__isFightBtnLocked

    def setGUIActive(self, guiType):
        self.__activeGUI = guiType
        self.__saveNewToysToAccountSettings()

    def showToysOnTreeModel(self):
        for slotID, itemID in enumerate(self.__christmasTree, start=1):
            if itemID is not None and itemID > 0:
                self.__treeModel.installItem(itemID, slotID)
            self.__treeModel.uninstallItem(slotID)

        return

    def setOnclickCallback(self, callbacks):
        _ctm.g_christMassManager.setOnclickCallback(callbacks)

    def clearOnclickCallback(self):
        _ctm.g_christMassManager.clearOnclickCallback()

    def isEventInProgress(self):
        if self.__clientChristmas is not None:
            return self.__clientChristmas.eventInProgress
        else:
            return self.__eventState == EVENT_STATE.IN_PROGRESS
            return

    def isChestOnScene(self):
        return _ctm.g_christMassManager.giftBox.getState() != AnimatedGiftBox.BoxState.HIDDEN

    def isChestOpened(self):
        return _ctm.g_christMassManager.giftBox.getState() == AnimatedGiftBox.BoxState.DONE

    def mayRemoveChest(self):
        giftBox = _ctm.g_christMassManager.giftBox
        return giftBox.getState() in (AnimatedGiftBox.BoxState.WAITING_FOR_OPEN_RESPONSE, AnimatedGiftBox.BoxState.DONE, AnimatedGiftBox.BoxState.OPENING) if giftBox is not None else False

    def isKnownToysReceived(self):
        return self.__knownToys is not None

    def getChristmasItemByID(self, itemId):
        if self.__knownToys:
            toyInfo = self.__knownToys.get(itemId)
            if toyInfo is not None:
                return ChristmasItem(itemId, toyInfo)
        return

    def getChristmasItemInfo(self, itemId, count=None, isNew=False):
        if count is None:
            count = self.__toysCache.get(itemId, 0)
        item = self.getChristmasItemByID(itemId)
        return ChristmasItemInfo(item, count, isNew) if item is not None else None

    def getRatingInfo(self, toys=None):
        if toys is None:
            toys = self.__christmasTree
        rating = 0
        if self.__knownToys:
            rating = calcChristmasTreeRating(self.__knownToys, toys)
        levelInfo = self.__getLevelForRating(rating)
        if levelInfo['maxRating'] == TREE_RATING[-1]:
            levelInfo['maxRating'] -= 1
        result = levelInfo.copy()
        result['rating'] = rating
        return result

    def getTempStorage(self, createNew=False):
        if self.__storage is None or createNew:
            self.__storage = ChristmasStorage(self.getToysCache(), self.getChristmasTree(), self.__getNewToysFromAccountSettings())
        return self.__storage

    def getGlobalState(self):
        if self.__clientChristmas is None:
            return EVENT_STATE.NOT_STARTED
        else:
            return self.__clientChristmas.getState()
            return

    def getToysCache(self):
        return self.__toysCache.copy()

    def getChristmasTree(self):
        return list(self.__christmasTree)

    def hasNewToys(self):
        return bool(self.__getNewToysFromAccountSettings())

    def newToysCount(self):
        return sum(self.__getNewToysFromAccountSettings().values())

    @staticmethod
    def getToyID(tokenUid):
        return getToyID(tokenUid)

    @staticmethod
    def getSlots():
        result = {}
        for idx, slotType in enumerate(CHRISTMAS_TREE_SCHEMA):
            result[idx] = TOY_TYPE_ID_TO_NAME[slotType]

        return result

    def getToysMaxRank(self):
        if self.__knownToys:
            return max([ toyInfo['rank'] for toyInfo in self.__knownToys.values() ])

    def getConversionInfo(self, rank):
        return self.__conversions.get(rank)

    def isEnoughForConversion(self, rank, count):
        conversion = self.getConversionInfo(rank)
        return conversion is not None and count is not None and conversion['number'] <= count

    def installItem(self, itemId, slotId):
        if itemId:
            self.__treeModel.installItem(itemId, slotId + 1)
        else:
            self.uninstallItem(slotId)

    def uninstallItem(self, slotID):
        self.__treeModel.uninstallItem(slotID + 1)

    @process()
    def applyChanges(self, storage, useConfirmation=False):
        data = storage.getToysOnTree()
        treeInfo = self.getRatingInfo(data)
        result = yield ChristmasTreeFiller(data, treeInfo, useConfirmation).request()
        if result.success:
            if len(result.userMsg):
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        else:
            self.showToysOnTreeModel()

    @async
    @process('upgradingChristmasItem')
    def doAlchemy(self, items, storage, callback):
        inventorySynced = True
        if storage.isStateChanged():
            data = storage.getToysOnTree()
            treeInfo = self.getRatingInfo(data)
            result = yield ChristmasTreeFiller(data, treeInfo, False).request()
            inventorySynced = result.success
        if inventorySynced:
            result = yield ToysConvertor(items).request()
            if len(result.userMsg):
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.HIGH)
            callback(result.auxData)
        else:
            callback(-1)

    def openChest(self):
        if not self.isEventInProgress():
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CHRISTMAS_COMMON_ERROR, type=SystemMessages.SM_TYPE.Error)
            self.__isNavigationDisabled = False
            return
        self.__isNavigationDisabled = True
        self.onOpenChestAnimationStarted()
        if self.isChestOnScene() and not self.isChestOpened():
            self.openChestRequest()
            self.playChestWaitBonusAnimation()
        else:
            _ctm.playReceiveChestAnimation(callback=self.openChest)

    def finishRibbonAnimation(self):
        self.__isNavigationDisabled = False
        self.onRibbonAnimationFinished()

    @process()
    def openChestRequest(self):
        """
        Send server request for open chest and receive gifts
        """
        result = yield ChestBonusReceiver(self.__getClosedChests()).request()
        if len(result.userMsg) and not result.success:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.HIGH)

    def switchToHangar(self):
        _ctm.switchCameraToHangar(callback=self.onCameraSwitchedToHangar)

    def switchToTree(self):
        _ctm.switchCameraToTree(callback=self.onCameraSwitchedToTree)

    def switchToTank(self):
        _ctm.switchCameraToTank(callback=self.onCameraSwitchedToTree)

    def switchToChest(self):
        _ctm.switchCameraToChest(callback=self.onCameraSwitchedToChest)

    def playReceiveChestAnimation(self):
        _ctm.playReceiveChestAnimation(callback=self.onReceivedChestAnimationFinished)

    @staticmethod
    def playChestWaitBonusAnimation():
        _ctm.playChestWaitBonusAnimation()

    def playExploseChestAnimation(self):
        _ctm.playExploseChestAnimation(callback=self.onExploseChestAnimationFinished)

    @staticmethod
    def addChestToScene():
        _ctm.addChestToScene()

    @staticmethod
    def removeChestFromScene():
        _ctm.removeChestFromScene()

    def getClosedChestsCount(self):
        return sum(self.__getClosedChests().values())

    def isNavigationDisabled(self):
        return self.__isNavigationDisabled

    def addNewToysToAccountSettings(self, newToys):
        self.__saveNewToysToAccountSettings(newToys)

    def __getChristmasMaxLvlEverReached(self):
        levels = [ int(chestID.split(FINAL_PRIZE_TOKEN_PREFIX)[1]) for chestID in self.__getMyChests().iterkeys() ]
        return max(levels) if levels else 0

    def __getClosedChests(self):
        """
        Gets Christmas Lvl closed chests tokens {tokenID, count}
        token represents a closed chest, which exchange later on gifts by client request
        """
        return {chestID:state for chestID, state in self.__getMyChests().iteritems() if state == CHEST_STATE.RECEIVED}

    def __getMyChests(self):
        """
        Gets Christmas Lvl chests tokens {tokenID, count}
        token represents a chest
        """
        return self.__clientChristmas.getMyChests() if self.__clientChristmas else {}

    def __startEvent(self):
        self.__eventState = EVENT_STATE.IN_PROGRESS
        self.onEventStarted()

    def __pauseEvent(self):
        _ctm.enableEvent(False)
        if self.__eventState != EVENT_STATE.IN_PROGRESS:
            self.showToysOnTreeModel()
        self.__eventState = EVENT_STATE.SUSPENDED
        self.onEventStopped()

    def __stopEvent(self):
        self.__eventState = EVENT_STATE.FINISHED
        self.onEventStopped()

    def __updateInventory(self, diff=None):
        if diff is not None:
            self.__toysTotal.update(diff)
        self.__updateTree()
        toysInventory = self.__calcToysInInventory()
        delta = self.__calcToysDelta(toysInventory)
        self.__toysCache = toysInventory
        self.onToysCacheChanged(delta, self.__forceStorageResync)
        self.__forceStorageResync = False
        self.onChestsUpdate(self.__getClosedChests())
        self.__checkChests()
        return

    def __calcToysDelta(self, newInventory):
        delta = {}
        for toyId, count in newInventory.iteritems():
            deltaCount = count - self.__toysCache.get(toyId, 0)
            if deltaCount != 0:
                delta[toyId] = deltaCount

        return delta

    def __calcToysInInventory(self):
        result = self.__toysTotal.copy()
        for itemID in self.__christmasTree:
            if itemID != 0:
                count = result.get(itemID, 0)
                if count > 0:
                    result[itemID] = count - 1

        return result

    def __updateTree(self):
        if self.__clientChristmas:
            serverTreeState = self.__clientChristmas.christmasTree
            self.__forceStorageResync = self.__christmasTree != serverTreeState
            self.__christmasTree = serverTreeState
            level = self.getRatingInfo().get('level', 0)
            WWISE.WW_setRTCPGlobal('RTPC_ext_ev_christmas_tree_level', level)

    def __updateGlobalState(self):
        eventState = self.getGlobalState()
        self.__knownToys = self.__clientChristmas.getAllToys()
        if eventState in (EVENT_STATE.NOT_STARTED, EVENT_STATE.FINISHED):
            self.__stopEvent()
        elif eventState == EVENT_STATE.IN_PROGRESS:
            self.__startEvent()
        elif eventState == EVENT_STATE.SUSPENDED:
            self.__pauseEvent()
        else:
            LOG_ERROR('Wrong event state', eventState)
            return
        self.__updateConversion()

    def __updateConversion(self):
        self.__conversions = {}
        if self.__clientChristmas is not None:
            conversions = self.__clientChristmas.getConversions()
            for conversion in conversions.values():
                source, result = conversion['from'], conversion['to']
                self.__conversions[source['rank']] = {'number': source['number'],
                 'result': result}

        return

    def __saveNewToysToAccountSettings(self, newToys=None):
        toys = self.__getNewToysFromAccountSettings()
        if newToys is not None:
            for toyID, count in self.__filterNewToys(newToys).iteritems():
                oldCount = toys.get(toyID, 0)
                toys[toyID] = oldCount + count

        else:
            toys = self.__filterNewToys(toys)
        AccountSettings.setSettings(CHRISTMAS_NEW_TOYS, toys)
        return

    def __filterNewToys(self, toys):
        result = {}
        for toyID, count in toys.iteritems():
            if self.getChristmasItemByID(toyID).targetType != self.__activeGUI:
                result[toyID] = count

        return result

    @staticmethod
    def __getNewToysFromAccountSettings():
        return AccountSettings.getSettings(CHRISTMAS_NEW_TOYS)

    def __getLevelForRating(self, rating):
        level, lower, upper = ratingToLevelRange(rating)
        maxLvlEverReached = self.__getChristmasMaxLvlEverReached()
        if maxLvlEverReached > level:
            level = maxLvlEverReached
            upper = getUpperLvlBound(level)
        return {'level': level,
         'minRating': lower,
         'maxRating': upper}

    def __onTreeLoaded(self):
        """
        After 3D christmas tree loaded on scene update tree model and set christmas state
        """
        self.__updateTree()
        self.showToysOnTreeModel()
        self.__updateGlobalState()

    def __onChestLoaded(self):
        """
        After 3D chest loaded on scene update its model
        """
        if self.getGlobalState() != EVENT_STATE.FINISHED and self.getClosedChestsCount():
            self.addChestToScene()

    def __checkChests(self):
        if self.isEventInProgress():
            chests = self.__getClosedChests()
            shownLvlsAwards = set(AccountSettings.getSettings(CHRISTMAS_SHOWN_AWARDS))
            lvls = []
            for chestID, state in chests.iteritems():
                if chestID not in shownLvlsAwards and state == CHEST_STATE.RECEIVED:
                    lvls.append(int(chestID.strip(FINAL_PRIZE_TOKEN_PREFIX)))
                    shownLvlsAwards.add(chestID)

            if lvls and max(lvls) > 1:
                shared_events.showLvlUpChristmasAward(max(lvls), self)
            AccountSettings.setSettings(CHRISTMAS_SHOWN_AWARDS, shownLvlsAwards)


g_christmasCtrl = _ChristmasController()
