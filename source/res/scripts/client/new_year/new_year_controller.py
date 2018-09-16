# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/new_year_controller.py
from collections import namedtuple, defaultdict
import BigWorld
import Event
from account_helpers.AccountSettings import AccountSettings, CHRISTMAS_BOXES, CHRISTMAS_FINISHED_AWARDS_SHOWN, CHRISTMAS_STARTED_AWARDS_SHOWN, CHRISTMAS_VEH_DISCOUNTS, CHRISTMAS_TMANS_INV_IDS
from chat_shared import SYS_MESSAGE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from gui import SystemMessages, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.server_events.bonuses import getTutorialBonuses
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, i18n
from items import new_year_types
from items.new_year_types import TOY_TYPES, INVALID_TOY_ID, calculateCraftCost, NY_STATE, NATIONAL_SETTINGS
from messenger.m_constants import PROTO_TYPE, SCH_CLIENT_MSG_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from new_year.new_year_toy import ToyItemInfo
from new_year.requester import ny_contexts
from new_year.requester.new_year_requester import NYRequestController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from gui import GUI_SETTINGS
from items.new_year_types import SETTING_BY_NATION
_NewYearProgress = namedtuple('AtmosphereLevel', ('level', 'maxLevel', 'progress', 'bound'))
_EmptySlot = namedtuple('EmptySlot', ['id'])
_TOKEN_SYS_MSG_TYPE = SYS_MESSAGE_TYPE.tokenQuests.index()
NEW_YEAR_HANGAR_PATH = 'h07_newyear_2015'

class _NYBaseStorage(object):

    def __init__(self):
        super(_NYBaseStorage, self).__init__()
        self._cny = None
        self._nyCtrl = None
        self.__requestCtrl = None
        return

    def init(self, nyCtrl, requester):
        self._cny = BigWorld.player().newYear
        self._nyCtrl = nyCtrl
        self.__requestCtrl = requester

    def clear(self):
        self.__requestCtrl = None
        return

    def fini(self):
        self._cny = None
        self._nyCtrl = None
        self.__requestCtrl = None
        return

    def getDescriptors(self):
        raise NotImplementedError

    def _validateRequest(self, ctx):
        return self.__requestCtrl.validateRequest(ctx)

    def _sendRequest(self, ctx):
        """
        Sends request to the server
        :param ctx:
        :return: bool, True if all checkings are passed and request sent to server, otherwise False
        """
        return self.__requestCtrl.request(ctx, self._handleRequestResult)

    def _handleRequestResult(self, response):
        pass


class _NYContainersStorage(_NYBaseStorage):

    def __init__(self):
        super(_NYContainersStorage, self).__init__()
        self._count = 0
        self.onCountChanged = Event.Event()
        self.onItemOpened = Event.Event()
        self.onItemOpenError = Event.Event()
        self._openingItemId = None
        return

    @property
    def count(self):
        return self._count

    @property
    def openingItemId(self):
        return self._openingItemId

    def fini(self):
        super(_NYContainersStorage, self).fini()
        self._openingItemId = None
        return

    def hasItem(self, itemId):
        return None

    def isUnderOpening(self):
        return self._openingItemId is not None

    def canOpen(self, itemID=None):
        return self._validateRequest(self._getContext()(itemID or self._getNextItem()))

    def open(self, itemID=None):
        """
        Do send request
        :param itemID:
        :return: bool, True if request has been successfully sent to server, otherwise False
        """
        self._openingItemId = itemID or self._getNextItem()
        return self._sendRequest(self._getContext()(self._openingItemId))

    def _getContext(self):
        raise NotImplementedError

    def _getNextItem(self):
        return None

    def _onDataChanged(self, diff):
        pass

    def _handleRequestResult(self, response):
        if not response.isSuccess():
            self.onItemOpenError(self._openingItemId)
        self._openingItemId = None
        return


class _NewYearBoxStorage(_NYContainersStorage):

    def __init__(self):
        super(_NewYearBoxStorage, self).__init__()
        self._BOX_ID_ORDER = None
        return

    def getDescriptors(self):
        """
        :return: {boxStringId: BoxDescriptor}
        """
        return new_year_types.g_cache.boxes

    def init(self, nyCtrl, requester):
        super(_NewYearBoxStorage, self).init(nyCtrl, requester)
        if self._cny is not None:
            self._onDataChanged(self._cny.boxes)
            self._cny.onBoxesChanged += self._onDataChanged
        return

    def __getBoxIdOrder(self):
        if not self._BOX_ID_ORDER and self._cny:
            maxIndex = len(NATIONAL_SETTINGS) + 10
            self._BOX_ID_ORDER = [ bDescr.id for bDescr in sorted(self.getDescriptors().values(), key=lambda i: 2 * (self._nyCtrl.getSettingIndexInNationsOrder(i.setting) if i.setting in NATIONAL_SETTINGS else maxIndex) + int(not i.present)) ]
        return self._BOX_ID_ORDER

    def clear(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handleSysMsg
        if self._cny is not None:
            self._cny.onBoxesChanged -= self._onDataChanged
        self._count = 0
        super(_NewYearBoxStorage, self).clear()
        return

    def fini(self):
        self.clear()
        super(_NewYearBoxStorage, self).fini()

    def hasItem(self, itemId):
        return self._cny.boxes.get(itemId, 0) > 0

    def getOrderedBoxes(self):
        outcome = []
        boxDescrs = self.getDescriptors()
        for boxId in self.__getBoxIdOrder():
            boxes = self._cny.boxes
            count = boxes.get(boxId, 0)
            if count > 0:
                outcome.append((boxDescrs[boxId], count))

        return outcome

    def open(self, itemID=None):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__handleSysMsg
        return super(_NewYearBoxStorage, self).open(itemID)

    def getItemIDBySetting(self, setting):
        ordered = self.getOrderedBoxes()
        for descr, count in ordered:
            if descr.setting == setting:
                return descr.id

        return None

    def _onDataChanged(self, diff):
        accountSetting = CHRISTMAS_BOXES
        actualItems = self._cny.boxes
        savedBoxes = AccountSettings.getSettings(accountSetting)
        self._count = 0
        for bCount in actualItems.itervalues():
            self._count += bCount

        addedCount = 0
        removedCount = 0
        addedInfo = defaultdict(int)
        for boxId, newCount in diff.iteritems():
            nDiff = newCount - savedBoxes.get(boxId, 0)
            if nDiff > 0:
                addedCount += nDiff
                addedInfo[boxId] += nDiff
            if nDiff < 0:
                removedCount += abs(nDiff)

        if addedCount > 0 or removedCount > 0:
            self.onCountChanged(addedCount, removedCount, addedInfo)
        if savedBoxes != actualItems:
            LOG_DEBUG('New account settings "{}" storing: {}'.format(accountSetting, actualItems))
            AccountSettings.setSettings(accountSetting, actualItems)

    def _getNextItem(self):
        for boxId in self.__getBoxIdOrder():
            boxes = self._cny.boxes
            if boxId in boxes and boxes[boxId] > 0:
                return boxId

        return None

    def _getContext(self):
        return ny_contexts.NYBoxOpenContext

    def _handleRequestResult(self, response):
        if not response.isSuccess():
            super(_NewYearBoxStorage, self)._handleRequestResult(response)
            g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handleSysMsg

    def __handleSysMsg(self, _, message):
        if message.type == _TOKEN_SYS_MSG_TYPE:
            if 'completedQuestIDs' in message.data:
                completedQuestIDs = message.data['completedQuestIDs']
                if self._openingItemId in completedQuestIDs:
                    self.onItemOpened(self._openingItemId, self.__extractBonuses(message.data))
                    g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handleSysMsg
                    self._openingItemId = None
        return

    def __extractBonuses(self, data):
        outcome = []
        for k, value in data.iteritems():
            bonusObj = []
            if k == 'completedQuestIDs':
                continue
            elif k == 'vehicles':
                for vehiclesDict in value:
                    bonusObj.extend(getTutorialBonuses(k, vehiclesDict))

            else:
                bonusObj = getTutorialBonuses(k, value)
            outcome.extend(bonusObj)

        return outcome


class _NewYearChestStorage(_NYContainersStorage):
    _eventsCache = dependency.descriptor(IEventsCache)

    def init(self, nyCtrl, requester):
        super(_NewYearChestStorage, self).init(nyCtrl, requester)
        self._count = self.__getActualChestCount()
        if self._cny is not None:
            self._cny.onChestsChanged += self._onDataChanged
        return

    def clear(self):
        if self._cny is not None:
            self._cny.onChestsChanged -= self._onDataChanged
        self._count = 0
        super(_NewYearChestStorage, self).clear()
        return

    def fini(self):
        self.clear()
        super(_NewYearChestStorage, self).fini()

    def getDescriptors(self):
        return new_year_types.g_cache.chests

    def hasItem(self, itemId):
        return self._cny.chests.get(itemId, 0) > 0

    def _getContext(self):
        return ny_contexts.NYChestOpenContext

    def _getNextItem(self):
        minChest = None
        for chestId, amount in self._cny.chests.items():
            if amount > 0:
                currentChest = self.getDescriptors().get(chestId, None)
                if minChest is None or currentChest is not None and currentChest.level < minChest.level:
                    minChest = currentChest

        return minChest.id if minChest is not None else None

    def _handleRequestResult(self, response):
        if response.isSuccess():
            hidden_quests = self._eventsCache.getHiddenQuests()
            nyQuest = hidden_quests.get(self._openingItemId, None)
            bonuses = nyQuest.getBonuses() if nyQuest is not None else None
            self.onItemOpened(self._openingItemId, bonuses)
            self._openingItemId = None
        else:
            super(_NewYearChestStorage, self)._handleRequestResult(response)
        return

    def _onDataChanged(self, diff):
        newChestsCount = self.__getActualChestCount()
        nD = newChestsCount - self._count
        self._count = newChestsCount
        if nD != 0:
            addedCount = max(0, nD)
            self.onCountChanged(addedCount, abs(min(nD, 0)), {k:v for k, v in diff.iteritems() if v > 0})
            if addedCount > 0:
                g_eventBus.handleEvent(events.LoadViewEvent(alias=VIEW_ALIAS.NY_LEVEL_UP, ctx={'level': self._cny.level}), EVENT_BUS_SCOPE.LOBBY)

    def __getActualChestCount(self):
        newChestsCount = 0
        for v in self._cny.chests.itervalues():
            newChestsCount += v

        return newChestsCount


class _DiscountsStorage(_NYBaseStorage):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(_DiscountsStorage, self).__init__()
        self.onUpdated = Event.Event()

    def fini(self):
        self.clear()
        super(_DiscountsStorage, self).fini()

    def getDiscounts(self):
        raise NotImplementedError


class _VehicleDiscountsStorage(_DiscountsStorage):

    def __init__(self):
        super(_VehicleDiscountsStorage, self).__init__()
        self.__discountsCache = None
        return

    def init(self, nyCtrl, requester):
        super(_VehicleDiscountsStorage, self).init(nyCtrl, requester)
        self.__discountsCache = self.__initLocalCache()
        self._cny.onVariadicDiscountsChanged += self.__onVariadicDiscountsChanged
        g_clientUpdateManager.addCallback('goodies', self.__onGoodiesUpdated)

    def clear(self):
        if self._cny:
            self.__discountsCache = None
            self._cny.onVariadicDiscountsChanged -= self.__onVariadicDiscountsChanged
        g_clientUpdateManager.removeCallback('goodies', self.__onGoodiesUpdated)
        super(_VehicleDiscountsStorage, self).clear()
        return

    def getDescriptors(self):
        return new_year_types.g_cache.variadicDiscounts

    def getDiscounts(self):
        return self._cny.variadicDiscounts

    def getClientDiscountsCache(self):
        return self.__discountsCache

    def getBoughtVehicle(self, level):
        """
        Provides vehicle that was bought using NY discount.
        :param level: NY atmosphere level
        :return gui.shared.gui_items.Vehicle:
        """
        savedDiscounts = AccountSettings.getSettings(CHRISTMAS_VEH_DISCOUNTS)
        if level in savedDiscounts:
            discountId = savedDiscounts[level]
            discount = self.__discountsCache[level].get(discountId)
            if discount:
                vehicle = self._itemsCache.items.getItemByCD(typeCompDescr=discount.target.targetValue)
                if vehicle:
                    return vehicle
                LOG_ERROR("Couldn't find vehicle by provided ID = {}".format(discount.target.targetValue))
            else:
                LOG_ERROR("Couldn't find discount by provided ID = {}".format(discountId))
        return None

    def activateVehicleDiscount(self, discountID, variadicDiscountID, vehName, vehIntCD, discountVal):
        self._sendRequest(ny_contexts.NYSelectDiscount(discountID, variadicDiscountID, vehName, vehIntCD, discountVal))

    def extractLevelFromDiscountID(self, vdKey):
        return int(vdKey.split(':').pop())

    def extractDiscountIDByLvl(self, level):
        strId = 'ny18:vd:{}'.format(level)
        return strId if strId in self.getDescriptors() else None

    def extractDiscountValueByLevel(self, level):
        discountValue = None
        nyDiscountsDescrs = self.getDescriptors().get(self.extractDiscountIDByLvl(level))
        if nyDiscountsDescrs:
            vehDiscountsDict = self.getClientDiscountsCache()[level - 1]
            if vehDiscountsDict:
                anyDiscount = vehDiscountsDict.itervalues().next()
                discountValue = str(anyDiscount.resource.value)
            else:
                LOG_WARNING('Level "{}" Vehicle Discounts has not been found!'.format(level))
        return discountValue

    def __onVariadicDiscountsChanged(self, diff):
        self.onUpdated()

    def __onGoodiesUpdated(self, diff):
        if not self.__hasNYDiscount(diff.keys()):
            return
        activeDiscounts = self._itemsCache.items.shop.personalVehicleDiscounts
        if activeDiscounts:
            savedDiscounts = AccountSettings.getSettings(CHRISTMAS_VEH_DISCOUNTS)
            needSave = False
            for activeD in activeDiscounts.keys():
                for level, vdDict in enumerate(self.__discountsCache):
                    if activeD in vdDict:
                        if activeD not in savedDiscounts:
                            savedDiscounts[level] = activeD
                            needSave = True

            if needSave:
                AccountSettings.setSettings(CHRISTMAS_VEH_DISCOUNTS, savedDiscounts)
        self.onUpdated()

    def __initLocalCache(self):
        outcome = []
        for i in range(0, self._nyCtrl.maxLevel):
            outcome.append({})

        activeVehDiscounts = self._itemsCache.items.shop.getVehicleDiscountDescriptions()
        for dId, dVal in activeVehDiscounts.iteritems():
            for vdKey, vdDescr in self.getDescriptors().iteritems():
                vdLevel = self.extractLevelFromDiscountID(vdKey)
                rangeFrom, rangeTo = vdDescr.goodiesRange
                if rangeFrom <= dId < rangeTo:
                    outcome[vdLevel - 1][dId] = dVal

        return outcome

    def __hasNYDiscount(self, targetList):
        for changedDid in targetList:
            for vdDict in self.__discountsCache:
                if changedDid in vdDict:
                    return True

        return False


class _TankmanDiscountsStorage(_DiscountsStorage):

    def __init__(self):
        super(_TankmanDiscountsStorage, self).__init__()
        self.onTankmanChoicesChanged = Event.Event()
        self.__data = None
        return

    def init(self, nyCtrl, requester):
        super(_TankmanDiscountsStorage, self).init(nyCtrl, requester)
        self.__updateData()
        self._cny.onVariadicTankmenChanged += self.__onVariadicTankmanChanged
        self._cny.onTankmanChoicesChanged += self.__onTankmanChoicesChanged
        g_clientUpdateManager.addCallback('inventory.{}'.format(GUI_ITEM_TYPE.TANKMAN), self.__inventoryChanged)

    def clear(self):
        if self._cny:
            self._cny.onVariadicDiscountsChanged -= self.__onVariadicTankmanChanged
            self._cny.onTankmanChoicesChanged -= self.__onTankmanChoicesChanged
            g_clientUpdateManager.removeCallback('inventory.{}'.format(GUI_ITEM_TYPE.TANKMAN), self.__inventoryChanged)
        self.__data = None
        super(_TankmanDiscountsStorage, self).clear()
        return

    def getDescriptors(self):
        return new_year_types.g_cache.variadicTankmen

    def getDiscounts(self):
        return self.__data or {}

    def getTankmanNextChoices(self, nation):
        return self._cny.tankmanNextChoices[nation]

    def reqruitTankmen(self, nationID, vehicleInnationID, roleID, variadicTmanDiscountID):
        self.__variadicTmanDiscountID = variadicTmanDiscountID
        self._sendRequest(ny_contexts.NYSelectTankman(nationID, vehicleInnationID, roleID, variadicTmanDiscountID))

    def getRecruitedTankmen(self, level):
        """
        Provides tank woman that was recruited during NY event.
        :param level: NY atmosphere level
        :return gui.shared.gui_items.Tankman:
        """
        saved = AccountSettings.getSettings(CHRISTMAS_TMANS_INV_IDS)
        if level in saved:
            tManInvID = saved[level]
            if tManInvID:
                tankman = self._itemsCache.items.getTankman(tManInvID)
                return tankman
        return None

    def _handleRequestResult(self, response):
        super(_TankmanDiscountsStorage, self)._handleRequestResult(response)
        if response.isSuccess():
            descr = self.getDescriptors().get(self.__variadicTmanDiscountID)
            self.__decreaceDiscountCount(self.__variadicTmanDiscountID)
            saved = AccountSettings.getSettings(CHRISTMAS_TMANS_INV_IDS)
            if descr.level not in saved.keys():
                saved[descr.level] = response.data['tmanInvID']
                AccountSettings.setSettings(CHRISTMAS_TMANS_INV_IDS, saved)
            self._nyCtrl.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_TANKMAN_RECRUITED, auxData=response.data['tmanCompDescr'])
            self.onUpdated()

    def __inventoryChanged(self, diff):
        self.onUpdated()

    def __onVariadicTankmanChanged(self, diff):
        self.__updateData()
        self.onUpdated()

    def __updateData(self):
        self.__data = self._cny.variadicTankmen

    def __onTankmanChoicesChanged(self, diff):
        self.onTankmanChoicesChanged(diff)

    def __decreaceDiscountCount(self, discountID):
        if discountID in self.__data:
            if self.__data[discountID] > 0:
                self.__data[discountID] -= 1
                self.onUpdated()
            else:
                LOG_WARNING("Operation could'n be performed, items is 0 already!")


class _StateHandler(object):

    def __init__(self):
        super(_StateHandler, self).__init__()
        self.__isActive = False
        self.__activateRewardsMsgShown = False
        self.__hadChests = None
        return

    def onLobbyInited(self):
        self.__isActive = True

    def onDisconnected(self):
        self.__activateRewardsMsgShown = False

    def clear(self):
        self.__isActive = False

    def setMessageShown(self, shown=True):
        self.__activateRewardsMsgShown = shown

    def update(self, state, variadicDiscounts, nyCtrl):
        self.__saveState()
        if not self.__isActive:
            return
        if state == NY_STATE.FINISHED:
            presentVD = variadicDiscounts and sum(variadicDiscounts.itervalues()) > 0
            if presentVD or self.__hadChests is True:
                if not (self.__hadChests is True or self.__activateRewardsMsgShown):
                    nyCtrl.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_EVENT_FINISHED)
                    self.__activateRewardsMsgShown = True
            elif not AccountSettings.getSettings(CHRISTMAS_FINISHED_AWARDS_SHOWN):
                SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_STATE_FINISHED, type=SystemMessages.SM_TYPE.Information)
                AccountSettings.setSettings(CHRISTMAS_FINISHED_AWARDS_SHOWN, True)
        elif state == NY_STATE.IN_PROGRESS and not AccountSettings.getSettings(CHRISTMAS_STARTED_AWARDS_SHOWN):
            nyCtrl.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_EVENT_STARTED)
            AccountSettings.setSettings(CHRISTMAS_STARTED_AWARDS_SHOWN, True)

    def __saveState(self):
        cny = BigWorld.player().newYear
        if cny and cny.state == NY_STATE.FINISHED and self.__hadChests is not None:
            self.__hadChests = sum(cny.chests.itervalues()) > 0
        return


class _SysMsgsHandler(object):

    def __init__(self):
        super(_SysMsgsHandler, self).__init__()
        self.__nyCtrl = None
        return

    def init(self, nyCtrl):
        self.__nyCtrl = nyCtrl
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__onSysMsgReceived
        self.__nyCtrl.boxStorage.onCountChanged += self.__onBoxesCountChanged

    def clear(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onSysMsgReceived
        if self.__nyCtrl:
            self.__nyCtrl.boxStorage.onCountChanged -= self.__onBoxesCountChanged

    def fini(self):
        self.clear()
        self.__nyCtrl = None
        return

    def __onBoxesCountChanged(self, _, __, addedInfo):
        descriptors = self.__nyCtrl.boxStorage.getDescriptors()
        for k, v in addedInfo.iteritems():
            boxDescr = descriptors.get(k)
            if boxDescr:
                if boxDescr.present:
                    self.__nyCtrl.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_PRESENT_BOX_RECEIVED, auxData=makeHtmlString('html_templates:newYear/sysMsgs', 'presentFromFriendBody', {'setting': i18n.makeString(NY.system_messages_presentbox_setting_name(boxDescr.setting)),
                     'count': v}))
            LOG_WARNING("Couldn't find descriptor for box '{}'".format(k))

    def __onSysMsgReceived(self, _, message):
        if message.type == _TOKEN_SYS_MSG_TYPE:
            if 'completedQuestIDs' in message.data:
                completedQuestIDs = message.data['completedQuestIDs']
                collectionRewardsSet = set(self.__nyCtrl.collectionRewardsBySettingID)
                passedCollectionRewards = completedQuestIDs.intersection(collectionRewardsSet)
                if passedCollectionRewards:
                    _ms = i18n.makeString
                    for reward in passedCollectionRewards:
                        settingName = NATIONAL_SETTINGS[self.__nyCtrl.collectionRewardsBySettingID.index(reward)]
                        self.__nyCtrl.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_SETTING_COLLECTED, auxData=makeHtmlString('html_templates:newYear/sysMsgs', 'settingCollectedBody', {'setting': _ms(NY.system_messages_setting_name(settingName)),
                         'styles': _ms(VEHICLE_CUSTOMIZATION.getStyleName(settingName)),
                         'titles': _ms(NY.system_messages_setting_collected_titles(settingName)),
                         'emblem': _ms(NY.system_messages_setting_collected_emblem(settingName))}))


class NewYearController(INewYearController):
    __es = _EmptySlot(INVALID_TOY_ID)

    def __init__(self):
        self.__toysCache = None
        self.__inventoryToys = None
        self.__breakingToysIndexes = None
        self.__isBreakingToysFromSlot = False
        self.__slots = None
        self.__cny = None
        self.__em = Event.EventManager()
        self.onSlotUpdated = Event.Event(self.__em)
        self.onInventoryUpdated = Event.Event(self.__em)
        self.onProgressChanged = Event.Event(self.__em)
        self.onToyFragmentsChanged = Event.Event(self.__em)
        self.onToyCollectionChanged = Event.Event(self.__em)
        self.onCraftedToysChanged = Event.Event(self.__em)
        self.onToysBreak = Event.Event(self.__em)
        self.onToysBreakFailed = Event.Event(self.__em)
        self.onToysBreakStarted = Event.Event(self.__em)
        self.onStateChanged = Event.Event(self.__em)
        self.__isEnabled = False
        self.__isAvailable = False
        self.__state = None
        self.__craftedToys = []
        self.__boxStorage = _NewYearBoxStorage()
        self.__chestStorage = _NewYearChestStorage()
        self.__vehDiscountsStorage = _VehicleDiscountsStorage()
        self.__tankmanDiscountsStorage = _TankmanDiscountsStorage()
        self.__stateHandler = _StateHandler()
        self.__sysMsgsHandler = _SysMsgsHandler()
        self.__requestCtrl = None
        return

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def isEnabled(self):
        return self.__isEnabled

    def isAvailable(self):
        return self.__isAvailable

    @property
    def boxStorage(self):
        return self.__boxStorage

    @property
    def chestStorage(self):
        return self.__chestStorage

    @property
    def vehDiscountsStorage(self):
        return self.__vehDiscountsStorage

    @property
    def tankmanDiscountsStorage(self):
        return self.__tankmanDiscountsStorage

    @property
    def stateHandler(self):
        return self.__stateHandler

    @property
    def craftedToys(self):
        return self.__craftedToys

    @property
    def toysDescrs(self):
        return self.__toysCache

    @property
    def slotsDescrs(self):
        return new_year_types.g_cache.slots

    @property
    def collectionRewardsBySettingID(self):
        return new_year_types.g_cache.collectionRewardsBySettingID

    @property
    def receivedToysCollection(self):
        return self.__cny.toyCollection

    @property
    def maxLevel(self):
        return new_year_types.MAX_CHEST_LEVEL

    @property
    def state(self):
        return self.__state

    @property
    def toysDataDict(self):
        """
        just proxy ClientNewYear toys data
        :return: { toyID : ToyInventoryData }
        """
        return self.__cny.inventoryToys

    @property
    def slots(self):
        return self.__slots

    @staticmethod
    def getSettingIndexInNationsOrder(setting):
        for index, nation in enumerate(GUI_SETTINGS.nations_order):
            if SETTING_BY_NATION[nation] == setting:
                return index

    def init(self):
        self.__buildCache()

    def fini(self):
        self.__clear()
        self.__clearHandlers()
        self.__boxStorage.fini()
        self.__sysMsgsHandler.fini()
        self.__chestStorage.fini()
        self.__vehDiscountsStorage.fini()
        self.__tankmanDiscountsStorage.fini()

    def onLobbyInited(self, event):
        self.__stateHandler.onLobbyInited()
        self.__stateHandler.update(self.__state, self.getVariadicDiscounts(), self)

    def onLobbyStarted(self, ctx):
        self.__inventoryToys = {k:{} for k in TOY_TYPES}
        self.__slots = [_EmptySlot(None)] * len(self.slotsDescrs)
        self.__cny = BigWorld.player().newYear
        if self.__cny:
            self.__cny.onStateChanged += self._updateState
            self.__cny.onInventoryChanged += self.__onInventoryChanged
            self.__cny.onSlotsChanged += self.__onSlotsChanged
            self.__cny.onLevelChanged += self.__onLevelChanged
            self.__cny.onToyFragmentsChanged += self.__onToyFragmentsChanged
            self.__cny.onToyCollectionChanged += self.__onToyCollectionChanged
            self.__requestCtrl = NYRequestController(self)
            self.__sysMsgsHandler.init(self)
            self.__boxStorage.init(self, self.__requestCtrl)
            self.__chestStorage.init(self, self.__requestCtrl)
            self.__vehDiscountsStorage.init(self, self.__requestCtrl)
            self.__tankmanDiscountsStorage.init(self, self.__requestCtrl)
            self.__updateData()
            self._updateState(self.__cny.state)
            from gui.shared.utils.HangarSpace import g_hangarSpace
            g_hangarSpace.onSpaceRefreshed += self.__updateData
        else:
            self._updateState(NY_STATE.NOT_STARTED)
        return

    def onDisconnected(self):
        self.__stateHandler.onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def getToysForSlot(self, slotID):
        if not 0 <= slotID <= len(self.slotsDescrs):
            LOG_ERROR('[NEW YEAR] There is no type information for slot with id = {}'.format(slotID))
            return {}
        slotType = self.slotsDescrs[slotID].type
        return self.__inventoryToys[slotType].values()

    def getPlacedToy(self, slotID):
        assert 0 <= slotID <= len(self.slotsDescrs)
        return ToyItemInfo(self.__slots[slotID])

    def getPlacedToys(self, slotIDs):
        return {i:v for i, v in enumerate(self.__slots) if i in slotIDs}

    def getProgress(self):
        return _NewYearProgress(self.__cny.atmosphereLevel, self.__cny.level, *self.__cny.progress)

    def getToyFragments(self):
        return self.__cny.toyFragments

    def getInventory(self):
        return self.__inventoryToys

    def getPriceForCraft(self, toyType, toyNation, toyLevel):
        return calculateCraftCost(toyType is not None, toyNation is not None, toyLevel)

    def getFragmentsForToy(self, toyID):
        toyDescr = new_year_types.g_cache.toys.get(toyID, None)
        fragments = 0 if toyDescr is None else toyDescr.fragments
        return fragments

    def getBonusesForNation(self, nationID):
        return self.__cny.getBonusesForNation(nationID)

    def getBonusesForSetting(self, settingID):
        return self.__cny.getBonusesForSetting(settingID)

    def getSettingForNation(self, nationID):
        return self.__cny.getSettingForNation(nationID)

    def getCollectionLevelForNation(self, nationID):
        return self.__cny.getCollectionLevelForNation(nationID)

    def getCollectionRatingForNation(self, nationID):
        return self.__cny.getCollectionRatingForNation(nationID)

    def getVariadicDiscounts(self):
        return dict(self.vehDiscountsStorage.getDiscounts(), **self.tankmanDiscountsStorage.getDiscounts())

    def calculateBonusesForCollectionLevel(self, collectionLevel):
        return self.__cny.calculateBonusesForCollectionLevel(collectionLevel)

    def clearCraftedToys(self):
        self.__craftedToys = []

    def craftToy(self, toyType, toyNation, toyLevel):
        self.__sendRequest(ny_contexts.CraftToyContext(toyType, toyNation, toyLevel), self.__onCraftCallback)

    def breakToys(self, toys, toyIndexes=None, fromSlot=False):
        self.__breakingToysIndexes = toyIndexes
        self.__isBreakingToysFromSlot = fromSlot
        r = self.__sendRequest(ny_contexts.BreakToyContext(toys), self.__onBreakToysCallback)
        if r:
            self.onToysBreakStarted()
        return r

    def placeToy(self, toyID, slotID):
        return self.__sendRequest(ny_contexts.PlaceToyContext(toyID, slotID), lambda callback: None)

    def markToysAsSeen(self, toys):
        self.__cny.markToysAsSeen(toys)

    def __sendRequest(self, ctx, callback):
        """
        Sends request to the server
        :param ctx:
        :return: bool, True if all checkings are passed and request sent to server, otherwise False
        """
        return self.__requestCtrl.request(ctx, callback)

    def __onBreakToysCallback(self, response):
        if response.isSuccess():
            self.onToysBreak(self.__breakingToysIndexes, self.__isBreakingToysFromSlot)
        else:
            self.onToysBreakFailed()
        self.__breakingToysIndexes = None
        self.__isBreakingToysFromSlot = False
        return

    def __onCraftCallback(self, response):
        if response.isSuccess():
            toyId = response.data
            self.__craftedToys.append(toyId)
            self.onCraftedToysChanged(toyId)

    def __clearHandlers(self):
        if self.__cny is not None:
            self.__cny.onInventoryChanged -= self.__onInventoryChanged
            self.__cny.onSlotsChanged -= self.__onSlotsChanged
            self.__cny.onLevelChanged -= self.__onLevelChanged
            self.__cny.onToyFragmentsChanged -= self.__onToyFragmentsChanged
            self.__cny.onToyCollectionChanged -= self.__onToyCollectionChanged
        return

    def __buildCache(self):
        self.__toysCache = new_year_types.g_cache.toys

    def __updateData(self):
        assert self.__cny
        self.__inventoryToys = {k:{} for k in TOY_TYPES}
        self.__slots = [_EmptySlot(None)] * len(self.slotsDescrs)
        self.__onSlotsChanged()
        self.__onInventoryChanged()
        self.__onLevelChanged()
        self.__onToyFragmentsChanged()
        return

    def _updateState(self, state):
        assert state in NY_STATE.ALL
        prevState = self.__state
        if self.__state != state:
            self.__state = state
            self.__stateHandler.update(state, self.getVariadicDiscounts(), self)
            isEnabled = state in NY_STATE.ENABLED
            if self.__isEnabled != isEnabled:
                self.__isEnabled = isEnabled
                LOG_DEBUG('NY Controller state changed, isEnabled={}'.format(isEnabled))
            isAvailable = state == NY_STATE.IN_PROGRESS
            isNotInitialized = prevState is None
            if self.__isAvailable != isAvailable or isNotInitialized:
                LOG_DEBUG('NY Controller availability changed, isAvailable={}'.format(isAvailable))
                self.__isAvailable = isAvailable
                if not isAvailable:
                    if self.__state == NY_STATE.SUSPENDED:
                        SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_STATE_ERROR_NOTAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
                    self.__switchHangar(True)
                else:
                    if prevState == NY_STATE.SUSPENDED:
                        SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_STATE_RESTORED, type=SystemMessages.SM_TYPE.Warning)
                    self.__switchHangar(False)
            self.onStateChanged(state)
        return

    def __onInventoryChanged(self, toys=None):
        if not toys:
            toys = self.__cny.inventoryToys
            self.__inventoryToys = {k:{} for k in TOY_TYPES}
        for id, data in toys.iteritems():
            count = data.totalCount
            newCount = data.newCount
            toyDescr = self.__toysCache[id]
            typedToys = self.__inventoryToys[toyDescr.type]
            if count == 0:
                typedToys.pop(id, None)
            toy = typedToys.setdefault(id, ToyItemInfo(toyDescr))
            toy.count = count
            toy.newCount = newCount

        self.onInventoryUpdated()
        return

    def __onSlotsChanged(self, slots=None):
        if not slots:
            slots = self.__cny.slots
        for slotID, toyID in enumerate(slots):
            if toyID != self.__slots[slotID].id:
                self.__slots[slotID] = self.__toysCache[toyID] if toyID in self.__toysCache else self.__es
                self.onSlotUpdated(self.slotsDescrs[slotID], self.__slots[slotID])

        self.onProgressChanged(self.getProgress())

    def __onToyFragmentsChanged(self, fragmentsCount=None):
        if fragmentsCount is None:
            fragmentsCount = self.__cny.toyFragments
        self.onToyFragmentsChanged(fragmentsCount)
        return

    def __onToyCollectionChanged(self, diff):
        self.onToyCollectionChanged(diff)

    def __onLevelChanged(self, level=None, progress=None, bound=None):
        nyProgress = _NewYearProgress(level, level, progress, bound) if level is not None else self.getProgress()
        self.onProgressChanged(nyProgress)
        return

    def __clear(self):
        if self.__requestCtrl:
            self.__requestCtrl.fini()
            self.__requestCtrl = None
        self.__stateHandler.clear()
        self.__state = None
        self.__craftedToys = []
        self.__isEnabled = False
        self.__isAvailable = False
        if self.__cny:
            self.__cny.onStateChanged -= self._updateState
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.onSpaceRefreshed -= self.__updateData
        self.__boxStorage.clear()
        self.__sysMsgsHandler.clear()
        self.__chestStorage.clear()
        self.__vehDiscountsStorage.clear()
        self.__tankmanDiscountsStorage.clear()
        return

    def __switchHangar(self, defaultHangar):
        pass
