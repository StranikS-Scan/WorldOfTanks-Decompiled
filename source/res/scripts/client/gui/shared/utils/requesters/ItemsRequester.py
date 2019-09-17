# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/ItemsRequester.py
from abc import ABCMeta, abstractmethod
from collections import defaultdict
import operator
import constants
import dossiers2
import nations
from account_shared import LayoutIterator
from adisp import async, process
from constants import CustomizationInvData, SkinInvData
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR
from goodies.goodie_constants import GOODIE_STATE
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES, ItemsCollection, getVehicleSuitablesByType
from gui.shared.utils.requesters import vehicle_items_getter
from gui.shared.gui_items.customization.outfit import Outfit
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers import dependency
from items import vehicles, tankmen, getTypeOfCompactDescr, makeIntCompactDescrByID
from items.components.c11n_constants import SeasonType, StyleFlags
from items.components.crew_skins_constants import CrewSkinType
from skeletons.gui.shared import IItemsRequester
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS

def _getDiffID(itemdID):
    if isinstance(itemdID, tuple):
        itemdID, _ = itemdID
    return itemdID


class _CriteriaCondition(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, item):
        pass


class PredicateCondition(_CriteriaCondition):

    def lookInInventory(self):
        return False

    def getIntCDProtector(self):
        return None

    def __init__(self, predicate):
        self.predicate = predicate

    def __call__(self, item):
        return self.predicate(item)


class InventoryPredicateCondition(PredicateCondition):

    def lookInInventory(self):
        return True


class CompoundPredicateCondition(PredicateCondition):

    def __init__(self, *predicates):
        self.predicates = predicates

    def lookInInventory(self):
        for predicate in self.predicates:
            if not predicate.lookInInventory():
                return False

        return True

    def __call__(self, item):
        for predicate in self.predicates:
            if not predicate(item):
                return False

        return True


class NegativeCompoundPredicateCondition(CompoundPredicateCondition):

    def __call__(self, item):
        for predicate in self.predicates:
            if not predicate(item):
                return True

        return False

    def lookInInventory(self):
        for predicate in self.predicates:
            if predicate.lookInInventory():
                return False

        return super(NegativeCompoundPredicateCondition, self).lookInInventory()


class OrCompoundPredicateCondition(CompoundPredicateCondition):

    def __call__(self, item):
        for predicate in self.predicates:
            if predicate(item):
                return True

        return not self.predicates

    def lookInInventory(self):
        for predicate in self.predicates:
            if not predicate.lookInInventory():
                return False

        return self.predicates


class IntCDProtector(object):
    __slots__ = ('__intCDs',)

    def __init__(self, *intCDs):
        super(IntCDProtector, self).__init__()
        self.__intCDs = intCDs

    def isUnlinked(self):
        return not self.__intCDs

    def isTriggered(self, intCD):
        return intCD not in self.__intCDs


class RequestCriteria(object):

    def __init__(self, *args):
        self._conditions = args
        self._protector = None
        return

    def __call__(self, item):
        for c in self._conditions:
            if not c(item):
                return False

        return True

    def __or__(self, other):
        return RequestCriteria(*(self._conditions + other.getConditions()))

    def __invert__(self):
        return RequestCriteria(NegativeCompoundPredicateCondition(*self._conditions))

    def __xor__(self, other):
        selfConditions = CompoundPredicateCondition(*self._conditions)
        otherConditions = CompoundPredicateCondition(*other.getConditions())
        return RequestCriteria(OrCompoundPredicateCondition(selfConditions, otherConditions))

    def getConditions(self):
        return self._conditions

    def getIntCDProtector(self):
        return self._protector

    def lookInInventory(self):
        for condition in self._conditions:
            if condition.lookInInventory():
                return True

        return False

    @property
    def conditions(self):
        return self._conditions


class IntCDProtectionRequestCriteria(RequestCriteria):

    def __init__(self, condition, intCDs):
        super(IntCDProtectionRequestCriteria, self).__init__(PredicateCondition(condition))
        self._protector = IntCDProtector(*intCDs)


class VehsSuitableCriteria(RequestCriteria):

    def __init__(self, vehsItems, itemTypeIDs=None):
        itemTypeIDs = itemTypeIDs or GUI_ITEM_TYPE.VEHICLE_MODULES
        suitableCompDescrs = set()
        for vehicle in vehsItems:
            for itemTypeID in itemTypeIDs:
                for descr in getVehicleSuitablesByType(vehicle.descriptor, itemTypeID)[0]:
                    suitableCompDescrs.add(descr.compactDescr)

        super(VehsSuitableCriteria, self).__init__(PredicateCondition(lambda item: item.intCD in suitableCompDescrs))


class REQ_CRITERIA(object):
    EMPTY = RequestCriteria()
    CUSTOM = staticmethod(lambda predicate: RequestCriteria(PredicateCondition(predicate)))
    HIDDEN = RequestCriteria(PredicateCondition(operator.attrgetter('isHidden')))
    SECRET = RequestCriteria(PredicateCondition(operator.attrgetter('isSecret')))
    DISCLOSABLE = RequestCriteria(PredicateCondition(lambda item: item.inventoryCount > 0 or not item.isSecret))
    UNLOCKED = RequestCriteria(PredicateCondition(operator.attrgetter('isUnlocked')))
    REMOVABLE = RequestCriteria(PredicateCondition(operator.attrgetter('isRemovable')))
    INVENTORY = RequestCriteria(InventoryPredicateCondition(lambda item: item.inventoryCount > 0))
    NATIONS = staticmethod(lambda nationIDs=nations.INDICES.keys(): RequestCriteria(PredicateCondition(lambda item: item.nationID in nationIDs)))
    INNATION_IDS = staticmethod(lambda innationIDs: RequestCriteria(PredicateCondition(lambda item: item.innationID in innationIDs)))
    ITEM_TYPES = staticmethod(lambda *args: RequestCriteria(PredicateCondition(lambda item: item.itemTypeID in args)))
    ITEM_TYPES_NAMES = staticmethod(lambda *args: RequestCriteria(PredicateCondition(lambda item: item.itemTypeName in args)))
    IN_CD_LIST = staticmethod(lambda itemsList: RequestCriteria(PredicateCondition(lambda item: item.intCD in itemsList)))
    INVENTORY_OR_UNLOCKED = RequestCriteria(InventoryPredicateCondition(lambda item: item.inventoryCount > 0 or item.isUnlocked and not item.isInitiallyUnlocked))
    DISCOUNT_BUY = RequestCriteria(PredicateCondition(lambda item: item.buyPrices.itemPrice.isActionPrice() and not item.isRestoreAvailable()))
    DISCOUNT_SELL = RequestCriteria(PredicateCondition(lambda item: not item.isRented and item.sellPrices.itemPrice.isActionPrice()))
    IN_OWNERSHIP = RequestCriteria(PredicateCondition(lambda item: item.inventoryCount > 0 and not item.isRented))
    TYPE_CRITERIA = staticmethod(lambda itemsTypeID, condition: RequestCriteria(PredicateCondition(lambda item: condition(item) if item.itemTypeID in itemsTypeID else True)))

    class VEHICLE(object):
        FAVORITE = RequestCriteria(PredicateCondition(lambda item: item.isFavorite))
        PREMIUM = RequestCriteria(PredicateCondition(lambda item: item.isPremium))
        READY = RequestCriteria(PredicateCondition(lambda item: item.isReadyToFight))
        OBSERVER = RequestCriteria(PredicateCondition(lambda item: item.isObserver))
        LOCKED = RequestCriteria(PredicateCondition(lambda item: item.isLocked))
        CLASSES = staticmethod(lambda types=constants.VEHICLE_CLASS_INDICES.keys(): RequestCriteria(PredicateCondition(lambda item: item.type in types)))
        LEVELS = staticmethod(lambda levels=range(1, constants.MAX_VEHICLE_LEVEL + 1): RequestCriteria(PredicateCondition(lambda item: item.level in levels)))
        LEVEL = staticmethod(lambda level=1: RequestCriteria(PredicateCondition(lambda item: item.level == level)))
        SPECIFIC_BY_CD = staticmethod(lambda typeCompDescrs: RequestCriteria(PredicateCondition(lambda item: item.intCD in typeCompDescrs)))
        SPECIFIC_BY_NAME = staticmethod(lambda typeNames: RequestCriteria(PredicateCondition(lambda item: item.name in typeNames)))
        SPECIFIC_BY_INV_ID = staticmethod(lambda invIDs: RequestCriteria(PredicateCondition(lambda item: item.invID in invIDs)))
        SUITABLE = staticmethod(lambda vehsItems, itemTypeIDs=None: VehsSuitableCriteria(vehsItems, itemTypeIDs))
        RENT = RequestCriteria(PredicateCondition(lambda item: item.isRented))
        TELECOM = RequestCriteria(PredicateCondition(lambda item: item.isTelecom))
        ACTIVE_RENT = RequestCriteria(InventoryPredicateCondition(lambda item: item.isRented and not item.rentalIsOver))
        EXPIRED_RENT = RequestCriteria(PredicateCondition(lambda item: item.isRented and item.rentalIsOver))
        EXPIRED_IGR_RENT = RequestCriteria(PredicateCondition(lambda item: item.isRented and item.rentalIsOver and item.isPremiumIGR))
        RENT_PROMOTION = RequestCriteria(PredicateCondition(lambda item: item.isRentPromotion))
        SEASON_RENT = RequestCriteria(PredicateCondition(lambda item: item.isSeasonRent))
        DISABLED_IN_PREM_IGR = RequestCriteria(PredicateCondition(lambda item: item.isDisabledInPremIGR))
        IS_PREMIUM_IGR = RequestCriteria(PredicateCondition(lambda item: item.isPremiumIGR))
        ELITE = RequestCriteria(PredicateCondition(lambda item: item.isElite))
        IS_BOT = RequestCriteria(PredicateCondition(lambda item: item.name.endswith('_bot')))
        FULLY_ELITE = RequestCriteria(PredicateCondition(lambda item: item.isFullyElite))
        EVENT = RequestCriteria(PredicateCondition(lambda item: item.isEvent))
        EVENT_BATTLE = RequestCriteria(PredicateCondition(lambda item: item.isOnlyForEventBattles))
        EPIC_BATTLE = RequestCriteria(PredicateCondition(lambda item: item.isOnlyForEpicBattles))
        HAS_XP_FACTOR = RequestCriteria(PredicateCondition(lambda item: item.dailyXPFactor != -1))
        IS_RESTORE_POSSIBLE = RequestCriteria(PredicateCondition(lambda item: item.isRestorePossible()))
        CAN_TRADE_IN = RequestCriteria(PredicateCondition(lambda item: item.canTradeIn))
        CAN_TRADE_OFF = RequestCriteria(PredicateCondition(lambda item: item.canTradeOff))
        CAN_SELL = RequestCriteria(PredicateCondition(lambda item: item.canSell))
        CAN_NOT_BE_SOLD = RequestCriteria(PredicateCondition(lambda item: item.canNotBeSold))
        SECRET = RequestCriteria(PredicateCondition(lambda item: item.isSecret))
        IS_IN_BATTLE = RequestCriteria(PredicateCondition(lambda item: item.isInBattle))
        NAME_VEHICLE = staticmethod(lambda nameVehicle: RequestCriteria(PredicateCondition(lambda item: nameVehicle in item.searchableUserName)))
        NAME_VEHICLE_WITH_SHORT = staticmethod(lambda nameVehicle: RequestCriteria(PredicateCondition(lambda item: nameVehicle in item.searchableShortUserName or nameVehicle in item.searchableUserName)))
        DISCOUNT_RENT_OR_BUY = RequestCriteria(PredicateCondition(lambda item: (item.buyPrices.itemPrice.isActionPrice() or item.getRentPackageActionPrc() != 0) and not item.isRestoreAvailable()))
        HAS_TAGS = staticmethod(lambda tags: RequestCriteria(PredicateCondition(lambda item: item.tags.issuperset(tags))))

    class TANKMAN(object):
        IN_TANK = RequestCriteria(PredicateCondition(lambda item: item.isInTank))
        ROLES = staticmethod(lambda roles=tankmen.ROLES: RequestCriteria(PredicateCondition(lambda item: item.descriptor.role in roles)))
        NATIVE_TANKS = staticmethod(lambda vehiclesList=[]: RequestCriteria(PredicateCondition(lambda item: item.vehicleNativeDescr.type.compactDescr in vehiclesList)))
        DISMISSED = RequestCriteria(PredicateCondition(lambda item: item.isDismissed))
        NOT_IN_EVENT_TANKS = RequestCriteria(PredicateCondition(lambda item: VEHICLE_TAGS.EVENT not in item.vehicleNativeDescr.type.tags))
        ACTIVE = ~DISMISSED

    class CREW_ITEM(object):
        IN_ACCOUNT = RequestCriteria(PredicateCondition(lambda item: item.inAccount()))
        BOOK_RARITIES = staticmethod(lambda rarityTypes: RequestCriteria(PredicateCondition(lambda item: item.getBookType() in rarityTypes)))
        NATIONS = staticmethod(lambda nationIDs=nations.INDICES.keys(): RequestCriteria(PredicateCondition(lambda item: item.nationID in nationIDs or item.getNationID() == nations.NONE_INDEX)))

    class BOOSTER(object):
        ENABLED = RequestCriteria(PredicateCondition(lambda item: item.enabled))
        IN_ACCOUNT = RequestCriteria(InventoryPredicateCondition(lambda item: item.count > 0))
        ACTIVE = RequestCriteria(PredicateCondition(lambda item: item.finishTime is not None and item.state == GOODIE_STATE.ACTIVE))
        IS_READY_TO_ACTIVATE = RequestCriteria(PredicateCondition(lambda item: item.isReadyToActivate))
        BOOSTER_TYPES = staticmethod(lambda boosterTypes: RequestCriteria(PredicateCondition(lambda item: item.boosterType in boosterTypes)))
        IN_BOOSTER_ID_LIST = staticmethod(lambda boostersList: RequestCriteria(PredicateCondition(lambda item: item.boosterID in boostersList)))
        QUALITY = staticmethod(lambda qualityValues: RequestCriteria(PredicateCondition(lambda item: item.quality in qualityValues)))
        DURATION = staticmethod(lambda durationTimes: RequestCriteria(PredicateCondition(lambda item: item.effectTime in durationTimes)))

    class EQUIPMENT(object):
        BUILTIN = staticmethod(RequestCriteria(PredicateCondition(lambda item: item.isBuiltIn)))

    class BATTLE_BOOSTER(object):
        ALL = RequestCriteria(PredicateCondition(lambda item: item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER))
        CREW_EFFECT = RequestCriteria(PredicateCondition(lambda item: item.isCrewBooster()))
        OPTIONAL_DEVICE_EFFECT = RequestCriteria(PredicateCondition(lambda item: not item.isCrewBooster()))

    class SHELL(object):
        TYPE = staticmethod(lambda typesList: RequestCriteria(PredicateCondition(lambda item: item.type in typesList)))

    class ARTEFACT(object):
        DESCRIPTOR_NAME = staticmethod(lambda descriptorName: RequestCriteria(PredicateCondition(lambda item: item.name == descriptorName)))

    class OPTIONAL_DEVICE(object):
        SIMPLE = RequestCriteria(PredicateCondition(lambda item: not item.isDeluxe()))
        DELUXE = RequestCriteria(PredicateCondition(lambda item: item.isDeluxe()))

    class BADGE(object):
        SELECTED = RequestCriteria(PredicateCondition(lambda item: item.isSelected))
        PREFIX_LAYOUT = RequestCriteria(PredicateCondition(lambda item: item.isPrefixLayout()))
        ACHIEVED = RequestCriteria(PredicateCondition(lambda item: item.isAchieved))

    class CUSTOMIZATION(object):
        SUMMER = RequestCriteria(PredicateCondition(lambda item: item.isSummer()))
        WINTER = RequestCriteria(PredicateCondition(lambda item: item.isWinter()))
        DESERT = RequestCriteria(PredicateCondition(lambda item: item.isDesert()))
        ALL_SEASON = RequestCriteria(PredicateCondition(lambda item: item.isAllSeason()))
        SEASON = staticmethod(lambda season: RequestCriteria(PredicateCondition(lambda item: item.season & season)))
        HISTORICAL = RequestCriteria(PredicateCondition(lambda item: item.isHistorical()))
        FOR_VEHICLE = staticmethod(lambda vehicle: RequestCriteria(PredicateCondition(lambda item: item.mayInstall(vehicle))))
        UNLOCKED_BY = staticmethod(lambda token: RequestCriteria(PredicateCondition(lambda item: item.requiredToken == token)))
        IS_UNLOCKED = staticmethod(lambda progress: RequestCriteria(PredicateCondition(lambda item: not item.requiredToken or item.requiredToken and progress.getTokenCount(item.requiredToken) > 0)))
        PRICE_GROUP = staticmethod(lambda priceGroup: RequestCriteria(PredicateCondition(lambda item: item.priceGroup == priceGroup)))
        PRICE_GROUP_TAG = staticmethod(lambda tag: RequestCriteria(PredicateCondition(lambda item: tag in item.priceGroupTags)))
        FREE_OR_IN_INVENTORY = RequestCriteria(PredicateCondition(lambda item: item.isInInventory or item.getBuyPrice() == ITEM_PRICE_EMPTY))
        ONLY_IN_GROUP = staticmethod(lambda group: RequestCriteria(PredicateCondition(lambda item: item.groupUserName == group)))
        DISCLOSABLE = staticmethod(lambda vehicle: RequestCriteria(PredicateCondition(lambda item: item.fullInventoryCount(vehicle) or not item.isHidden)))
        IS_INSTALLED_ON_VEHICLE = staticmethod(lambda vehicle: RequestCriteria(PredicateCondition(lambda item: item.getInstalledOnVehicleCount(vehicle.intCD) > 0)))
        HAS_TAGS = staticmethod(lambda tags: RequestCriteria(PredicateCondition(lambda item: item.tags.issuperset(tags))))


class RESEARCH_CRITERIA(object):
    VEHICLE_TO_UNLOCK = ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.VEHICLE.PREMIUM | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR | ~REQ_CRITERIA.VEHICLE.EVENT


class ItemsRequester(IItemsRequester):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, inventory, stats, dossiers, goodies, shop, recycleBin, vehicleRotation, ranked, badges, epicMetaGame, tokens, festivityRequester, blueprints=None, sessionStatsRequester=None):
        self.__inventory = inventory
        self.__stats = stats
        self.__dossiers = dossiers
        self.__goodies = goodies
        self.__shop = shop
        self.__vehicleRotation = vehicleRotation
        self.__recycleBin = recycleBin
        self.__ranked = ranked
        self.__badges = badges
        self.__epicMetaGame = epicMetaGame
        self.__blueprints = blueprints
        self.__festivity = festivityRequester
        self.__tokens = tokens
        self.__sessionStats = sessionStatsRequester
        self.__itemsCache = defaultdict(dict)
        self.__brokenSyncAlreadyLoggedTypes = set()
        self.__vehCustomStateCache = defaultdict(dict)

    @property
    def inventory(self):
        return self.__inventory

    @property
    def stats(self):
        return self.__stats

    @property
    def dossiers(self):
        return self.__dossiers

    @property
    def goodies(self):
        return self.__goodies

    @property
    def shop(self):
        return self.__shop

    @property
    def recycleBin(self):
        return self.__recycleBin

    @property
    def vehicleRotation(self):
        return self.__vehicleRotation

    @property
    def ranked(self):
        return self.__ranked

    @property
    def badges(self):
        return self.__badges

    @property
    def epicMetaGame(self):
        return self.__epicMetaGame

    @property
    def blueprints(self):
        return self.__blueprints

    @property
    def festivity(self):
        return self.__festivity

    @property
    def tokens(self):
        return self.__tokens

    @property
    def sessionStats(self):
        return self.__sessionStats

    @async
    @process
    def request(self, callback=None):
        from gui.Scaleform.Waiting import Waiting
        Waiting.show('download/inventory')
        yield self.__stats.request()
        yield self.__inventory.request()
        yield self.__vehicleRotation.request()
        Waiting.hide('download/inventory')
        Waiting.show('download/shop')
        yield self.__shop.request()
        Waiting.hide('download/shop')
        Waiting.show('download/dossier')
        yield self.__dossiers.request()
        yield self.__sessionStats.request()
        Waiting.hide('download/dossier')
        Waiting.show('download/discounts')
        yield self.__goodies.request()
        Waiting.hide('download/discounts')
        Waiting.show('download/recycleBin')
        yield self.__recycleBin.request()
        Waiting.hide('download/recycleBin')
        Waiting.show('download/ranked')
        yield self.__ranked.request()
        Waiting.hide('download/ranked')
        Waiting.show('download/badges')
        yield self.__badges.request()
        Waiting.hide('download/badges')
        Waiting.show('download/epicMetaGame')
        yield self.epicMetaGame.request()
        Waiting.hide('download/epicMetaGame')
        Waiting.show('download/blueprints')
        yield self.__blueprints.request()
        Waiting.hide('download/blueprints')
        Waiting.show('download/tokens')
        yield self.__tokens.request()
        Waiting.hide('download/tokens')
        Waiting.show('download/festivity')
        yield self.__festivity.request()
        Waiting.hide('download/festivity')
        self.__brokenSyncAlreadyLoggedTypes.clear()
        callback(self)

    def isSynced(self):
        return self.__stats.isSynced() and self.__inventory.isSynced() and self.__recycleBin.isSynced() and self.__shop.isSynced() and self.__dossiers.isSynced() and self.__goodies.isSynced() and self.__vehicleRotation.isSynced() and self.ranked.isSynced() and self.epicMetaGame.isSynced() and self.__blueprints.isSynced() if self.__blueprints is not None else False

    @async
    @process
    def requestUserDossier(self, databaseID, callback):
        dr = self.__dossiers.getUserDossierRequester(databaseID)
        userAccDossier = yield dr.getAccountDossier()
        clanInfo = yield dr.getClanInfo()
        seasons = yield dr.getRated7x7Seasons()
        ranked = yield dr.getRankedInfo()
        festival = yield dr.getFestivalInfo()
        container = self.__itemsCache[GUI_ITEM_TYPE.ACCOUNT_DOSSIER]
        container[databaseID] = (userAccDossier,
         clanInfo,
         seasons,
         ranked,
         festival)
        callback((userAccDossier, clanInfo, dr.isHidden))

    def unloadUserDossier(self, databaseID):
        container = self.__itemsCache[GUI_ITEM_TYPE.ACCOUNT_DOSSIER]
        if databaseID in container:
            del container[databaseID]
            self.__dossiers.closeUserDossier(databaseID)

    @async
    @process
    def requestUserVehicleDossier(self, databaseID, vehTypeCompDescr, callback):
        dr = self.__dossiers.getUserDossierRequester(databaseID)
        userVehDossier = yield dr.getVehicleDossier(vehTypeCompDescr)
        container = self.__itemsCache[GUI_ITEM_TYPE.VEHICLE_DOSSIER]
        container[databaseID, vehTypeCompDescr] = userVehDossier
        callback(userVehDossier)

    def clear(self):
        while self.__itemsCache:
            _, cache = self.__itemsCache.popitem()
            cache.clear()

        self.__vehCustomStateCache.clear()
        self.__inventory.clear()
        self.__shop.clear()
        self.__stats.clear()
        self.__dossiers.clear()
        self.__goodies.clear()
        self.__vehicleRotation.clear()
        self.__recycleBin.clear()
        self.__ranked.clear()
        self.__badges.clear()
        self.__tokens.clear()
        self.epicMetaGame.clear()
        self.__blueprints.clear()
        self.__festivity.clear()

    def invalidateCache(self, diff=None):
        invalidate = defaultdict(set)
        if diff is None:
            LOG_DEBUG('Gui items cache full invalidation')
            for itemTypeID, cache in self.__itemsCache.iteritems():
                if itemTypeID not in (GUI_ITEM_TYPE.ACCOUNT_DOSSIER, GUI_ITEM_TYPE.VEHICLE_DOSSIER, GUI_ITEM_TYPE.BATTLE_ABILITY):
                    cache.clear()

        else:
            for statName, data in diff.get('stats', {}).iteritems():
                if statName in ('unlocks', ('unlocks', '_r')):
                    self._invalidateUnlocks(data, invalidate)
                if statName == 'eliteVehicles':
                    invalidate[GUI_ITEM_TYPE.VEHICLE].update(data)
                if statName in ('vehTypeXP', 'vehTypeLocks'):
                    invalidate[GUI_ITEM_TYPE.VEHICLE].update(data.keys())
                if statName in (('multipliedXPVehs', '_r'), ('multipliedRankedBattlesVehs', '_r')):
                    getter = vehicles.getVehicleTypeCompactDescr
                    inventoryVehiclesCDs = [ getter(v['compDescr']) for v in self.__inventory.getItems(GUI_ITEM_TYPE.VEHICLE).itervalues() ]
                    invalidate[GUI_ITEM_TYPE.VEHICLE].update(inventoryVehiclesCDs)
                if statName in ('oldVehInvIDs',):
                    invalidate[GUI_ITEM_TYPE.VEHICLE].update(data)

        for cacheType, data in diff.get('cache', {}).iteritems():
            if cacheType == 'vehsLock':
                for itemID in data.keys():
                    vehData = self.__inventory.getVehicleData(_getDiffID(itemID))
                    if vehData is not None:
                        invalidate[GUI_ITEM_TYPE.VEHICLE].add(vehData.descriptor.type.compactDescr)

        for cacheType, data in diff.get('groupLocks', {}).iteritems():
            if cacheType in ('isGroupLocked', 'groupBattles'):
                getter = vehicles.getVehicleTypeCompactDescr
                inventoryVehiclesCDs = [ getter(v['compDescr']) for v in self.inventory.getItems(GUI_ITEM_TYPE.VEHICLE).itervalues() ]
                invalidate[GUI_ITEM_TYPE.VEHICLE].update(inventoryVehiclesCDs)

        for itemTypeID, itemsDiff in diff.get('inventory', {}).iteritems():
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                if 'compDescr' in itemsDiff:
                    for strCD in itemsDiff['compDescr'].itervalues():
                        if strCD is not None:
                            invalidate[itemTypeID].add(vehicles.getVehicleTypeCompactDescr(strCD))

                for data in itemsDiff.itervalues():
                    for itemID in data.iterkeys():
                        vehData = self.__inventory.getVehicleData(_getDiffID(itemID))
                        if vehData is not None:
                            invalidate[itemTypeID].add(vehData.descriptor.type.compactDescr)
                            invalidate[GUI_ITEM_TYPE.TANKMAN].update(self.__getTankmenIDsForVehicle(vehData))

            if itemTypeID == GUI_ITEM_TYPE.TANKMAN:
                for data in itemsDiff.itervalues():
                    invalidate[itemTypeID].update(data.keys())
                    for itemID in data.keys():
                        tmanInvID = _getDiffID(itemID)
                        tmanData = self.__inventory.getTankmanData(tmanInvID)
                        if tmanData is not None and tmanData.vehicle != -1:
                            invalidate[GUI_ITEM_TYPE.VEHICLE].update(self.__getVehicleCDForTankman(tmanData))
                            invalidate[GUI_ITEM_TYPE.TANKMAN].update(self.__getTankmenIDsForTankman(tmanData))

            if itemTypeID == GUI_ITEM_TYPE.CREW_SKINS:
                for data in itemsDiff.itervalues():
                    invalidate[GUI_ITEM_TYPE.TANKMAN].update(data.keys())

                if SkinInvData.ITEMS in itemsDiff:
                    skinsDiff = itemsDiff[SkinInvData.ITEMS]
                    skinCDs = [ makeIntCompactDescrByID('crewSkin', CrewSkinType.CREW_SKIN, v) for v in skinsDiff.keys() ]
                    invalidate[itemTypeID].update(skinCDs)
                if SkinInvData.OUTFITS in itemsDiff:
                    outfitDiff = itemsDiff[SkinInvData.OUTFITS]
                    for tmanInvID in outfitDiff.keys():
                        tmanData = self.__inventory.getTankmanData(tmanInvID)
                        if tmanData is not None and tmanData.vehicle != constants.VEHICLE_NO_INV_ID:
                            invalidate[GUI_ITEM_TYPE.VEHICLE].update(self.__getVehicleCDForTankman(tmanData))
                            invalidate[GUI_ITEM_TYPE.TANKMAN].update(self.__getTankmenIDsForTankman(tmanData))

            if itemTypeID == GUI_ITEM_TYPE.CREW_BOOKS:
                invalidate[itemTypeID].update(itemsDiff.keys())
            if itemTypeID == GUI_ITEM_TYPE.SHELL:
                invalidate[itemTypeID].update(itemsDiff.keys())
                vehicleItems = self.__inventory.getItems(GUI_ITEM_TYPE.VEHICLE)
                if vehicleItems:
                    for shellIntCD in itemsDiff.iterkeys():
                        for vehicle in vehicleItems.itervalues():
                            shells = vehicle['shells']
                            for intCD, _, _ in LayoutIterator(shells):
                                if shellIntCD == intCD:
                                    vehicleIntCD = vehicles.getVehicleTypeCompactDescr(vehicle['compDescr'])
                                    invalidate[GUI_ITEM_TYPE.VEHICLE].add(vehicleIntCD)
                                    vehicleData = self.__inventory.getItemData(vehicleIntCD)
                                    if vehicleData is not None:
                                        gunIntCD = vehicleData.descriptor.gun.compactDescr
                                        invalidate[GUI_ITEM_TYPE.GUN].add(gunIntCD)

            if itemTypeID == GUI_ITEM_TYPE.CUSTOMIZATION:
                for vehicleIntCD, outfitsData in itemsDiff.get(CustomizationInvData.OUTFITS, {}).iteritems():
                    self._invalidateVehicleOutfits(vehicleIntCD, outfitsData, invalidate)

                for cType, items in itemsDiff.get(CustomizationInvData.ITEMS, {}).iteritems():
                    for idx in items.iterkeys():
                        intCD = vehicles.makeIntCompactDescrByID('customizationItem', cType, _getDiffID(idx))
                        invalidate[GUI_ITEM_TYPE.CUSTOMIZATION].add(intCD)

                for cType, items in itemsDiff.get(CustomizationInvData.NOVELTY_DATA, {}).iteritems():
                    for idx in items.iterkeys():
                        intCD = vehicles.makeIntCompactDescrByID('customizationItem', cType, _getDiffID(idx))
                        invalidate[GUI_ITEM_TYPE.CUSTOMIZATION].add(intCD)

            invalidate[itemTypeID].update(itemsDiff.keys())

        for itemType, itemsDiff in diff.get('recycleBin', {}).iteritems():
            deletedItems = itemsDiff.get('buffer', {})
            for itemID in deletedItems.iterkeys():
                if itemType == 'tankmen':
                    invalidate[GUI_ITEM_TYPE.TANKMAN].add(itemID * -1)
                invalidate[GUI_ITEM_TYPE.VEHICLE].add(itemID)

        if 'goodies' in diff:
            vehicleDiscounts = self.__shop.getVehicleDiscountDescriptions()
            for goodieID in diff['goodies'].iterkeys():
                if goodieID in vehicleDiscounts:
                    vehicleDiscount = vehicleDiscounts[goodieID]
                    invalidate[GUI_ITEM_TYPE.VEHICLE].add(vehicleDiscount.target.targetValue)

        for itemTypeID, uniqueIDs in invalidate.iteritems():
            self._invalidateItems(itemTypeID, uniqueIDs)

        return invalidate

    def getVehicle(self, vehInvID):
        vehInvData = self.__inventory.getVehicleData(vehInvID)
        return self.__makeVehicle(vehInvData.descriptor.type.compactDescr, vehInvData) if vehInvData is not None else None

    def getStockVehicle(self, typeCompDescr, useInventory=False):
        if getTypeOfCompactDescr(typeCompDescr) == GUI_ITEM_TYPE.VEHICLE:
            proxy = self if useInventory else None
            return self.itemsFactory.createVehicle(typeCompDescr=typeCompDescr, proxy=proxy)
        else:
            return

    def getVehicleCopy(self, vehicle):
        return self.itemsFactory.createVehicle(typeCompDescr=vehicle.intCD, strCompactDescr=vehicle.descriptor.makeCompactDescr(), inventoryID=vehicle.invID, proxy=self)

    def getTankman(self, tmanInvID):
        tankman = None
        tmanInvData = self.__inventory.getTankmanData(tmanInvID)
        if tmanInvData is not None:
            tankman = self.__makeTankman(tmanInvID, tmanInvData)
        else:
            duration = self.__shop.tankmenRestoreConfig.billableDuration
            tankmanData = self.__recycleBin.getTankman(tmanInvID, duration)
            if tankmanData is not None:
                tankman = self.__makeDismissedTankman(tmanInvID, tankmanData)
        return tankman

    def getCrewSkin(self, skinID):
        typeCompDescr = vehicles.makeIntCompactDescrByID(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CREW_SKINS], CrewSkinType.CREW_SKIN, skinID)
        return self.__makeSimpleItem(typeCompDescr)

    def getItems(self, itemTypeID=None, criteria=REQ_CRITERIA.EMPTY, nationID=None, onlyWithPrices=True):
        result = ItemsCollection()
        if not isinstance(itemTypeID, tuple):
            itemTypeID = (itemTypeID,)
        for typeID in itemTypeID:
            if typeID == GUI_ITEM_TYPE.VEHICLE and nationID is None and criteria.lookInInventory():
                vehGetter = self.getVehicle
                for vehInvID in (self.inventory.getItems(GUI_ITEM_TYPE.VEHICLE) or {}).iterkeys():
                    item = vehGetter(vehInvID)
                    if criteria(item):
                        result[item.intCD] = item

            itemGetter = self.getItemByCD
            protector = criteria.getIntCDProtector()
            if protector is not None and protector.isUnlinked():
                return result
            for intCD in vehicle_items_getter.getItemsIterator(self.__shop.getItemsData(), nationID=nationID, itemTypeID=typeID, onlyWithPrices=onlyWithPrices):
                if protector is not None and protector.isTriggered(intCD):
                    continue
                item = itemGetter(intCD)
                if criteria(item):
                    result[intCD] = item

        return result

    def getTankmen(self, criteria=REQ_CRITERIA.TANKMAN.ACTIVE):
        result = ItemsCollection()
        activeTankmenInvData = self.__inventory.getItemsData(GUI_ITEM_TYPE.TANKMAN)
        for invID, tankmanInvData in activeTankmenInvData.iteritems():
            item = self.__makeTankman(invID, tankmanInvData)
            if criteria(item):
                result[invID] = item

        duration = self.__shop.tankmenRestoreConfig.billableDuration
        dismissedTankmenData = self.__recycleBin.getTankmen(duration)
        for invID, tankmanData in dismissedTankmenData.iteritems():
            item = self.__makeDismissedTankman(invID, tankmanData)
            if criteria(item):
                result[invID] = item

        return result

    def getVehicles(self, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.VEHICLE, criteria=criteria)

    def getBadges(self, criteria=REQ_CRITERIA.EMPTY):
        result = ItemsCollection()
        for badgeID, badgeData in self.__badges.available.iteritems():
            item = self.itemsFactory.createBadge(badgeData, proxy=self)
            if criteria(item):
                result[badgeID] = item

        return result

    def getBadgeByID(self, badgeID):
        badgeData = self.__badges.available.get(badgeID)
        return None if badgeData is None else self.itemsFactory.createBadge(badgeData, proxy=self)

    def getItemByCD(self, typeCompDescr):
        return self.__makeVehicle(typeCompDescr) if getTypeOfCompactDescr(typeCompDescr) == GUI_ITEM_TYPE.VEHICLE else self.__makeSimpleItem(typeCompDescr)

    def getItem(self, itemTypeID, nationID, innationID):
        typeCompDescr = vehicles.makeIntCompactDescrByID(GUI_ITEM_TYPE_NAMES[itemTypeID], nationID, innationID)
        return self.__makeVehicle(typeCompDescr) if itemTypeID == GUI_ITEM_TYPE.VEHICLE else self.__makeSimpleItem(typeCompDescr)

    def getTankmanDossier(self, tmanInvID):
        tankman = self.getTankman(tmanInvID)
        tmanDossierDescr = self.__getTankmanDossierDescr(tmanInvID)
        currentVehicleItem = None
        if tankman.isInTank:
            extDossier = self.getVehicleDossier(tankman.vehicleDescr.type.compactDescr)
            currentVehicleItem = self.getItemByCD(tankman.vehicleDescr.type.compactDescr)
        else:
            extDossier = self.getAccountDossier()
        return self.itemsFactory.createTankmanDossier(tankman.descriptor, tmanDossierDescr, extDossier, currentVehicleItem=currentVehicleItem)

    def getVehicleDossier(self, vehTypeCompDescr, databaseID=None):
        if databaseID is None:
            return self.itemsFactory.createVehicleDossier(self.__getVehicleDossierDescr(vehTypeCompDescr), vehTypeCompDescr)
        container = self.__itemsCache[GUI_ITEM_TYPE.VEHICLE_DOSSIER]
        dossier = container.get((int(databaseID), vehTypeCompDescr))
        if dossier is None:
            LOG_WARNING('Vehicle dossier for this user is empty', vehTypeCompDescr, databaseID)
            return
        else:
            return self.itemsFactory.createVehicleDossier(dossier, vehTypeCompDescr, playerDBID=databaseID)

    def getVehicleDossiersIterator(self):
        for intCD, dossier in self.__dossiers.getVehDossiersIterator():
            yield (intCD, dossiers2.getVehicleDossierDescr(dossier))

    def getAccountDossier(self, databaseID=None):
        if databaseID is None:
            dossierDescr = self.__getAccountDossierDescr()
            return self.itemsFactory.createAccountDossier(dossierDescr)
        container = self.__itemsCache[GUI_ITEM_TYPE.ACCOUNT_DOSSIER]
        dossier, _, _, _, festival = container.get(int(databaseID))
        if dossier is None:
            LOG_WARNING('Trying to get empty user dossier', databaseID)
            return
        else:
            return self.itemsFactory.createAccountDossier(dossier, databaseID, festivalInfo=festival)

    def getClanInfo(self, databaseID=None):
        if databaseID is None:
            return (self.__stats.clanDBID, self.__stats.clanInfo)
        container = self.__itemsCache[GUI_ITEM_TYPE.ACCOUNT_DOSSIER]
        _, clanInfo, _, _, _ = container.get(int(databaseID))
        if clanInfo is None:
            LOG_WARNING('Trying to get empty user clan info', databaseID)
            return
        else:
            return clanInfo

    def getPreviousItem(self, itemTypeID, invDataIdx):
        itemData = self.__inventory.getPreviousItem(itemTypeID, invDataIdx)
        return self.__makeItem(itemTypeID, invDataIdx, strCompactDescr=itemData.compDescr, inventoryID=itemData.invID, proxy=self)

    def doesVehicleExist(self, intCD):
        itemTypeID, nationID, innationID = vehicles.parseIntCompactDescr(intCD)
        return innationID in vehicles.g_list.getList(nationID)

    def _invalidateItems(self, itemTypeID, uniqueIDs):
        cache = self.__itemsCache[itemTypeID]
        for uid in uniqueIDs:
            invRes = self.__inventory.invalidateItem(itemTypeID, uid)
            if uid in cache:
                LOG_DEBUG('Item marked as invalid', uid, cache[uid], invRes)
                self.__deleteItemFromCache(cache, uid, itemTypeID)
            LOG_DEBUG('No cached item', uid, invRes)

    def _invalidateUnlocks(self, unlocked, result):
        vehInCache = self.__itemsCache[GUI_ITEM_TYPE.VEHICLE]
        for itemCD in unlocked:
            itemTypeID = getTypeOfCompactDescr(itemCD)
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                result[itemTypeID].add(itemCD)
                if itemCD in vehInCache:
                    self._invalidateUnlocks(vehInCache[itemCD].getAutoUnlockedItems(), result)
            if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
                result[itemTypeID].add(itemCD)
            if itemTypeID != GUI_ITEM_TYPE.FUEL_TANK:
                LOG_WARNING('Item is not vehicle or module', itemTypeID)

    def _invalidateVehicleOutfits(self, vehicleIntCD, outfitsData, invalidate):
        invalidate[GUI_ITEM_TYPE.VEHICLE].add(vehicleIntCD)
        vehicle = self.getItemByCD(vehicleIntCD)
        if outfitsData is None:
            invalidItems = self.__removeVehicleOutfits(vehicle)
            invalidate[GUI_ITEM_TYPE.CUSTOMIZATION] |= invalidItems
            invalidate[GUI_ITEM_TYPE.OUTFIT] |= {(vehicleIntCD, season) for season in SeasonType.RANGE}
            return
        else:
            for season in outfitsData:
                invalidate[GUI_ITEM_TYPE.OUTFIT].add((vehicleIntCD, season))
                if outfitsData[season] is None:
                    outfitCD, flags = None, StyleFlags.ACTIVE
                else:
                    outfitCD, flags = outfitsData[season]
                if flags != StyleFlags.ACTIVE:
                    continue
                newOutfit = Outfit(outfitCD)
                if newOutfit.style is not None:
                    prevOutfit = vehicle.getOutfit(SeasonType.SUMMER) or Outfit()
                    if prevOutfit.id != newOutfit.id:
                        self.__inventory.updateC11nItemAppliedCount(newOutfit.style.compactDescr, vehicleIntCD, 1)
                        invalidate[GUI_ITEM_TYPE.CUSTOMIZATION].add(newOutfit.style.compactDescr)
                    invalidItems = self.__removeVehicleOutfits(vehicle)
                    invalidate[GUI_ITEM_TYPE.CUSTOMIZATION] |= invalidItems
                    break
                prevOutfit = vehicle.getCustomOutfit(season) or Outfit()
                prevItemsCounter = prevOutfit.itemsCounter
                newItemsCounter = newOutfit.itemsCounter
                newItemsCounter.subtract(prevItemsCounter)
                for itemCD, count in newItemsCounter.iteritems():
                    self.__inventory.updateC11nItemAppliedCount(itemCD, vehicleIntCD, count)
                    invalidate[GUI_ITEM_TYPE.CUSTOMIZATION].add(itemCD)

            return

    def __removeVehicleOutfits(self, vehicle):
        invalidItems = set()
        for season in SeasonType.RANGE:
            outfit = vehicle.getCustomOutfit(season) or Outfit()
            if not outfit.isActive():
                continue
            if outfit.style is not None:
                styleIntCD = outfit.style.compactDesc
                self.__inventory.updateC11nItemAppliedCount(styleIntCD, vehicle.intCD, -1)
                invalidItems.add(styleIntCD)
                continue
            for itemCD, count in outfit.itemsCounter.iteritems():
                self.__inventory.updateC11nItemAppliedCount(itemCD, vehicle.intCD, -count)
                invalidItems.add(itemCD)

        return invalidItems

    def __deleteItemFromCache(self, cache, uid, itemTypeID):
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            item = cache[uid]
            if item.isCustomStateSet():
                self.__vehCustomStateCache[uid] = item.getCustomState()
            elif uid in self.__vehCustomStateCache:
                del self.__vehCustomStateCache[uid]
        del cache[uid]

    def __getAccountDossierDescr(self):
        return dossiers2.getAccountDossierDescr(self.__stats.accountDossier)

    def __getTankmanDossierDescr(self, tmanInvID):
        tmanData = self.__inventory.getTankmanData(tmanInvID)
        return dossiers2.getTankmanDossierDescr(tmanData.descriptor.dossierCompactDescr) if tmanData is not None else dossiers2.getTankmanDossierDescr()

    def __getVehicleDossierDescr(self, vehTypeCompDescr):
        return dossiers2.getVehicleDossierDescr(self.__dossiers.getVehicleDossier(vehTypeCompDescr))

    def __makeItem(self, itemTypeIdx, uid, *args, **kwargs):
        container = self.__itemsCache[itemTypeIdx]
        if uid in container:
            return container[uid]
        else:
            if not self.isSynced():
                self.__logBrokenSync(itemTypeIdx)
            item = self.itemsFactory.createGuiItem(itemTypeIdx, *args, **kwargs)
            if item is not None:
                container[uid] = item
                self.__restoreItemCustomState(itemTypeIdx, uid, item)
            return item

    def __restoreItemCustomState(self, itemTypeIdx, uid, item):
        if itemTypeIdx == GUI_ITEM_TYPE.VEHICLE:
            prevItem = self.__vehCustomStateCache.get(uid, None)
            if prevItem:
                item.setCustomState(prevItem)
                del self.__vehCustomStateCache[uid]
        return

    def __makeVehicle(self, typeCompDescr, vehInvData=None):
        vehInvData = vehInvData or self.__inventory.getItemData(typeCompDescr)
        return self.__makeItem(GUI_ITEM_TYPE.VEHICLE, typeCompDescr, strCompactDescr=vehInvData.compDescr, inventoryID=vehInvData.invID, proxy=self) if vehInvData is not None else self.__makeItem(GUI_ITEM_TYPE.VEHICLE, typeCompDescr, typeCompDescr=typeCompDescr, proxy=self)

    def __makeTankman(self, tmanInvID, tmanInvData=None):
        tmanInvData = tmanInvData or self.__inventory.getTankmanData(tmanInvID)
        if tmanInvData is not None:
            vehicle = None
            if tmanInvData.vehicle > 0:
                vehicle = self.getVehicle(tmanInvData.vehicle)
            return self.__makeItem(GUI_ITEM_TYPE.TANKMAN, tmanInvID, strCompactDescr=tmanInvData.compDescr, inventoryID=tmanInvID, vehicle=vehicle, proxy=self)
        else:
            return

    def __makeDismissedTankman(self, tmanID, tmanData):
        strCD, dismissedAt = tmanData
        return self.__makeItem(GUI_ITEM_TYPE.TANKMAN, tmanID, strCompactDescr=strCD, inventoryID=tmanID, proxy=self, dismissedAt=dismissedAt)

    def __makeSimpleItem(self, typeCompDescr):
        return self.__makeItem(getTypeOfCompactDescr(typeCompDescr), typeCompDescr, intCompactDescr=typeCompDescr, proxy=self)

    def __getTankmenIDsForVehicle(self, vehData):
        vehTmanIDs = set()
        for tmanInvID in vehData.crew:
            if tmanInvID is not None:
                vehTmanIDs.add(tmanInvID)

        return vehTmanIDs

    def __getTankmenIDsForTankman(self, tmanData):
        vehData = self.__inventory.getVehicleData(tmanData.vehicle)
        return self.__getTankmenIDsForVehicle(vehData) if vehData is not None else set()

    def __getVehicleCDForTankman(self, tmanData):
        vehData = self.__inventory.getVehicleData(tmanData.vehicle)
        return {vehData.descriptor.type.compactDescr} if vehData is not None else set()

    def __logBrokenSync(self, itemTypeID):
        if itemTypeID in self.__brokenSyncAlreadyLoggedTypes:
            return
        self.__brokenSyncAlreadyLoggedTypes.add(itemTypeID)
        requesters = (self.__stats,
         self.__inventory,
         self.__recycleBin,
         self.__shop,
         self.__dossiers,
         self.__goodies,
         self.__vehicleRotation,
         self.ranked)
        unsyncedList = [ r.__class__.__name__ for r in [ r for r in requesters if not r.isSynced() ] ]
        LOG_ERROR('Trying to create fitting item when requesters are not fully synced:', unsyncedList, stack=True)
