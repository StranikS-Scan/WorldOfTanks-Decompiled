# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/utils/requesters.py
from gui.shared.money import Money, MoneySet

class IRequester(object):
    """Interface of requester that fetches required data from cache."""

    def request(self, callback):
        raise NotImplementedError

    def isSynced(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class IInventoryRequester(IRequester):
    """Class provides access to inventory data."""

    def invalidateItem(self, itemTypeID, invIdx):
        """Invalidates data of item by specified item type ID and inventory ID."""
        raise NotImplementedError

    def getItemsData(self, itemTypeID):
        """Gets raw data of items by specified item type ID."""
        raise NotImplementedError

    def getItemData(self, typeCompDescr):
        """Gets raw data of items by specified int-type compact descriptor."""
        raise NotImplementedError

    def getTankmanData(self, tmanInvID):
        """Gets raw data of tankman by specified inventory ID."""
        raise NotImplementedError

    def getVehicleData(self, vehInvID):
        """Gets raw data of vehicle by specified inventory ID."""
        raise NotImplementedError

    def getPreviousItem(self, itemTypeID, invDataIdx):
        """Gets data of item that was removed from cache when method 'invalidateItem' is invoked."""
        raise NotImplementedError

    def getItems(self, itemTypeIdx, dataIdx=None):
        """Returns inventory items data by given item type. If data index is
        not specified - returns dictionary of items data, otherwise -
        specific item data.
        
        @param itemTypeIdx: item type index from common.items.ITEM_TYPE_NAMES
        @param dataIdx:optional  item data index in cache. Used to get data only for
                                specific item. This index is different for each item type:
                                        - for vehicles and tankmen: inventory id
                                        - for the rest types: type compact descriptor (int)
        @return: dict of items data or specific item data
        """
        raise NotImplementedError

    def isInInventory(self, intCompactDescr):
        """ Check whether item is in inventory or not.
        
        @param intCompactDescr: item int compact descriptor to check
        @return: bool flag of item inventory existence
        """
        raise NotImplementedError

    def isItemInInventory(self, itemTypeID, invDataIdx):
        raise NotImplementedError

    def getIgrCustomizationsLayout(self):
        raise NotImplementedError

    def getFreeSlots(self, vehiclesSlots):
        raise NotImplementedError


class IStatsRequester(IRequester):
    """Class provides access to player's statistics (money, xp, etc.)."""

    @property
    def mayConsumeWalletResources(self):
        """Gets wallet resources available flag."""
        raise NotImplementedError

    @property
    def credits(self):
        """Gets account credits balance as positive value."""
        raise NotImplementedError

    @property
    def gold(self):
        """Gets account gold balance as positive value."""
        raise NotImplementedError

    @property
    def crystal(self):
        """Gets account crystal balance as positive value."""
        raise NotImplementedError

    @property
    def money(self):
        """Gets account money (credits, gold) as positive value."""
        raise NotImplementedError

    @property
    def actualCredits(self):
        """Gets account credits actual balance."""
        raise NotImplementedError

    @property
    def actualGold(self):
        """Gets account gold actual balance."""
        raise NotImplementedError

    @property
    def actualCrystal(self):
        """Gets account crystal actual balance."""
        raise NotImplementedError

    @property
    def actualMoney(self):
        """Gets account money (credits, gold) in actual state."""
        raise NotImplementedError

    @property
    def freeXP(self):
        """Gets account free experience value greater then zero."""
        raise NotImplementedError

    @property
    def actualFreeXP(self):
        """Gets account free experience value."""
        raise NotImplementedError

    @property
    def vehiclesXPs(self):
        """Gets vehicles experience. Dict format:
            { vehicle type int compact descriptor: xp value, }
        """
        raise NotImplementedError

    @property
    def multipliedVehicles(self):
        """Gets current day already multiplied vehicles list. Format:
            {vehicle type int compact descriptor, ...}
        """
        raise NotImplementedError

    @property
    def eliteVehicles(self):
        """Gets elite vehicles list. Format:
                    {vehicle type int compact descriptor, ...}
        """
        raise NotImplementedError

    @property
    def vehicleTypeLocks(self):
        """Gets vehicles locks. Now available only clan locks [1]. Format:
            { vehicle type int compact descriptor: { 1: time to unlock in seconds }, }
        """
        raise NotImplementedError

    @property
    def globalVehicleLocks(self):
        """Gets vehicles locks. Now available only clan locks [1]. Format:
            { 1: time to unlock in seconds, }
        """
        raise NotImplementedError

    @property
    def attributes(self):
        """Gets account attributes. Bit combination of constants.ACCOUNT_ATTR.*."""
        raise NotImplementedError

    @property
    def premiumExpiryTime(self):
        """Gets account premiumExpiryTime. Timestamp."""
        raise NotImplementedError

    @property
    def isPremium(self):
        """Is account premium."""
        raise NotImplementedError

    @property
    def isTeamKiller(self):
        """Is player team killer."""
        raise NotImplementedError

    @property
    def restrictions(self):
        """Gets account restrictions. Set of values constants.RESTRICTION_TYPE.*."""
        raise NotImplementedError

    @property
    def unlocks(self):
        """Gets unlocked items. Format: {int compact descriptor, ...}."""
        raise NotImplementedError

    @property
    def initialUnlocks(self):
        """Gets initial unlocked items. Format: {int compact descriptor, ...}."""
        raise NotImplementedError

    @property
    def vehicleSlots(self):
        """Gets number of vehicle slots that was bought."""
        raise NotImplementedError

    @property
    def dailyPlayHours(self):
        """Played hours per each day in current month.
        List of hours values. Current day played hours value is cache['dailyPlayHours'][0].
        """
        raise NotImplementedError

    @property
    def todayPlayHours(self):
        """Gets number of hours that player sends in the game today."""
        raise NotImplementedError

    @property
    def playLimits(self):
        """Gets playing time limits, (hours per day, hours per week)"""
        raise NotImplementedError

    def getDailyTimeLimits(self):
        """Gets daily time limits."""
        raise NotImplementedError

    def getWeeklyTimeLimits(self):
        """Gets weekly time limits."""
        raise NotImplementedError

    def getPlayTimeLimits(self):
        """Gets daily and weekly time limits."""
        raise NotImplementedError

    @property
    def tankmenBerthsCount(self):
        """Gets ankmen berths count in the barracks."""
        raise NotImplementedError

    @property
    def vehicleSellsLeft(self):
        """Gets value of vehicle sells left this day."""
        raise NotImplementedError

    @property
    def freeTankmenLeft(self):
        """Gets value of free tankmen recruit operations of this day."""
        raise NotImplementedError

    @property
    def accountDossier(self):
        """Gets account dossier compact descriptor."""
        raise NotImplementedError

    @property
    def denunciationsLeft(self):
        """Gets value of denunciations left this day."""
        raise NotImplementedError

    @property
    def freeVehiclesLeft(self):
        """Gets number of free vehicles that player could buy during the current game day."""
        raise NotImplementedError

    @property
    def clanDBID(self):
        """Gets clan database id."""
        raise NotImplementedError

    @property
    def clanInfo(self):
        """Gets clan information."""
        raise NotImplementedError

    @property
    def globalRating(self):
        """Gets player's global rating."""
        raise NotImplementedError

    @property
    def refSystem(self):
        """Gets information about referrals, referrers."""
        raise NotImplementedError

    @property
    def SPA(self):
        """Gets information about SPA. It is not used."""
        raise NotImplementedError

    @property
    def isGoldFishBonusApplied(self):
        """Is "gold fish" bonus applied."""
        raise NotImplementedError

    @property
    def tutorialsCompleted(self):
        """Gets bitmask containing all received bonuses (1 << bonusID)."""
        raise NotImplementedError

    @property
    def oldVehInvIDs(self):
        """Gets unit previously selected vehicles."""
        raise NotImplementedError


class IDossierRequester(IRequester):
    """This requester store only vehicles dossiers (server architecture).
    Account dossier is stored in IStatsRequester and
    tankmen dossiers - in its own compact descriptor (in inventory).
    """

    def getVehicleDossier(self, vehTypeCompDescr):
        """Gets string containing vehicle dossier descriptor."""
        raise NotImplementedError

    def getVehDossiersIterator(self):
        """ Returns iterator through all player's vehicle dossiers
        :return: each call returns pair (veh_int_cd, dossier_str)
        """
        raise NotImplementedError

    def getUserDossierRequester(self, databaseID):
        """Gets requester to fetch user dossier by account's database ID."""
        raise NotImplementedError

    def closeUserDossier(self, databaseID):
        """Remove user dossier if it has."""
        raise NotImplementedError

    def onCenterIsLongDisconnected(self, isLongDisconnected):
        raise NotImplementedError


class IShopCommonStats(object):
    """There is common data in the shop. This data is used in the current shop and
    default shop to calculate discounts."""

    def getPrices(self):
        """Gets dictionary containing items prices."""
        raise NotImplementedError

    def getBoosterPrices(self):
        """Gets dictionary containing boosters prices that are represented by tuple."""
        raise NotImplementedError

    def getHiddens(self):
        """Gets int-type compact descriptors of items that are hidden in the shop."""
        raise NotImplementedError

    def getHiddenBoosters(self):
        """Gets IDs of booster than can be bought."""
        raise NotImplementedError

    def getNotToBuyVehicles(self):
        """Gets int-type compact descriptors of items that are disable for buy in the shop."""
        raise NotImplementedError

    def getVehicleRentPrices(self):
        """Gets dictionary containing rent prices where each key is int-type compact descriptor."""
        raise NotImplementedError

    def getVehiclesForGold(self):
        """Gets int-type compact descriptors of items that can be sold for gold."""
        raise NotImplementedError

    def getVehiclesSellPriceFactors(self):
        """Gets dictionary containing sell prices where each key is int-type compact descriptor."""
        raise NotImplementedError

    def getItemPrice(self, intCD):
        """Gets item price to buy."""
        raise NotImplementedError

    def getBoosterPricesTuple(self, boosterID):
        """Gets all available prices for buying booster with the given id."""
        raise NotImplementedError

    def getItem(self, intCD):
        """Gets information about shop item as
        tuple(price of item, item is hidden)."""
        raise NotImplementedError

    def getAchievementReward(self, achievement, arenaType=0):
        """Get information about achievement rewards"""
        raise NotImplementedError

    @property
    def revision(self):
        """Gets shop revision value."""
        raise NotImplementedError

    @property
    def paidRemovalCost(self):
        """Gets cost of dismantling of non-removable optional devices for gold."""
        raise NotImplementedError

    @property
    def paidDeluxeRemovalCost(self):
        """
        Gets cost of dismantling of non-removable Deluxe optional devices for crystals by default
        It can be any currency.
        """
        raise NotImplementedError

    @property
    def exchangeRate(self):
        """Gets rate of gold for credits exchanging."""
        raise NotImplementedError

    @property
    def crystalExchangeRate(self):
        """
        @return: rate of crystals for credits exchanging
        """
        raise NotImplementedError

    @property
    def exchangeRateForShellsAndEqs(self):
        """Gets rate of gold for credits exchanging for F2W premium shells and eqs action."""
        raise NotImplementedError

    @property
    def sellPriceModif(self):
        """Gets sell price modifier."""
        raise NotImplementedError

    @property
    def vehiclesRestoreConfig(self):
        """Gets configuration to restore vehicles."""
        raise NotImplementedError

    @property
    def tankmenRestoreConfig(self):
        """Gets configuration to restore tankmen."""
        raise NotImplementedError

    def sellPriceModifiers(self, compDescr):
        """Gets full information about price modifiers."""
        raise NotImplementedError

    @property
    def slotsPrices(self):
        """Gets number of initial slots and price to buy slot."""
        raise NotImplementedError

    def getVehicleSlotsPrice(self, currentSlotsCount):
        """Gets new price to buy slot by specified number of slots that are bought."""
        raise NotImplementedError

    @property
    def dropSkillsCost(self):
        """Gets drop tankman skill cost."""
        raise NotImplementedError

    @property
    def dailyXPFactor(self):
        """Gets daily experience multiplier."""
        raise NotImplementedError

    @property
    def winXPFactorMode(self):
        """Gets mode for applying daily XP factor."""
        raise NotImplementedError

    @property
    def berthsPrices(self):
        """Gets number of initial berths, number of berths in pack, and price to buy berths pack."""
        raise NotImplementedError

    def getTankmanBerthPrice(self, berthsCount):
        """Gets new price to buy berths pack and number of berths in pack
        by specified number of berths that are bought."""
        raise NotImplementedError

    @property
    def isEnabledBuyingGoldShellsForCredits(self):
        """Is premium shells for credits action enabled."""
        raise NotImplementedError

    @property
    def isEnabledBuyingGoldEqsForCredits(self):
        """Is premium equipments for credits action enabled."""
        raise NotImplementedError

    @property
    def tankmanCost(self):
        """
        @return: tankman studying cost
                        tmanCost -  ( tmanCostType, ), where
                        tmanCostType = {
                                        'roleLevel' : minimal role level after operation,
                                        'credits' : cost in credits,
                                        'gold' : cost in gold,
                                        'baseRoleLoss' : float in [0, 1], fraction of role to drop,
                                        'classChangeRoleLoss' : float in [0, 1], fraction of role to drop
                                                additionally if
                                                classes of self.vehicleTypeID and newVehicleTypeID are different,
                                        'isPremium' : tankman becomes premium,
                                        }.
                                List is sorted by role level.
        """
        raise NotImplementedError

    @property
    def changeRoleCost(self):
        """Gets tankman change role cost in gold."""
        raise NotImplementedError

    @property
    def freeXPConversion(self):
        """Gets free experience to vehicle xp exchange rate and cost (discrecity, cost)."""
        raise NotImplementedError

    @property
    def passportChangeCost(self):
        """Gets tankman passport replace cost in gold."""
        raise NotImplementedError

    @property
    def passportFemaleChangeCost(self):
        """Gets tankman passport replace cost in gold for female."""
        raise NotImplementedError

    @property
    def freeXPToTManXPRate(self):
        """Gets free experience to tankman experience exchange rate."""
        raise NotImplementedError

    def getItemsData(self):
        """Gets raw data of items."""
        raise NotImplementedError

    def getGoodiesData(self):
        """Gets raw data of goodies."""
        raise NotImplementedError

    def getVehCamouflagePriceFactor(self, typeCompDescr):
        """Gets price factor to buy vehicle's camouflage
        by vehicle int-type compact descriptor."""
        raise NotImplementedError

    def getEmblemsGroupPriceFactors(self):
        """Gets price factor to buy vehicle's emblems."""
        raise NotImplementedError

    def getEmblemsGroupHiddens(self):
        """Gets emblems that are not shown in the shop."""
        raise NotImplementedError

    def getInscriptionsGroupPriceFactors(self, nationID):
        """Gets price factor to buy vehicle's inscriptions."""
        raise NotImplementedError

    def getInscriptionsGroupHiddens(self, nationID):
        """Gets inscriptions that are not shown in the shop."""
        raise NotImplementedError

    def getCamouflagesPriceFactors(self, nationID):
        """Gets price factors to buy vehicle's camouflages by nation ID."""
        raise NotImplementedError

    def getCamouflagesHiddens(self, nationID):
        """Gets camouflages that are not shown in the shop."""
        raise NotImplementedError

    @property
    def premiumCost(self):
        """Gets cost to buy premium and durations."""
        raise NotImplementedError

    @property
    def goodies(self):
        """Gets all information about available goodies."""
        raise NotImplementedError

    def getGoodieByID(self, discountID):
        """Gets goodie data model by specified ID."""
        raise NotImplementedError

    def getGoodiesByVariety(self, variety):
        """Gets filtered information about goodies by criteria."""
        raise NotImplementedError

    @property
    def boosters(self):
        """Gets information about boosters."""
        raise NotImplementedError

    @property
    def discounts(self):
        """Gets information about discounts."""
        raise NotImplementedError

    def getPremiumPacketCost(self, days):
        """Gets cost to buy premuim by specified days."""
        raise NotImplementedError

    @property
    def camouflageCost(self):
        """Gets information about camouflage costs by period (duration, price, is gold price)."""
        raise NotImplementedError

    def getCamouflageCost(self, days=0):
        """Gets the base cost of camouflage on the indicated days (infinity by default)."""
        raise NotImplementedError

    @property
    def playerInscriptionCost(self):
        """Gets information about inscription costs by period(duration, price, is gold price)."""
        raise NotImplementedError

    def getInscriptionCost(self, days=0):
        """Gets the base cost of inscription on the indicated days (infinity by default)."""
        raise NotImplementedError

    @property
    def playerEmblemCost(self):
        """Gets information about emblem costs by period(duration, price, is gold price)."""
        raise NotImplementedError

    def getEmblemCost(self, days=0):
        """Gets the base cost of emblem on the indicated days (infinity by default)."""
        raise NotImplementedError

    @property
    def refSystem(self):
        """Gets settings of referral system."""
        raise NotImplementedError

    @property
    def tradeIn(self):
        """Gets settings of trade in."""
        raise NotImplementedError


class IShopRequester(IShopCommonStats, IRequester):
    """Class provides access to actual shop data with discount."""

    def getPremiumCostWithDiscount(self, premiumPacketDiscounts=None):
        """If premiumPacketDiscounts is not defined, return modified premiumCost,
        calculated with actual personal premium packet discounts."""
        raise NotImplementedError

    def getTankmanCostWithDefaults(self):
        """Gets tankman studying cost with discount.
            tmanCost, action -  ( tmanCostType, ), ( actionData, ) where
            tmanCostType = {
                            'roleLevel' : minimal role level after operation,
                            'credits' : cost in credits,
                            'defCredits' : cost in credits,
                            'gold' : default cost in gold,
                            'defGold' : default cost in gold,
                            'baseRoleLoss' : float in [0, 1], fraction of role to drop,
                            'classChangeRoleLoss' : float in [0, 1], fraction of role to drop
                            additionally if
                                    classes of self.vehicleTypeID and newVehicleTypeID are different,
                            'isPremium' : tankman becomes premium,
                            }.
                    List is sorted by role level.
            actionData = Action data for each level of retraining
        """
        raise NotImplementedError

    @property
    def tankmanCostWithGoodyDiscount(self):
        raise NotImplementedError

    @property
    def freeXPConversionLimit(self):
        """Gets xp that can be convert to free XP for free."""
        raise NotImplementedError

    @property
    def freeXPConversionWithDiscount(self):
        """Gets free experience to vehicle xp exchange rate and cost (discrecity, cost)
        with discounts."""
        raise NotImplementedError

    @property
    def isXPConversionActionActive(self):
        """freeXPConversion is not price, but count of XP for one gold
        so during action we have higher rate, not lower price"""
        raise NotImplementedError

    @property
    def isCreditsConversionActionActive(self):
        """
        @return: if rate of gold for credits exchanging not standard return True
        """
        raise NotImplementedError

    @property
    def personalPremiumPacketsDiscounts(self):
        """Return personal premium packets discounts in account."""
        raise NotImplementedError

    @property
    def personalSlotDiscounts(self):
        """Return personal slot discounts in account."""
        raise NotImplementedError

    @property
    def personalTankmanDiscounts(self):
        """Return personal tankman discounts in account."""
        raise NotImplementedError

    @property
    def personalXPExchangeDiscounts(self):
        """Return personal xp exchange discounts in account."""
        raise NotImplementedError

    @property
    def personalVehicleDiscounts(self):
        """Return personal vehicle discounts in account."""
        raise NotImplementedError

    def getVehicleDiscountDescriptions(self):
        """Return vehicle discounts descriptions."""
        raise NotImplementedError

    def getPersonalVehicleDiscountPrice(self, typeCompDescr):
        """Return price with max discount for selected vehicle."""
        raise NotImplementedError

    def bestGoody(self, goodies):
        """"Gets goody with biggest discount from given."""
        raise NotImplementedError


class IGoodiesRequester(IRequester):
    """Class provides access to goodies that player used."""

    @property
    def goodies(self):
        """Gets short information about used goodies."""
        raise NotImplementedError


class IRecycleBinRequester(IRequester):
    """Class provides access to tankmen, vehicles that player can restore."""

    @property
    def recycleBin(self):
        """Gets raw data of recycle bin."""
        raise NotImplementedError

    @property
    def vehiclesBuffer(self):
        raise NotImplementedError

    def getVehicleRestoreInfo(self, intCD, restoreDuration, restoreCooldown):
        raise NotImplementedError

    def getTankmen(self, maxDuration):
        raise NotImplementedError

    def getTankman(self, invID, maxDuration):
        raise NotImplementedError


class IVehicleRotationRequester(IRequester):

    def getBattlesCount(self, groupNum):
        raise NotImplementedError

    def isGroupLocked(self, groupNum):
        raise NotImplementedError

    def getGroupNum(self, vehIntCD):
        raise NotImplementedError

    def isInfinite(self, groupNum):
        raise NotImplementedError


class IRankedRequester(IRequester):
    """Class provides tor ranked dynamic data"""

    @property
    def accRank(self):
        raise NotImplementedError

    @property
    def vehRanks(self):
        raise NotImplementedError

    @property
    def clientRank(self):
        raise NotImplementedError

    @property
    def clientVehRanks(self):
        raise NotImplementedError

    @property
    def season(self):
        raise NotImplementedError

    @property
    def maxRank(self):
        raise NotImplementedError

    @property
    def maxVehRanks(self):
        raise NotImplementedError

    @property
    def ladderPoints(self):
        raise NotImplementedError

    @property
    def maxRankWithAwardReceived(self):
        raise NotImplementedError

    @property
    def seasonLadderPts(self):
        raise NotImplementedError

    @property
    def stepsCount(self):
        raise NotImplementedError

    @property
    def seasonStepsCount(self):
        raise NotImplementedError


class IBadgesRequester(IRequester):
    """Class provides tor badges data"""

    @property
    def available(self):
        raise NotImplementedError

    @property
    def selected(self):
        raise NotImplementedError
